from colorama import Fore


class Tester:
    def __init__(self, logger, module, quiet=False):
        self.logger = logger
        self.module = module
        self.quiet = quiet
        self.num = 0
        if not quiet:
            self.logger.info(f"Тестирование класса \"{self.module.__name__}\"", prefix="")

    def passed(self):
        if not self.quiet:
            self.logger.message(Fore.GREEN + f"Тест {self.num} пройден" + Fore.RESET)

    def failed(self, reason):
        if not self.quiet:
            self.logger.error(f"Тест {self.num} провален: {reason}", prefix="")

    def ret_value(self, module_method, *args, **kwargs):
        try:
            res = getattr(self.module, module_method)(*args, **kwargs)
            return res
        except IndexError:
            self.failed("метод не найден")
        except BaseException as e:
            self.failed(f"произошла ошибка \"{type(e).__name__}\"")

    def check_statement(self, result):
        if result:
            self.passed()
        else:
            if not self.quiet:
                self.failed(f"ожидался результат \"True\", получен результат \"{result}\"")
        return result

    def check(self, output, expected):
        try:
            assert output == expected
        except AssertionError:
            self.failed(f"ожидался результат \"{expected}\", получен результат \"{output}\"")
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
                self.failed(f"ожидался результат \"{result}\", получен результат \"{res}\"")
                return False
        except IndexError:
            self.failed("метод не найден")
            return False
        except BaseException as e:
            if isinstance(e, result):
                self.passed()
                return True
            self.failed(f"произошла ошибка \"{type(e).__name__}\"")
            return False
        self.passed()
        return True

    def end(self):
        if not self.quiet:
            self.logger.message("")
        delattr(self, "logger")
        delattr(self, "module")
        delattr(self, "quiet")
        delattr(self, "num")
