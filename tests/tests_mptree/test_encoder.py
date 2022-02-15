import pytest

from apps.commons.utils.mptree.encoder import Encoder


@pytest.mark.parametrize('encoder, number, expected', [
    # Default: hex
    (Encoder(), 0, '0'),
    (Encoder(), 0xFF, 'FF'),
    # Binary
    (Encoder(charset="01"), 0, '0'),
    (Encoder(charset="01"), 2, '10'),
    (Encoder(charset="01"), 42, '101010'),
    # Case sensitivity
    (Encoder(charset="ABCD", case=False), 0, 'a'),
    (Encoder(charset="AaBb"), 0, 'A'),
    (Encoder(charset='0123456789AbCDef', case=False), 0xDEADBEEF, 'deadbeef'),
    (Encoder(charset='0123456789AbCDef'), 0xDEADBEEF, 'DeADbeef'),
])
def test_encoding(encoder: Encoder, number: int, expected: str):
    encoded = encoder.encode(number)
    assert encoded == expected
    assert encoder.decode(encoded) == number


@pytest.mark.parametrize('charset, case', [
    ('aA', False),
    ('AA', True),
    ('AA', False),
])
def test_failures(charset: str, case: bool):
    with pytest.raises(AssertionError):
        Encoder(charset=charset, case=case)  # Two times the same char
    with pytest.raises(AssertionError):
        Encoder(charset=charset, case=case)  # Two times the same char


def test_negative():
    with pytest.raises(AssertionError):
        Encoder().encode(-1)


def test_char_not_in_charset():
    with pytest.raises(AssertionError):
        Encoder(charset='ABCD').decode('AABx')
