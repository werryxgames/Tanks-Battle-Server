"""Модуль с тестами данных."""
from sys import path
from os import path as path_

try:
    path.append(
        path_.normpath(
            path_.join(
                path_.dirname(
                    path_.realpath(
                        __file__
                    )
                ),
                "..",
                "src"
            )
        )
    )
except IndexError:
    pass

from mjson import read
import pytest


# @pytest.mark.parametrize("filename", ["server.log"])
# def test_file_empty(filename):
#     """Тестирует пустой ли файл с названием filename."""
#     data = None

#     with open(path_.normpath(
#         path_.join(
#             path_.dirname(path_.realpath(__file__)),
#             "..",
#             "src",
#             filename
#         )
#     ), encoding="utf8") as file:
#         data = file.read()

#     assert data == ""


@pytest.mark.parametrize("filename, field", [["data.json", "accounts"]])
def test_file_empty_field(filename, field):
    """Тестирует пустое ли поле field файла с названием filename."""
    data = read(filename)
    assert not data[field]
