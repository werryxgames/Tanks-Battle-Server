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


class TankStruct(BinaryStruct):
    """Class, that represents tank data in hangar."""

    def __init__(self, tank_data: dict, have_tank: bool):
        self.tank = {**tank_data, "have": have_tank}

    @staticmethod
    def __bb_init__(buffer: ByteBuffer) -> BinaryStruct:
        name = buffer.get_string()
        # 0 == every value < 0, so unsigned int
        tank_durability = buffer.get_u32()
        tank_mass = buffer.get_float()
        tank_speed = buffer.get_32()
        tank_gravity = buffer.get_32()
        tank_rotation_speed = buffer.get_32()
        gun_damage = buffer.get_32()
        gun_rotation_speed = buffer.get_float()
        gun_shot_speed = buffer.get_float()
        gun_recoil = buffer.get_32()
        gun_recharge = buffer.get_float()
        gun_limit_x = buffer.get_float()
        gun_limit_y = buffer.get_float()
        price = buffer.get_32()
        position_x = buffer.get_u16()
        position_y = buffer.get_u16()
        type_ = buffer.get_u8()
        have_tank = buffer.get_boolean()

        return TankStruct(have_tank, {
            "name": name,
            "tank": {
                "durability": tank_durability,
                "mass": tank_mass,
                "speed": tank_speed,
                "gravity": tank_gravity,
                "rotation_speed": tank_rotation_speed
            },
            "gun": {
                "damage": gun_damage,
                "rotation_speed": gun_rotation_speed,
                "shot_speed": gun_shot_speed,
                "recoil": gun_recoil,
                "recharge": gun_recharge,
                "limits": [gun_limit_x, gun_limit_y]
            },
            "price": price,
            "position": [position_x, position_y],
            "type": type_,
            "have": have_tank
        })

    def __bb_get__(self):
        return (self.have, self.tank)

    def __bb_size__(self):
        return len(self.tank["name"].encode("UTF-8")) + 1 + 58

    def __bb_put__(self, buffer: ByteBuffer):
        (
            buffer
            .put_string(self.tank["name"])
            .put_u32(self.tank["tank"]["durability"])
            .put_float(self.tank["tank"]["mass"])
            .put_32(self.tank["tank"]["speed"])
            .put_32(self.tank["tank"]["gravity"])
            .put_32(self.tank["tank"]["rotation_speed"])
            .put_32(self.tank["gun"]["damage"])
            .put_float(self.tank["gun"]["rotation_speed"])
            .put_float(self.tank["gun"]["shot_speed"])
            .put_32(self.tank["gun"]["recoil"])
            .put_float(self.tank["gun"]["recharge"])
            .put_float(self.tank["gun"]["limits"][0])
            .put_float(self.tank["gun"]["limits"][1])
            .put_32(self.tank["price"])
            .put_u16(self.tank["position"][0])
            .put_u16(self.tank["position"][1])
            .put_u8(self.tank["type"])
            .put_boolean(self.tank["have"])
        )
