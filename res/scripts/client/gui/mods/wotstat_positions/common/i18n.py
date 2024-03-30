# -*- coding: utf-8 -*-
from helpers import getClientLanguage

RU = {
  "test": "Тест",
}

EN = {
  "test": "Test",
}

language = getClientLanguage()
current_localizations = RU

if language == 'ru':
  current_localizations = RU
else:
  current_localizations = EN


def t(key):
  if key in current_localizations:
    return current_localizations[key]
  return key
