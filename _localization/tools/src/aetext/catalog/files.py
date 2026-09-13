"""Stage catalog saves together, serialize writers, and roll back failed replacements."""

from __future__ import annotations

import msvcrt
import os
import tempfile
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

_locks: dict[Path, threading.Lock] = {}


def content_hash(data: bytes | None) -> str | None:
    return None if data is None else sha256(data).hexdigest().upper()


@dataclass(frozen=True)
class FileWrite:
    path: Path
    expected_hash: str | None
    content: bytes
    conflict_error: type[Exception]


@contextmanager
def _save_lock(catalog_path: Path, conflict_error: type[Exception]):
    lock_path = catalog_path.with_name(catalog_path.name + ".save-lock")
    thread_lock = _locks.setdefault(lock_path, threading.Lock())
    if not thread_lock.acquire(blocking=False):
        raise conflict_error(f"another save is in progress: {catalog_path}")
    try:
        with lock_path.open("a+b") as stream:
            if stream.tell() == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as error:
                raise conflict_error(f"another save is in progress: {catalog_path}") from error
            try:
                yield
            finally:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
    finally:
        thread_lock.release()


def _stage(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".tmp.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def commit_files(catalog_path: Path, writes: list[FileWrite]) -> None:
    # Review-state precedes catalog data: an interrupted pair cannot certify new text as old text.
    with _save_lock(catalog_path, writes[-1].conflict_error):
        originals: dict[Path, bytes | None] = {}
        staged: dict[Path, Path] = {}
        replaced: list[FileWrite] = []
        try:
            for write in writes:
                current = write.path.read_bytes() if write.path.exists() else None
                if content_hash(current) != write.expected_hash:
                    raise write.conflict_error(f"file changed after review opened: {write.path}")
                originals[write.path] = current
                if current != write.content:
                    staged[write.path] = _stage(write.path, write.content)
            for write in writes:
                current = write.path.read_bytes() if write.path.exists() else None
                if content_hash(current) != write.expected_hash:
                    raise write.conflict_error(f"file changed while preparing save: {write.path}")
            for write in writes:
                if write.path in staged:
                    os.replace(staged[write.path], write.path)
                    replaced.append(write)
        except BaseException as error:
            unrestored: list[str] = []
            for write in reversed(replaced):
                try:
                    if write.path.read_bytes() != write.content:
                        raise OSError("file changed again during rollback")
                    original = originals[write.path]
                    if original is None:
                        write.path.unlink()
                    else:
                        staged[write.path] = _stage(write.path, original)
                        os.replace(staged[write.path], write.path)
                except OSError:
                    unrestored.append(str(write.path))
            if unrestored:
                raise OSError(
                    "Save failed and these files could not be restored; reload before saving: "
                    + ", ".join(unrestored)
                ) from error
            raise
        finally:
            for temporary in staged.values():
                temporary.unlink(missing_ok=True)
