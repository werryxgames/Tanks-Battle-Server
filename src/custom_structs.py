"""Module with custom Tanks Battle structures."""
from serializer import BinaryStruct
from serializer import ByteBuffer


class MapStruct(BinaryStruct):
    """Class, that represents map configuration."""

    def __init__(self, map_content: dict):
        self.map = map_content

    @staticmethod
    def __bb_init__(buffer: ByteBuffer) -> BinaryStruct:
        name = buffer.get_string()
        spawn_points_length = buffer.get_u16()
        spawn_points = []

        for _i in range(spawn_points_length):
            spawn_points.append([
                buffer.get_16(),
                buffer.get_16(),
                buffer.get_16()
            ])

        kill_y = buffer.get_16()
        return MapStruct({
            "name": name,
            "spawn_points": spawn_points,
            "kill_y": kill_y
        })

    def __bb_get__(self):
        return self.map

    def __bb_size__(self):
        return len(self.map["name"].encode("UTF-8")) + 1 + 2 + len(
            self.map["spawn_points"]
        ) * 3 * 2 + 2

    def __bb_put__(self, buffer: ByteBuffer):
        (
            buffer
            .put_string(self.map["name"])
            .put_u16(len(self.map["spawn_points"]))
        )

        for spawn_point in self.map["spawn_points"]:
            (
                buffer
                .put_16(spawn_point[0])
                .put_16(spawn_point[1])
                .put_16(spawn_point[2])
            )

        buffer.put_16(self.map["kill_y"])


class RankStruct(BinaryStruct):
    """Class, that represents rank configuraion."""

    def __init__(self, rank_configuration: dict):
        self.rank = rank_configuration

    @staticmethod
    def __bb_init__(buffer: ByteBuffer) -> BinaryStruct:
        name = buffer.get_string()
        texture = buffer.get_string()
        max_xp = buffer.get_u32()
        return RankStruct({
            "name": name,
            "texture": texture,
            "max_xp": max_xp
        })

    def __bb_get__(self):
        return self.rank

    def __bb_size__(self):
        return len(self.rank["name"].encode("UTF-8")) + 1 + len(
            self.rank["texture"].encode("UTF-8")
        ) + 1 + 4

    def __bb_put__(self, buffer: ByteBuffer):
        (
            buffer
            .put_string(self.rank["name"])
            .put_string(self.rank["texture"])
            .put_u32(self.rank["max_xp"])
        )
