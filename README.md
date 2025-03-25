# Minimap positions
Исходный код мода на от WotStat

Сайт [positions.wotstat.info](https://positions.wotstat.info)

## Компиляция 
На Unix системах `./build.sh -v 1.0.0 -d`. Флаг `-d` отвечает за дебаг версию с выводом логов уровня `DEBUG`.

## Редактирование
Для корректной типизации и подсказок кода, в папку `helpers` скачать следующие репозитории:

```bash
git clone git@bitbucket.org:IzeBerg/modssettingsapi.git
git clone https://github.com/IzeBerg/wot-src.git
git clone https://github.com/Kurzdor/wot.bigworld-placeholder
```

Установить `Apache Royale` для компиляции `flash`

```bash
npm install -g @apache-royale/royale-js
```

Установить рекомендуемые расширения:
- [ActionScript & MXML](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Python](https://marketplace.visualstudio.com/items?itemName=bowlerhatllc.vscode-as3mxml)

## CICD
На каждый `tag` в `GitHub` автоматически создаётся релиз к которому прикладывается скомпилированная версия мода.