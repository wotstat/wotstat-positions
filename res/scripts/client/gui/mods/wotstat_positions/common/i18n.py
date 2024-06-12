# -*- coding: utf-8 -*-
from helpers import getClientLanguage
from Singleton import Singleton


def highlight(text):
  return '<font color="#c5c5b4">%s</font>' % text

RU = {
  'settings:modDisplayName': 'Мод «Позиции от WotStat»',
  'settings:showArea': 'Отображать области эффективности',
  'settings:showMinimapMarkers': 'Отображать позиции на миникарте',
  'settings:showIdealMarker': 'Отображать <b>наилучшую</b> позицию в 3D',
  'settings:showAll3D': 'Отображать <b>все</b> позиции в 3D',
  'settings:showAll3DTooltip': '{HEADER}Отображение всех позиций в 3D{/HEADER}{BODY}На игровом поле будут отображаться <b>все</b> позиции 3D маркерами{/BODY}',
  'settings:showAreaTooltip': '{HEADER}Области эффективности{/HEADER}{BODY}На миникарте будут отображаться области эффективности с помощью заливки точками{/BODY}',
  'settings:showMinimapMarkersTooltip': '{HEADER}Позиции эффективности{/HEADER}{BODY}На миникарте будут отображаться позиции эффективности с помощью маркеров{/BODY}',
  'settings:showIdealTooltip': '{HEADER}Отображать <b>наилучшую</b> позицию в 3D{/HEADER}{BODY}На игровом поле будет отображаться маркер наилучшей позиции, если такая имеется{/BODY}',
  'settings:areaDensity': 'Плотность точек областей',
  'settings:areaDensityTooltip': '{HEADER}Плотность точек областей{/HEADER}{BODY}Чем выше значение, тем больше точек будет отображаться на миникарте.\n\n<b>ВНИМАНИЕ!</b>\nВысокая плотность может вызывать подвисания на слабых компьютерах. Рекомендуется протестировать в «тренировочных боях» или «топографии»\n\n<i>По умолчанию: 65</i>{/BODY}',
  'settings:interval': 'Интервал обновления',
  'settings:intervalFormat': '{{value}} сек.',
  'settings:intervalTooltip': '{HEADER}Интервал обновления{/HEADER}{BODY}Как часто будут обновляться позиции на миникарте (в секундах)\n\n<i>По умолчанию: 30</i>{/BODY}',
  'settings:showInfoMessages': 'Отображать информационные сообщения',
  'settings:showInfoMessagesTooltip': '{HEADER}Отображение информационных сообщений{/HEADER}{BODY}Включите, чтобы отображать информационные сообщения над миникартой.{/BODY}',
  'settings:reportHotkey': 'Сообщить об ошибке',
  'settings:reportHotkeyTooltip': '{HEADER}Сообщить об ошибке{/HEADER}{BODY}Нажмите эту клавишу в бою, если видите некорректную позицию{/BODY}',
  'settings:reset': 'Сбросить',
  'settings:never': 'Никогда',
  'settings:onAlt': 'По нажанитю на Alt',
  'settings:always': 'Постоянно',
  'battleMessage:showArea': 'Отображение областей',
  'battleMessage:showMinimapMarkers': 'Отображение позиций',
  'battleMessage:showIdealMarker': 'Отображение наилучшего маркера',
  'battleMessage:reportSended': 'Жалоба отправлена',
  'battleMessage:reportSendTimeLimit': 'Жалоба уже была отправлена',
  'hangarMessage:cannotResetFileLicense': 'Файловая лицензия не может быть сброшена. Пожалуйста, удалите файл лицензии вручную',
  'hangarMessage:licenseReset': 'Персональная лицензия сброшена',
  'updateMessage:header': 'Новая версия «Позиции от WotStat»',
  'updateMessage:releaseNotesPrefix': 'Версия мода <b>v{version}</b> успешно установлена.\n\nЧто нового:',
  'releaseNotes:1.0.1': '• Адаптация для версии %s\n• Адаптация для режима %s\n• Исправлены незначительные ошибки' % (highlight('Lesta 1.27'), highlight('Натиск')),
}

EN = {
  'settings:modDisplayName': 'Positions by WotStat',
  'settings:showArea': 'Display efficiency areas',
  'settings:showMinimapMarkers': 'Display positions on the minimap',
  'settings:showIdealMarker': 'Display the <b>best</b> position in 3D',
  'settings:showAll3D': 'Display <b>all</b> positions in 3D',
  'settings:showAll3DTooltip': '{HEADER}Displaying all positions in 3D{/HEADER}{BODY}All positions will be displayed on the battlefield with 3D markers{/BODY}',
  'settings:showAreaTooltip': '{HEADER}Efficiency areas{/HEADER}{BODY}Efficiency areas will be displayed on the minimap using dotted fill{/BODY}',
  'settings:showMinimapMarkersTooltip': '{HEADER}Efficiency positions{/HEADER}{BODY}Efficiency positions will be displayed on the minimap using markers{/BODY}',
  'settings:showIdealTooltip': '{HEADER}Display the <b>best</b> position in 3D{/HEADER}{BODY}The best position marker will be displayed on the battlefield if available{/BODY}',
  'settings:areaDensity': 'Dot density of areas',
  'settings:areaDensityTooltip': '{HEADER}Dot density of areas{/HEADER}{BODY}The higher the value, the more dots will be displayed on the minimap.\n\n<b>WARNING!</b>\nHigh density may cause lag on weak computers. It is recommended to test in \'Training battles\' or \'Topography\'\n\n<i>Default: 65</i>{/BODY}',
  'settings:interval': 'Update interval',
  'settings:intervalFormat': '{{value}} sec.',
  'settings:intervalTooltip': '{HEADER}Update interval{/HEADER}{BODY}How often the positions on the minimap will be updated (in seconds)\n\n<i>Default: 30</i>{/BODY}',
  'settings:showInfoMessages': 'Display information messages',
  'settings:showInfoMessagesTooltip': '{HEADER}Display information messages{/HEADER}{BODY}Enable to display information messages above the minimap.{/BODY}',
  'settings:reportHotkey': 'Report position',
  'settings:reportHotkeyTooltip': '{HEADER}Report an error{/HEADER}{BODY}Press this key in battle if you see an incorrect position{/BODY}',
  'settings:reset': 'Reset',
  'settings:never': 'Never',
  'settings:onAlt': 'On Alt press',
  'settings:always': 'Always',
  'battleMessage:showArea': 'Displaying areas',
  'battleMessage:showMinimapMarkers': 'Displaying positions',
  'battleMessage:showIdealMarker': 'Displaying the best marker',
  'battleMessage:reportSended': 'Report sent',
  'battleMessage:reportSendTimeLimit': 'Report has already been sent',
  'hangarMessage:cannotResetFileLicense': 'File license cannot be reset. Please delete the license file manually',
  'hangarMessage:licenseReset': 'Personal license reset',
  'updateMessage:header': 'New version \'Positions by WotStat\'',
  'updateMessage:releaseNotesPrefix': 'Mod version <b>v{version}</b> installed.\n\nWhat\'s new:',
  'releaseNotes:1.0.1': '• Adaptation for version %s\n• Adaptation for mode %s\n• Minor bugs fixed' % (highlight('Lesta 1.27'), highlight('Onslaught')),
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


