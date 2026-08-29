from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from aetext.cpp.literals import decode_string_literal


@given(st.text(alphabet=st.characters(exclude_categories=("Cs",)), max_size=40))
def test_universal_escape_decoder_round_trips_unicode(value: str) -> None:
    literal = '"' + "".join(f"\\U{ord(character):08X}" for character in value) + '"'

    assert decode_string_literal(literal) == value
