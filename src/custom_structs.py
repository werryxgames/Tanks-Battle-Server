"""Module with custom Tanks Battle structures."""
from serializer import BinaryStruct
from serializer import ByteBuffer


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

        return TankStruct({
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
        }, have_tank)

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


class SettingsStruct(BinaryStruct):
    def __init__(self, settings_data):
        self.settings = settings_data

    @staticmethod
    def __bb_init__(buffer: ByteBuffer) -> BinaryStruct:
        return SettingsStruct([buffer.get_boolean(), buffer.get_boolean(), buffer.get_u16()])

    def __bb_get__(self):
        return self.settings

    def __bb_size__(self):
        return 1 + 1 + 2

    def __bb_put__(self, buffer: ByteBuffer):
        (
            buffer
            .put_boolean(self.settings[0])
            .put_boolean(self.settings[1])
            .put_u16(self.settings[2])
        )


class MatchStruct(BinaryStruct):
    def __init__(self, match_data):
        self.match_ = match_data

    @staticmethod
    def __bb_init__(buffer: ByteBuffer) -> BinaryStruct:
        return MatchStruct(
            {
                "max_players": buffer.get_u8(),
                "players": buffer.get_u8(),
                "map": buffer.get_u16()
            }
        )

    def __bb_get__(self):
        return self.match_

    def __bb_size__(self):
        return 1 + 1 + 2

    def __bb_put__(self, buffer: ByteBuffer):
        (
            buffer
            .put_u8(self.match_["max_players"])
            .put_u8(self.match_["players"])
            .put_u16(self.match_["map"])
        )


class BattleTankStruct(BinaryStruct):
    """Class, that represents tank data in hangar."""

    def __init__(self, tank_data: dict):
        self.tank = tank_data

    @staticmethod
    def __bb_init__(buffer: ByteBuffer) -> BinaryStruct:
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

        return BattleTankStruct({
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
        })

    def __bb_get__(self):
        return self.tank

    def __bb_size__(self):
        return 48

    def __bb_put__(self, buffer: ByteBuffer):
        (
            buffer
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
        )


class BattlePlayerStruct(BinaryStruct):
    def __init__(self, battle_player):
        self.player = battle_player

    @staticmethod
    def __bb_init__(buffer: ByteBuffer) -> BinaryStruct:
        arr = [
            buffer.get_string(),
            (buffer.get_float(), buffer.get_float(), buffer.get_float()),
            (buffer.get_float(), buffer.get_float(), buffer.get_float()),
            buffer.get_u16(),
            (buffer.get_float(), buffer.get_float(), buffer.get_float()),
            buffer.get_u32()
        ]
        return BattleDataStruct(arr)

    def __bb_get__(self):
        return self.player

    def __bb_size__(self):
        return len(self.player[0].encode("UTF-8")) + 1 + 42

    def __bb_put__(self, buffer: ByteBuffer):
        buffer.put_string(self.player[0])
        buffer.put_float(self.player[1][0])
        buffer.put_float(self.player[1][1])
        buffer.put_float(self.player[1][2])
        buffer.put_float(self.player[2][0])
        buffer.put_float(self.player[2][1])
        buffer.put_float(self.player[2][2])
        buffer.put_u16(self.player[3])
        buffer.put_float(self.player[4][0])
        buffer.put_float(self.player[4][1])
        buffer.put_float(self.player[4][2])
        buffer.put_u32(self.player[5])


class BattleDataStruct(BinaryStruct):
    def __init__(self, battle_data):
        self.battle = battle_data

    @staticmethod
    def __bb_init__(buffer: ByteBuffer) -> BinaryStruct:
        arr = [
            buffer.get_string(),
            [buffer.get_struct(BattlePlayerStruct), buffer.get_struct(BattleTankStruct)]
        ]
        players_count = buffer.get_u8()
        players = []

        for _i in range(players_count):
            players.append([
                buffer.get_struct(BattlePlayerStruct),
                buffer.get_struct(BattleTankStruct)
            ])

        arr.append(players)
        arr.append(buffer.get_struct(SettingsStruct))
        return BattleDataStruct(arr)

    def __bb_get__(self):
        return self.battle

    def __bb_size__(self):
        return len(self.battle[0].encode("UTF-8")) + 1 + self.battle[1][0].__bb_size__() + self.battle[1][1].__bb_size__() + 1 + sum([i[0].__bb_size__() + i[1].__bb_size__() for i in self.battle[2]]) + self.battle[3].__bb_size__()

    def __bb_put__(self, buffer: ByteBuffer):
        buffer.put_string(self.battle[0])
        buffer.put_struct(self.battle[1][0])
        buffer.put_struct(self.battle[1][1])
        buffer.put_u8(len(self.battle[2]))

        for i in self.battle[2]:
            buffer.put_struct(i[0])
            buffer.put_struct(i[1])

        buffer.put_struct(self.battle[3])


class TankDataStruct(BinaryStruct):
    def __init__(self, tank_data):
        self.data = tank_data

    @staticmethod
    def __bb_init__(buffer: ByteBuffer) -> BinaryStruct:
        tanks_count: int = buffer.get_u8()
        arr = [buffer.get_struct(BattlePlayerStruct) for _i in range(tanks_count)]
        return TankDataStruct(arr)

    def __bb_get__(self):
        return self.data

    def __bb_size__(self):
        return 1 + sum([bp.__bb_size__() for bp in self.arr])

    def __bb_put__(self, buffer: ByteBuffer):
        buffer.put_u8(len(self.data))

        for bp in self.data:
            buffer.put_struct(bp)


class BattlePlayerDataStruct(BinaryStruct):
    def __init__(self, bp_data):
        self.data = bp_data

    @staticmethod
    def __bb_init__(buffer: ByteBuffer) -> BinaryStruct:
        return BattlePlayerDataStruct([
            buffer.get_float(),
            buffer.get_float(),
            buffer.get_float(),
            buffer.get_float(),
            buffer.get_float(),
            buffer.get_float(),
            buffer.get_float(),
            buffer.get_float(),
            buffer.get_float(),
            buffer.get_u32()
        ])

    def __bb_get__(self):
        return self.data

    def __bb_size__(self):
        return 40

    def __bb_put__(self, buffer: ByteBuffer):
        buffer.put_float(self.data[0])
        buffer.put_float(self.data[1])
        buffer.put_float(self.data[2])
        buffer.put_float(self.data[3])
        buffer.put_float(self.data[4])
        buffer.put_float(self.data[5])
        buffer.put_float(self.data[6])
        buffer.put_float(self.data[7])
        buffer.put_float(self.data[8])
        buffer.put_u32(self.data[9])
