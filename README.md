# Tanks Battle Server
[![CodeQL](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/codeql.yml/badge.svg?branch=master)](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/codeql.yml)
[![Тесты кода](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/tests.yml)

Официальный сервер для многопользовательской игры "Tanks Battle"

Скачать "Tanks Battle" можно по ссылке **[Werryx Games](https://werryxgames.ml/games/#tanks_battle)**

# Установка
## Linux
Используйте команду
```bash
cd ~ && sudo apt-get update -y && sudo apt-get install git python -y && git clone https://github.com/werryxgames/Tanks-Battle-Server.git && cd Tanks-Battle-Server && python main.py
```
чтобы установить все зависимости и запустить сервер

Добавьте ` --nogui` в конец, чтобы запустить сервер без графического интерфейса

Для последующего запсука используйте
```bash
python ~/Tanks-Battle-Server/main.py
```

## Запуск на Windows
Скачайте код этого репозитория

Распакуйте скачанный архив в папку

Установите [Python](https://python.org/download)

Откройте терминал (Нажмите Win + R и напишите `cmd.exe`)

Введите
```bash
cd распакованная_папка
python main.py
```

Добавьте ` --nogui` в конец, чтобы запустить сервер без графического интерфейса

Для последующего запуска используйте
```bash
python распакованная_папка/main.py
```

## Запуск на Android
### С графическим интерфейсом
Скачайте код этого репозитория

Распакуйте скачанный архив в папку

Установите Pydroid из Play Marketа

Откройте Pydroid, нажмите `Open` и выберите файл `main.py` в распакованной папке

Запустите код

### Без графического интерфейса, новейшая версия Python
Скачайте Termux из Play Marketа

Запустите Termux и введите
```bash
termux-setup-storage && cd /sdcard && apt-get update -y && apt-get install git python -y && cd Tanks-Battle-Server && python main.py
```

Вы можете добавить `--nogui` в конец, но ничего не изменится, так как Termux по умолчанию не поддерживает графический интерфейс

Для последующего запуска используйте
```bash
python /sdcard/Tanks-Battle-Server/main.py
```

# Обновление сервера
## Графический интерфейс
Отключите сервер, если он включён

Перейдите в директорию с **Tanks Battle Server**

Скопируйте файл `data.json` в надёжное место

Удалите **Tanks Battle Server**

Выполните этап [Установка](установка)

Замените новый файл `data.json` на старый

**Только данные игроков, корпусов, башен, комплектов и карт сохранятся**, а также не добавятся новые корпуса, башни, комплекты и карты. Вы можете добавить их вручную

## Терминал Linux (Termux)
Отключите сервер, если он включён

Откройте терминал

Перейдите в директорию с **Tanks Battle Server** (`cd`)

Выполните команду
```bash
rm tbsold_data.json && cp data.json ../tbsold_data.json && rm . -rf && cd .. && git clone https://github.com/werryxgames/Tanks-Battle-Server && cat Tanks-Battle-Server/data.json && rm Tanks-Battle-Server/data.json && mv tbsold_data.json Tanks-Battle-Server/data.json
```

В конце результата команды будет содержимое нового файла `data.json`. Вы можете изменить старый в соответствии с новым (добавить корпуса, башни, комплекты и карты из нового файла)

Теперь вы можете запустить новую версию сервера как обычно

# Версии
Статусы поддержки версий:

**full** - Полная поддержка, исправление ошибок и уязвимостей

**security** - Только исправление уязвимостей

**none** - Не поддерживается

| Версия  | Статус поддержки   |
| ------- | ------------------ |
| 1.4.0   | **full**           |
| 1.3.0   | **full**           |
| 1.2.0   | **security**       |
| 1.1.0   | **security**       |
| 1.0.0   | **none**           |
