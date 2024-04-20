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
  'settings:areaDensityTooltip': '{HEADER}Плотность точек областей{/HEADER}{BODY}Чем выше значение, тем больше точек будет отображаться на миникарте.\n\n<b>ВНИМАНИЕ!</b>\nВысокая плотность может вызывать подвисания на слабых компьютерах. Рекомендуется протестировать в «тренировочных боях» или «топографии»\n\n<i>По умолчанию: 65</i>{/BODY}',
  'settings:interval': 'Интервал обновления',
  'settings:intervalFormat': '{{value}} сек.',
  'settings:intervalTooltip': '{HEADER}Интервал обновления{/HEADER}{BODY}Как часто будут обновляться позиции на миникарте (в секундах)\n\n<i>По умолчанию: 30</i>{/BODY}',
  'settings:showInfoMessages': 'Отображать информационные сообщения',
  'settings:showInfoMessagesTooltip': '{HEADER}Отображение информационных сообщений{/HEADER}{BODY}Включите, чтобы отображать информационные сообщения над миникартой.{/BODY}',
  'settings:reset': 'Сбросить',
  'settings:never': 'Никогда',
  'settings:onAlt': 'По нажанитю на Alt',
  'settings:always': 'Постоянно',
  'battleMessage:showArea': 'Отображение областей',
  'battleMessage:showMiniMarkers': 'Отображение позиций',
  'battleMessage:showIdealMarker': 'Отображение наилучшего маркера',
}

EN = {
  'settings:modDisplayName': 'Minimap positions by WotStat',
  'settings:showArea': 'Display efficiency areas',
  'settings:showMiniMarkers': 'Display efficiency positions',
  'settings:showIdealMarker': 'Display marker for the best position',
  'settings:showAreaTooltip': '{HEADER}Efficiency areas{/HEADER}{BODY}Efficiency areas will be displayed on the minimap using dotted fill{/BODY}',
  'settings:showMiniMarkersTooltip': '{HEADER}Efficiency positions{/HEADER}{BODY}Efficiency positions will be displayed on the minimap using markers{/BODY}',
  'settings:showIdealTooltip': '{HEADER}Marker for the best position{/HEADER}{BODY}A marker for the best position, if available, will be displayed on the minimap and in GAME{/BODY}',
  'settings:areaChangeKey': 'Toggle areas in battle',
  'settings:areaChangeKeyTooltip': '{HEADER}Toggling the display mode of the area{/HEADER}{BODY}During a battle, press this key to change the display mode of the efficiency area.\nOptions: Never/On Alt/Always{/BODY}',
  'settings:markersChangeKey': 'Toggle positions in battle',
  'settings:markersChangeKeyTooltip': '{HEADER}Toggling the display mode of positions{/HEADER}{BODY}During a battle, press this key to change the display mode of efficiency positions.\nOptions: Never/On Alt/Always{/BODY}',
  'settings:idealChangeKey': 'Toggle the best marker in battle',
  'settings:idealChangeKeyTooltip': '{HEADER}Toggling the display mode of the best position{/HEADER}{BODY}During a battle, press this key to change the display mode of the best position.\nOptions: Never/On Alt/Always{/BODY}',
  'settings:areaDensity': 'Dot density of areas',
  'settings:areaDensityTooltip': '{HEADER}Dot density of areas{/HEADER}{BODY}The higher the value, the more dots will be displayed on the minimap.\n\n<b>WARNING!</b>\nHigh density may cause lag on weak computers. It is recommended to test in \'Training battles\' or \'Topography\'\n\n<i>Default: 65</i>{/BODY}',
  'settings:interval': 'Update interval',
  'settings:intervalFormat': '{{value}} sec.',
  'settings:intervalTooltip': '{HEADER}Update interval{/HEADER}{BODY}How often the positions on the minimap will be updated (in seconds)\n\n<i>Default: 30</i>{/BODY}',
  'settings:showInfoMessages': 'Display information messages',
  'settings:showInfoMessagesTooltip': '{HEADER}Display information messages{/HEADER}{BODY}Enable to display information messages above the minimap.{/BODY}',
  'settings:reset': 'Reset',
  'settings:never': 'Never',
  'settings:onAlt': 'On Alt press',
  'settings:always': 'Always',
  'battleMessage:showArea': 'Displaying areas',
  'battleMessage:showMiniMarkers': 'Displaying positions',
  'battleMessage:showIdealMarker': 'Displaying the best marker',
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


