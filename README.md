# Minimap positions
Мод на динамические позиции на миникарте от WotStat

## Компиляция 
На Unix системах `./build.sh -v 1.0.0 -d` в папке `WOTSTAT`. Флаг `-d` отвечает за дебаг версию с print_debug выводом.

## Схема API v1
### Запрос позиций
`GET /api/v1/positions`

Параметры:
| Параметр   | Описание                                                  | Пример                 |
| ---------- | --------------------------------------------------------- | ---------------------- |
| region     | Регион игрока `AUTH_REALM`                                | RU                     |
| mode       | Режим игры `ARENA_TAGS[player.arena.bonusType]`           | REGULAR                |
| gameplay   | Тип игры `ARENA_GAMEPLAY_NAMES[player.arenaTypeID >> 16]` | сtf                    |
| arena      | Тен название карты `player.arena.arenaType.geometry`      | spaces/03_campania_big |
| tank       | Танк тег                                                  | uk:GB100_Manticore     |
| level      | Уровень танка                                             | 10                     |
| type       | Тип танка                                                 | LT                     |
| role       | Роль танка                                                | role_LT_universal      |
| health     | ХП танка в долях от максимального                         | 0.95                   |
| position   | Координата танка                                          | (100.8,0,-100)         |
| time       | Время боя в секундах                                      | 100                    |
| allyfrags  | Число фрагов союзников                                    | 5                      |
| enemyfrags | Число фрагов противников                                  | 5                      |

Ответ:
```json
{
  "status": "ok",
  "message": {
    "RU": "test",
    "EN": "test"
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