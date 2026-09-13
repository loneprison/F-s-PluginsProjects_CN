"""Family-owned review workflow configuration persistence."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .models import WorkflowDefinition


class WorkflowService:
    def __init__(self, repository_root: str | Path, family_id: str = "fs") -> None:
        self.repository_root = Path(repository_root).resolve()
        self.path = (
            self.repository_root / "_localization" / "families" / family_id / "review-workflow.json"
        ).resolve()

    def load(self) -> WorkflowDefinition:
        document = json.loads(self.path.read_text(encoding="utf-8-sig"))
        return WorkflowDefinition.model_validate(document, strict=True)

    def save(self, definition: WorkflowDefinition | dict[str, object]) -> WorkflowDefinition:
        validated = (
            definition
            if isinstance(definition, WorkflowDefinition)
            else WorkflowDefinition.model_validate(definition, strict=True)
        )
        output = (
            json.dumps(validated.model_dump(by_alias=True), ensure_ascii=False, indent=2) + "\n"
        )
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=self.path.name + ".tmp.",
            dir=self.path.parent,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(output)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
        return validated
