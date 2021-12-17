from datetime import datetime
from functools import reduce


class Encoder:
    DEFAULT_CHARSET = '0123456789ABCDEF'

    def __init__(self, charset: str = DEFAULT_CHARSET, case=True):
        if len(set(charset)) != len(charset):
            raise ValueError('Charset must contains only uniques characters')
        self.case = case
        if not self.case:
            charset = charset.lower()
        self.charset = charset
        self.base = len(charset)

    def encode(self, n: int) -> str:

        result = ''

        if n == 0:
            return self.charset[0]
        while n > 0:
            tmp = n % self.base
            result += self.charset[tmp]
            n //= self.base

        return result[::-1]

    def decode(self, s: str) -> int:
        if not self.case:
            s = s.lower()
        assert len(set(self.charset + s)) == len(self.charset), \
            f"These characters are unknow in the instance charset: `{','.join(sorted(set(s) - set(self.charset)))}`"

        return reduce(lambda count, c: count * self.base + self.charset.index(c), s, 0)


def encode_decode(e: Encoder, n: int, s: str):
    encoded = e.encode(n)
    assert encoded == s
    assert e.decode(encoded) == n


def test_encode():
    e = Encoder()
    assert e.base == 16

    encode_decode(e, 0, '0')
    encode_decode(e, 65535, 'FFFF')
    encode_decode(e, 65534, 'FFFE')
    encode_decode(e, 27492339183, '666ABCDEF')

    e = Encoder(charset='01')
    assert e.base == 2

    encode_decode(e, 0, '0')
    encode_decode(e, 65535, '1111111111111111')
    encode_decode(e, 42, '101010')

    e = Encoder(charset='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ~`!@#$%^&*()_-+={[]}:;<,>.?/')
    assert e.base == 64

    encode_decode(e, 0, '0')
    encode_decode(e, 63, '/')
    encode_decode(e, 64, '10')
    encode_decode(e, 4096, '100')
    encode_decode(e, 35, 'Z')

    e = Encoder(charset='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ~`!@#$%^&*()_-+={[]}:;<,>.?/', case=False)
    encode_decode(e, 35, 'z')

    e = Encoder(charset='XY')
    assert e.base == 2

    encode_decode(e, 0, 'X')

    e = Encoder(charset='XY', case=False)
    encode_decode(e, 0, 'x')


if __name__ == '__main__':
    t1 = datetime.now()

    test_encode()

    print(f"{(datetime.now() - t1).microseconds / 1000} milliseconds")
