@echo off

call activenv
call flake . --select=F,E,W,R,C --count --max-complexity=10 --show-source --statistics
pylint . --disable=all --enable=C0114,C0115,C0116
python -m pytest tests
echo Можно выполнить коммит
