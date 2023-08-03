"""Module for binary data serialization and deserialization."""
from struct import pack
from struct import unpack
from struct import error
from typing import Self


class ByteBufferException(Exception):
    """Base exception for ByteBuffer."""


class ByteBufferOutOfRange(ByteBufferException):
    """
        Raised when trying to write value, that is bigger / smaller, than
            acceptable.
    """


class BinaryStruct:
    """Base structure for `ByteBuffer` `put_struct()` / `get_struct()`."""

    @staticmethod
    def __bb_init__(buffer) -> Self:
        """Initializes structure and saves it's value."""
        raise NotImplementedError

    def __bb_get__(self):
        """Returns saved structure value."""
        raise NotImplementedError

    def __bb_size__(self):
        """Returns size of structure."""
        raise NotImplementedError

    def __bb_put__(self, buffer):
        """Puts structure to `buffer`."""
        raise NotImplementedError


class ByteBuffer:
    """Class for binary data manipulation."""

    def __init__(self, arg: bytearray | int):
        """Default constructor for ByteBuffer."""
        self.barr = None
        self.position = 0

        if isinstance(arg, int):
            self.__init_int(arg)
        elif isinstance(arg, (bytearray, bytes)):
            self.__init_bytearray(arg)
        else:
            raise ByteBufferException("Invalid __init__() arguments")

    def __init_int(self, capacity: int):
        """Constructor for ByteBuffer(int)."""
        self.barr = bytearray(capacity)

    def __init_bytearray(self, barr: bytearray):
        """Constructor for ByteBuffer(bytearray)."""
        self.barr = barr

    def is_reached_end(self, size=0):
        """
            Checks if current buffer position with size more than bytearray
                length.
        """
        return self.position + size > len(self.barr)

    def _check(self, size=0):
        """Raises exception if end of buffer reached"""
        if self.is_reached_end(size):
            raise ByteBufferException("End of ByteBuffer reached")

    def _base_put(self, value, size, pack_val):
        """
            Puts value to buffer with size `size` using
                `struct.pack(pack_val)`.
        """
        self._check(size)
        try:
            packed_value = pack(f">{pack_val}", value)
        except error as exc:
            raise ByteBufferOutOfRange("Invalid value") from exc

        for i in range(size):
            self.barr[self.position] = packed_value[i]
            self.position += 1

        return self

    def put_u8(self, value: int):
        """Puts `unsigned char` to buffer."""
        return self._base_put(value, 1, "B")

    def put_u16(self, value: int):
        """Puts `unsigned short` to buffer."""
        return self._base_put(value, 2, "H")

    def put_u32(self, value: int):
        """Puts `unsigned int` to buffer."""
        return self._base_put(value, 4, "I")

    def put_u64(self, value: int):
        """Puts `unsigned long long` to buffer."""
        return self._base_put(value, 8, "Q")

    def put_8(self, value: int):
        """Puts `char` to buffer."""
        return self._base_put(value, 1, "b")

    def put_16(self, value: int):
        """Puts `short` to buffer."""
        return self._base_put(value, 2, "h")

    def put_32(self, value: int):
        """Puts `int` to buffer."""
        return self._base_put(value, 4, "i")

    def put_64(self, value: int):
        """Puts `long long` to buffer."""
        return self._base_put(value, 8, "q")

    def put_boolean(self, value: int):
        """Puts `bool` to buffer."""
        return self._base_put(value, 1, "?")

    def put_float(self, value: float):
        """Puts `float` to buffer."""
        return self._base_put(value, 4, "f")

    def put_double(self, value: float):
        """Puts `double` to buffer."""
        return self._base_put(value, 8, "d")

    def put_string(self, string: str):
        """Puts UTF-8 string (`char[]`) to buffer."""
        utf8_bytes = string.encode("utf8")
        return self._base_put(
            utf8_bytes,
            len(utf8_bytes) + 1,
            f"{len(utf8_bytes) + 1}s"
        )

    def put_bytes(self, bytes_: bytes):
        """Puts bytes to buffer."""
        return self._base_put(
            bytes_,
            len(bytes_),
            f"{len(bytes_)}s"
        )

    def put_struct(self, struct: BinaryStruct):
        """Puts struct to buffer."""
        struct.__bb_put__(self)
        return self

    def _base_get(self, size, pack_val):
        """Gets value with size `size` using `struct.unpack(pack_val)`."""
        self._check(size)
        bytes_ = bytearray(size)

        for i in range(size):
            bytes_[i] = self.barr[self.position]
            self.position += 1

        return unpack(f">{pack_val}", bytes_)[0]

    def get_u8(self):
        """Returns `unsigned char` and moves buffer cursor."""
        return self._base_get(1, "B")

    def get_u16(self):
        """Returns `unsigned short` and moves buffer cursor."""
        return self._base_get(2, "H")

    def get_u32(self):
        """Returns `unsigned int` and moves buffer cursor."""
        return self._base_get(4, "I")

    def get_u64(self):
        """Returns `unsigned long long` and moves buffer cursor."""
        return self._base_get(8, "Q")

    def get_8(self):
        """Returns `char` and moves buffer cursor."""
        return self._base_get(1, "b")

    def get_16(self):
        """Returns `short` and moves buffer cursor."""
        return self._base_get(2, "h")

    def get_32(self):
        """Returns `int` and moves buffer cursor."""
        return self._base_get(4, "i")

    def get_64(self):
        """Returns `long long` and moves buffer cursor."""
        return self._base_get(8, "q")

    def get_boolean(self):
        """Returns `bool` and moves buffer cursor."""
        return self._base_get(1, "?")

    def get_float(self):
        """Returns `float` and moves buffer cursor."""
        return self._base_get(4, "f")

    def get_double(self):
        """Returns `double` and moves buffer cursor."""
        return self._base_get(8, "d")

    def get_string(self):
        """Returns UTF-8 string (`char[]`) and moves buffer cursor."""
        bytes_ = bytearray()

        for byte in self.barr[self.position:]:
            if byte == 0:
                break

            bytes_.append(byte)

        self.position += len(bytes_) + 1
        return bytes_.decode("UTF-8")

    def get_fully(self):
        """
            Returns all remaining content from bytearray and moves buffer
                cursor.
        """
        self._check()
        result = self.barr[self.position:]
        self.position = len(self.barr)
        return result

    def get_struct(self, struct_type):
        """Returns struct from bytearray and moves buffer cursor."""
        self._check()

        if not isinstance(struct_type, type):
            raise ValueError("Type required")

        struct = struct_type.__bb_init__(self)
        return struct.__bb_get__()

    def rewind(self):
        """Returns cursor position to beginning."""
        self.position = 0
        return self

    def seek(self, position):
        """Sets cursor position to `position`."""
        self.position = position
        return self

    def seekcur(self, position):
        """Adds `position` to cursor position."""
        self.position += position
        return self

    def seekend(self, position):
        """Sets cursor position to `len(barr) - position`."""
        self.position = len(self.barr) - position
        return self

    def tell(self):
        """Returns buffer cursor position."""
        return self.position

    def to_bytes(self):
        """Returns bytearray of this buffer."""
        return self.barr
