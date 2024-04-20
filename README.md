# Minimap positions
Мод на динамические позиции на миникарте от WotStat

## Компиляция 
На Unix системах `./build.sh -v 1.0.0 -d`. Флаг `-d` отвечает за дебаг версию с выводом логов уровня `DEBUG`.

## Редактирование
Для корректной типизации и подсказок кода, рекоменду в корень проекда докачать следующие репозитории:

```bash
git clone git@bitbucket.org:IzeBerg/modssettingsapi.git
git clone https://github.com/IzeBerg/wot-src.git
git clone https://github.com/SoprachevAK/BigWorldPlaceholder.git
```

При редактировании в `vscode` установите расширение `Ruff`

## Схема API v1
### Запрос позиций
`POST /api/v1/positions`

Тело:
| Параметр       | Описание                                                  | Пример                                      |
| -------------- | --------------------------------------------------------- | ------------------------------------------- |
| id             | UUID боя, уникальный на начало                            | 8bb133ae-747b-4c5d-9c8f-3d8c7160c3e3        |
| language       | Язык клиента                                              | ru                                          |
| token          | Токен из прошлого ответа                                  | XXX                                         |
| region         | Регион игрока `AUTH_REALM`                                | RU                                          |
| mode           | Режим игры `ARENA_TAGS[player.arena.bonusType]`           | REGULAR                                     |
| gameplay       | Тип игры `ARENA_GAMEPLAY_NAMES[player.arenaTypeID >> 16]` | сtf                                         |
| arena          | Тен название карты `player.arena.arenaType.geometry`      | spaces/03_campania_big                      |
| team           | Команда игрока `player.team`                              | 0                                           |
| tank           | Танк тег                                                  | uk:GB100_Manticore                          |
| level          | Уровень танка                                             | 10                                          |
| type           | Тип танка                                                 | LT                                          |
| role           | Роль танка                                                | role_LT_universal                           |
| health         | ХП танка в долях от максимального                         | 0.95                                        |
| position       | Координата танка                                          | { x: 100, z: 100}                           |
| time           | Время боя в секундах                                      | 100                                         |
| allyFrags      | Число фрагов союзников                                    | 5                                           |
| enemyFrags     | Число фрагов противников                                  | 5                                           |
| allyHealth     | Суммарное здоровье союзников                              | 15000                                       |
| enemyHealth    | Суммарное здоровье противников                            | 16000                                       |
| allyMaxHealth  | Суммарное максимальное здоровье союзников                 | 20000                                       |
| enemyMaxHealth | Суммарное максимальное здоровье противников               | 20000                                       |
| allyRoles      | Роли союзных танкоы                                       | ["role_ATSPG_assault", "role_HT_universal"] |
| allyTypes      | Типы союзных танков                                       | ["AT", "HT"]                                |
| allyLevels     | Уровни союзных танков                                     | [10, 10]                                    |
| enemyRoles     | Роли противников                                          | ["role_ATSPG_assault", "role_HT_universal"] |
| enemyTypes     | Типы противников                                          | ["AT", "HT"]                                |
| enemyLevels    | Уровни противников                                        | [10, 10]                                    |

Пример:
```json
{
  "id": "8bb133ae-747b-4c5d-9c8f-3d8c7160c3e3",
  "language": "ru",
  "token": "1713639284541",
  "region": "RU",
  "mode": "MAPS_TRAINING",
  "gameplay": "maps_training",
  "arena": "spaces/07_lakeville",
  "team": 1,
  "tank": "ussr:R04_T-34_MapsTraining_Player_MT_1",
  "level": 5,
  "type": "MT",
  "role": "NotDefined",
  "health": 0,
  "position": {
    "x": -132,
    "z": -243
  },
  "time": 100,
  "allyFrags": 2,
  "enemyFrags": 1,
  "allyHealth": 0,
  "enemyHealth": 350,
  "allyMaxHealth": 740,
  "enemyMaxHealth": 550,
  "allyRoles": ["role_ATSPG_assault", "role_HT_universal", "role_HT_support", "role_LT_universal", "role_HT_support", "role_ATSPG_support", "role_ATSPG_sniper", "role_ATSPG_support", "role_MT_support", "role_SPG", "role_MT_universal", "role_ATSPG_assault", "role_MT_sniper", "role_MT_sniper", "role_LT_universal"],
  "allyTypes": ["AT", "HT", "HT", "LT", "HT", "AT", "AT", "AT", "MT", "SPG", "MT", "AT", "MT", "MT", "LT"],
  "allyLevels": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
  "enemyRoles": ["role_ATSPG_support", "role_HT_support", "role_ATSPG_support", "role_ATSPG_universal", "role_ATSPG_universal", "role_SPG", "role_MT_universal", "role_LT_universal", "role_MT_universal", "role_MT_universal", "role_MT_universal", "role_HT_break", "role_HT_break", "role_MT_universal", "role_LT_universal"],
  "enemyTypes": ["AT", "HT", "AT", "AT", "AT", "SPG", "MT", "LT", "MT", "MT", "MT", "HT", "HT", "MT", "LT"],
  "enemyLevels": [ 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10 ]
}
```

Ответ:
```json
{
  "status": "ok",
  "token": "XXX",
  "message": {
    "type": "info",
    "value": "test"
  },
  "statistics": {
    "tag": null,
    "role": null,
    "type": "HT",
    "level": 10,
    "health": 0.5,
    "time": 10000,
    "position": false,
    "allyFrags": null,
    "enemyFrags": null,
    "count": 5000
  },
  "positions": {
    "polygons": [
      {
        "efficiency": 0.5,
        "area": [[0, 0], [0, 100], [100, 100], [100, 0]]
      }
    ],
    "points": [
      {
        "efficiency": 0.5,
        "position": [50, 50]
      }
    ],
    "idealPoints": [
      {
        "efficiency": 0.5,
        "position": [50, 50]
      }
    ]
  }
}
```