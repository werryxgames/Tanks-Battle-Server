# Tanks Battle Server
[![CodeQL](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/codeql.yml/badge.svg?branch=master)](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/codeql.yml)
[![Тесты кода](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/werryxgames/Tanks-Battle-Server/actions/workflows/tests.yml)

Официальный сервер для многопользовательской игры "Tanks Battle"

Скачать "Tanks Battle" можно по ссылке **[Werryx Games](https://werryxgames.ml/games/#tanks_battle)**

# Установка
## Linux
Используйте команду
```bash
cd ~ && sudo apt-get update -y && sudo apt-get install git python -y && git clone https://github.com/werryxgames/Tanks-Battle-Server.git && cd Tanks-Battle-Server && pip install --upgrade pip && pip install -r requirements.txt && python src/main.py
```
чтобы установить все зависимости и запустить сервер

Добавьте ` --nogui` в конец, чтобы запустить сервер без графического интерфейса

Для последующего запсука используйте
```bash
python ~/Tanks-Battle-Server/src/main.py
```

## Запуск на Windows
Скачайте код этого репозитория

Распакуйте скачанный архив в папку

Установите [Python](https://python.org/download)

Откройте терминал (Нажмите Win + R и напишите `cmd.exe`)

Введите
```bash
cd распакованная_папка
python src/main.py
```

Добавьте ` --nogui` в конец, чтобы запустить сервер без графического интерфейса

Для последующего запуска используйте
```bash
python распакованная_папка/src/main.py
```

## Запуск на Android
### С графическим интерфейсом
Скачайте код этого репозитория

Распакуйте скачанный архив в папку

Установите Pydroid из Play Marketа

Откройте Pydroid, нажмите `Open` и выберите файл `main.py` в `src` в распакованной папке

Запустите код

### Без графического интерфейса, новейшая версия Python
Скачайте Termux из Play Marketа

Запустите Termux и введите
```bash
termux-setup-storage && cd /sdcard && apt-get update -y && apt-get install git python -y && git clone https://github.com/werryxgames/Tanks-Battle-Server && cd Tanks-Battle-Server && pip install --upgrade pip && pip install -r requirements.txt && python src/main.py
```

Вы можете добавить `--nogui` в конец, но ничего не изменится, так как Termux по умолчанию не поддерживает графический интерфейс

Для последующего запуска используйте
```bash
python /sdcard/Tanks-Battle-Server/src/main.py
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
rm tbsold_accounts.json & cp src/accounts.json ../tbsold_accounts.json & rm ../Tanks-Battle-Server -rf && cd .. && git clone https://github.com/werryxgames/Tanks-Battle-Server && mv tbsold_accounts.json Tanks-Battle-Server/accounts.json
```

В конце результата команды будет содержимое нового файла `data.json`. Вы можете изменить старый в соответствии с новым (добавить корпуса, башни, комплекты и карты из нового файла)

Теперь вы можете запустить новую версию сервера как обычно

# Обновление
## Обновление аккаунтов
Для обновления аккаунтов используйте `update/accounts.py`:
`python update/accounts.py <файл_к_старому_accounts.json>`

После выполнения этой команды без ошибок, содержимое указанного файла обновится до новейшего формата

Пример:
```json
[
    {
        "nick": "Werryx",
        "password": "...",
        "xp": 1234,
        "crystals": 567,
        "tanks": [
            1,
            2
        ],
        "guns": [
            0
        ],
        "pts": [
            1
        ],
        "selected_tank": 0,
        "selected_gun": 0,
        "selected_pt": -1,
        "settings": [
            true,
            true,
            1500
        ]
    }
]
```
заменится на
```json
[
    {
        "nick": "Werryx",
        "password": "...",
        "xp": 1234,
        "crystals": 567,
        "tanks": [
            0,
            1
        ],
        "selected_tank": 0,
        "settings": [
            true,
            true,
            1500
        ]
    }
]
```

Появился танк с ID *0*, так как он даётся всем по умолчанию и так как **комплект** не был выбран (*-1*), `selected_tank` изменилось на *0*

# Версии
Статусы поддержки версий:

**full** - Полная поддержка, исправление ошибок и уязвимостей

**security** - Только исправление уязвимостей

**none** - Не поддерживается

| Версия  | Статус поддержки   | Примерная дата смены статуса |
| ------- | ------------------ | ---------------------------- |
| 2.0     | **full**           | 01.08.2024                   |
| 1.5.0   | **none**           |                              |
| 1.4.0   | **none**           |                              |
| 1.3.0   | **none**           |                              |
| 1.2.0   | **none**           |                              |
| 1.1.0   | **none**           |                              |
| 1.0.0   | **none**           |                              |
