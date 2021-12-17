from datetime import datetime
from functools import reduce

import pytest


class Encoder:
    CHARSET_16 = '0123456789ABCDEF'
    CHARSET_32 = '0123456789ABCDEFGHIJKLMNOPQRSTUV'
    CHARSET_44 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`{}~'
    CHARSET_64 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ~`!@#$%^&*()_-+={[]}:;<,>.?|'
    DEFAULT_CHARSET = CHARSET_16

    def __init__(self, charset: str = DEFAULT_CHARSET, case=True):
        self.case = case
        if not self.case:
            charset = charset.lower()
        assert len(set(charset)) == len(charset), 'Charset must contains only unique characters'

        self.charset = charset
        self.base = len(charset)

    def encode(self, number: int) -> str:

        result = ''

        if number == 0:
            return self.charset[0]
        while number > 0:
            tmp = number % self.base
            result += self.charset[tmp]
            number //= self.base

        return result[::-1]

    def decode(self, encoded: str) -> int:
        if not self.case:
            encoded = encoded.lower()
        assert len(set(self.charset + encoded)) == len(self.charset), \
            f"These characters are unknow in the instance charset: " \
            f"`{','.join(sorted(set(encoded) - set(self.charset)))}`"

        return reduce(lambda count, c: count * self.base + self.charset.index(c), encoded, 0)


def encode_decode(encoder: Encoder, number: int, target: str):
    encoded = encoder.encode(number)
    assert encoded == target
    assert encoder.decode(encoded) == number


def test_encode():
    encoder = Encoder()
    assert encoder.base == 16

    encode_decode(encoder, 0, '0')
    encode_decode(encoder, 65535, 'FFFF')
    encode_decode(encoder, 65534, 'FFFE')
    encode_decode(encoder, 27492339183, '666ABCDEF')

    encoder = Encoder(charset='01')
    assert encoder.base == 2

    encode_decode(encoder, 0, '0')
    encode_decode(encoder, 65535, '1111111111111111')
    encode_decode(encoder, 42, '101010')

    encoder = Encoder(charset='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ~`!@#$%^&*()_-+={[]}:;<,>.?/')
    assert encoder.base == 64

    encode_decode(encoder, 0, '0')
    encode_decode(encoder, 63, '/')
    encode_decode(encoder, 64, '10')
    encode_decode(encoder, 4096, '100')
    encode_decode(encoder, 35, 'Z')

    encoder = Encoder(
        charset='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ~`!@#$%^&*()_-+={[]}:;<,>.?/',
        case=False)
    encode_decode(encoder, 35, 'z')

    encoder = Encoder(charset='XY')
    assert encoder.base == 2

    encode_decode(encoder, 0, 'X')

    encoder = Encoder(charset='XY', case=False)
    encode_decode(encoder, 0, 'x')
    with pytest.raises(AssertionError):
        Encoder(charset='aA', case=False)  # Two times the same char


if __name__ == '__main__':
    t1 = datetime.now()

    test_encode()

    print(f"{(datetime.now() - t1).microseconds / 1000} milliseconds")
