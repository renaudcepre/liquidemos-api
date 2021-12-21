"""Encode and decode values for a given charset"""

from functools import reduce


class Encoder:
    """Encode and decode values for a given charset"""

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
        """Encodes the number into a value that takes the charset size as a
        base, using the charset values"""

        assert number >= 0, 'Number must be a positive value'
        result = ''

        if number == 0:
            return self.charset[0]
        while number > 0:
            tmp = number % self.base
            result += self.charset[tmp]
            number //= self.base

        return result[::-1]

    def decode(self, encoded: str) -> int:
        """Decode the string value to an integer, according to the charset and the base"""
        if not self.case:
            encoded = encoded.lower()
        assert len(set(self.charset + encoded)) == len(self.charset), \
            f"These characters are unknow in the instance charset: " \
            f"`{','.join(sorted(set(encoded) - set(self.charset)))}`"

        return reduce(lambda count, c: count * self.base + self.charset.index(c), encoded, 0)
