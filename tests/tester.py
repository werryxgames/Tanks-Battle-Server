"""Модуль проверки тестов."""
from colorama import Fore


class Tester:
    """Класс проверки тестов."""

    def __init__(self, logger, module, quiet=False):
        self.logger = logger
        self.module = module
        self.quiet = quiet
        self.num = 0
        self.tfailed = 0
        self.tsuccess = 0

        if not quiet:
            self.logger.info(
                f"Тестирование класса \"{self.module.__name__}\"",
                prefix=""
            )

    def passed(self):
        """Помечает текущий тест как пройденный."""
        if not self.quiet:
            self.logger.message(
                Fore.GREEN + f"Тест {self.num} пройден" + Fore.RESET
            )

        self.tsuccess += 1

    def failed(self, reason):
        """Помечает текущий тест как проваленный."""
        if not self.quiet:
            self.logger.error(f"Тест {self.num} провален: {reason}", prefix="")

        self.tfailed += 1

    def ret_value(self, module_method, *args, **kwargs):
        """Возвращает результат выполнения module_method()."""
        try:
            res = getattr(self.module, module_method)(*args, **kwargs)
            return res
        except IndexError:
            self.failed("метод не найден")
        except BaseException as e:
            self.failed(f"произошла ошибка \"{type(e).__name__}\"")

        return None

    def check_statement(self, result):
        """Проверяет выражение на положительный результат."""
        if result:
            self.passed()
        else:
            if not self.quiet:
                self.failed(
                    f"ожидался результат \"True\", получен результат \
\"{result}\""
                )
        return result

    def check(self, output, expected):
        """Проверяет output на соответствие с expected."""
        try:
            assert output == expected
        except AssertionError:
            self.failed(
                f"ожидался результат \"{expected}\", получен результат \
\"{output}\""
            )
            return False
        except BaseException as e:
            if isinstance(e, expected):
                self.passed()
                return True

            self.failed(f"произошла ошибка \"{type(e).__name__}\"")
            return False

        self.passed()
        return True

    def test(self, module_method, result, *args, **kwargs):
        """Тестирует module_method() на соответствие с result."""
        try:
            self.num += 1
        except AttributeError:
            print("У этого класса либо ещё ни разу не был вызван '__init__'\
, либо уже был вызван 'end'")
            return None
        try:
            res = getattr(self.module, module_method)(*args, **kwargs)

            try:
                assert res == result
            except AssertionError:
                self.failed(
                    f"ожидался результат \"{result}\", получен результат \
\"{res}\""
                )
                return False
        except IndexError:
            self.failed("метод не найден")
            return False
        except BaseException as e:
            try:
                if isinstance(e, result):
                    self.passed()
                    return True

                raise e
            except BaseException:
                self.failed(f"произошла ошибка \"{type(e).__name__}\"")
                return False

        self.passed()
        return True

    def end(self):
        """Завершает тестирование модуля."""
        if not self.quiet:
            self.logger.message(
                f"Пройдено тестов: {self.tsuccess}, провалено: {self.tfailed}\
 (всего: {self.num})"
            )
            self.logger.message("")

        tf = self.tfailed

        delattr(self, "logger")
        delattr(self, "module")
        delattr(self, "quiet")
        delattr(self, "num")
        delattr(self, "tfailed")
        delattr(self, "tsuccess")

        return tf == 0
