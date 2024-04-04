# -*- coding: utf-8 -*-
from helpers import getClientLanguage
from Singleton import Singleton

RU = {
  'settings:modDisplayName': 'Мод «Позиции на миникарте» от WotStat',
  'settings:showArea': 'Отображать области эффективности',
  'settings:showMiniMarkers': 'Отображать позиции эффективности',
  'settings:showIdealMarker': 'Отображать маркер наилучшей позиции',
  'settings:showAreaTooltip': '{HEADER}Области эффективности{/HEADER}{BODY}На миникарте бубут отображаться области эффективности с помощью заливки точками{/BODY}',
  'settings:showMiniMarkersTooltip': '{HEADER}Позиции эффективности{/HEADER}{BODY}На миникарте будут отображаться позиции эффективности с помощью маркеров{/BODY}',
  'settings:showIdealTooltip': '{HEADER}Маркер наилучшей позиции{/HEADER}{BODY}На миникарте и в ИГРЕ будет отображаться маркер наилучшей позиции, если такая имеется{/BODY}',
  'settings:areaChangeKey': 'Переключить области в бою',
  'settings:areaChangeKeyTooltip': '{HEADER}Переключение режима отображения области{/HEADER}{BODY}Во время боя нажмите эту клавишу для изменения режима отображения области эффективности.\nВарианты: Никогда/По Alt/Постоянно{/BODY}',
  'settings:markersChangeKey': 'Переключить позиции в бою',
  'settings:markersChangeKeyTooltip': '{HEADER}Переключение режима отображения позиций{/HEADER}{BODY}Во время боя нажмите эту клавишу для изменения режима отображения позиций эффективности.\nВарианты: Никогда/По Alt/Постоянно{/BODY}',
  'settings:idealChangeKey': 'Переключить наилучший маркера в бою',
  'settings:idealChangeKeyTooltip': '{HEADER}Переключение режима отображения наилучшей позиции{/HEADER}{BODY}Во время боя нажмите эту клавишу для изменения режима отображения наилучшей позиции.\nВарианты: Никогда/По Alt/Постоянно{/BODY}',
  'settings:areaDensity': 'Плотность точек областей',
  'settings:areaDensityTooltip': '{HEADER}Плотность точек областей{/HEADER}{BODY}Чем выше значение, тем больше точек будет отображаться на миникарте.\n\n<b>ВНИМАНИЕ!</b>\nВысокая плотность может вызывать подвисания на слабых компьютерах. Рекомендуется протестировать в «тренировочных боях» или «топографии»\n\n<i>По умолчанию: 20</i>{/BODY}',
  'settings:interval': 'Интервал обновления',
  'settings:intervalFormat': '{{value}} сек.',
  'settings:intervalTooltip': '{HEADER}Интервал обновления{/HEADER}{BODY}Как часто будут обновляться позиции на миникарте (в секундах)\n\n<i>По умолчанию: 20</i>{/BODY}',
  'settings:reset': 'Сбросить',
  'settings:never': 'Никогда',
  'settings:onAlt': 'По нажанитю на Alt',
  'settings:always': 'Постоянно',
}

EN = {
  "test": "Test",
}

class I18n(Singleton):
  @staticmethod
  def instance():
      return I18n()

  def __init__(self):
    language = getClientLanguage()

    if language == 'ru':
      self.current_localizations = RU
    else:
      self.current_localizations = EN

  def t(self, key):
    if key in self.current_localizations:
      return self.current_localizations[key]
    return key
  
  def translate(self, key):
    return self.t(key)
  
def t(key):
  return I18n.instance().t(key)


