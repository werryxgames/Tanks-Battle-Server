from struct import pack
from struct import unpack
from struct import error


class ByteBufferException(Exception):
    """Base exception for ByteBuffer."""


class ByteBufferOutOfRange(ByteBufferException):
    """Raised when trying to write value, that is bigger / smaller, than acceptable."""


class ByteBuffer:
    """Class for binary data manipulation."""

    def __init__(self, arg: bytearray | int):
        self.barr = None
        self.position = 0

        if isinstance(arg, int):
            self.__init_int(arg)
        elif isinstance(arg, bytearray):
            self.__init_bytearray(arg)

    def __init_int(self, capacity: int):
        self.barr = bytearray(capacity)

    def __init_bytearray(self, barr: bytearray):
        self.barr = barr

    def is_reached_end(self, size=0):
        return self.position + size > len(self.barr)

    def _check(self, size):
        if self.is_reached_end(size):
            raise ByteBufferException("End of ByteBuffer reached")

    def _base_put(self, value, size, pack_val):
        self._check(size)
        try:
            packed_value = pack(f">{pack_val}", value)
        except error:
            raise ByteBufferOutOfRange("Invalid value")

        for i in range(size):
            self.barr[self.position] = packed_value[i]
            self.position += 1

        return self

    def put_u8(self, value: int):
        return self._base_put(value, 1, "B")

    def put_u16(self, value: int):
        return self._base_put(value, 2, "H")

    def put_u32(self, value: int):
        return self._base_put(value, 4, "I")

    def put_u64(self, value: int):
        return self._base_put(value, 8, "Q")

    def put_8(self, value: int):
        return self._base_put(value, 1, "b")

    def put_16(self, value: int):
        return self._base_put(value, 2, "h")

    def put_32(self, value: int):
        return self._base_put(value, 4, "i")

    def put_64(self, value: int):
        return self._base_put(value, 8, "q")

    def put_boolean(self, value: int):
        return self._base_put(value, 1, "?")

    def put_float(self, value: float):
        return self._base_put(value, 4, "f")

    def put_double(self, value: float):
        return self._base_put(value, 8, "d")

    def put_string(self, string: str):
        utf8_bytes = string.encode("utf8")
        return self._base_put(utf8_bytes, len(utf8_bytes) + 1, f"{len(utf8_bytes) + 1}s")

    def _base_get(self, size, pack_val):
        self._check(size)
        bytes_ = bytearray(size)

        for i in range(size):
            bytes_[i] = self.barr[self.position]
            self.position += 1

        return unpack(f">{pack_val}", bytes_)[0]

    def get_u8(self):
        return self._base_get(1, "B")

    def get_u16(self):
        return self._base_get(2, "H")

    def get_u32(self):
        return self._base_get(4, "I")

    def get_u64(self):
        return self._base_get(8, "Q")

    def get_8(self):
        return self._base_get(1, "b")

    def get_16(self):
        return self._base_get(2, "h")

    def get_32(self):
        return self._base_get(4, "i")

    def get_64(self):
        return self._base_get(8, "q")

    def get_boolean(self):
        return self._base_get(1, "?")

    def get_float(self):
        return self._base_get(4, "f")

    def get_double(self):
        return self._base_get(8, "d")

    def get_string(self):
        bytes_ = bytearray()

        for byte in self.barr[self.position:]:
            if byte == 0:
                break

            bytes_.append(byte)

        return bytes_.decode("UTF-8")

    def get_fully(self):
        self._check()
        result = self.barr[self.position:]
        self.position = len(self.barr)
        return result

    def rewind(self):
        self.position = 0
        return self

    def seek(self, position):
        self.position = position
        return self

    def seekcur(self, position):
        self.position += position
        return self

    def seekend(self, position):
        self.position = len(self.barr) - position
        return self

    def tell(self):
        return self.position

    def to_bytes(self):
        return self.barr
