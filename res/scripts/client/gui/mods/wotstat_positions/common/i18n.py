# -*- coding: utf-8 -*-
from helpers import getClientLanguage
from Singleton import Singleton

from .Notifier import POSITION_WOTSTAT_EVENT_OPEN_URL

def highlight(text):
  return '<font color="#c5c5b4">%s</font>' % text

def openurl(text, url):
  return '<a href="event:%s%s">%s</a>' % (POSITION_WOTSTAT_EVENT_OPEN_URL, url, text)

RU = {
  'settings:modDisplayName': 'Мод «Позиции от WotStat»',
  'settings:showMinimapMarkers': 'Отображать позиции на миникарте',
  'settings:showMinimapMarkersTooltip': '{HEADER}Позиции эффективности{/HEADER}{BODY}На миникарте будут отображаться позиции эффективности с помощью маркеров{/BODY}',
  'settings:showIdealMarker': 'Отображать <b>наилучшую</b> позицию в 3D',
  'settings:showIdealTooltip': '{HEADER}Отображать <b>наилучшую</b> позицию в 3D{/HEADER}{BODY}На игровом поле будет отображаться маркер наилучшей позиции, если такая имеется{/BODY}',
  'settings:showAll3D': 'Отображать <b>все</b> позиции в 3D',
  'settings:showAll3DTooltip': '{HEADER}Отображение всех позиций в 3D{/HEADER}{BODY}На игровом поле будут отображаться <b>все</b> позиции 3D маркерами{/BODY}',
  'settings:showHeatmap': 'Отображать карту эффективности',
  'settings:showHeatmapTooltip': '{HEADER}Отображение тепловой карты <b>эффективных</b> позиций{/HEADER}{BODY}На миникарте будет отображаться тепловая карта <b>эффективных позиций</b>{/BODY}',
  'settings:showPopularHeatmap': 'Отображать карту популярности',
  'settings:showPopularHeatmapTooltip': '{HEADER}Отображение тепловой карты <b>популярных</b> позиций{/HEADER}{BODY}На миникарте будет отображаться тепловая карта <b>популярных позиций</b> (не обязательно эффективные){/BODY}',
  'settings:showSpotPoints': 'Отображать <b>основные</b> огневые рубежи',
  'settings:showSpotPointsTooltip': '{HEADER}Отображение <b>основных</b> огневых рубежей{/HEADER}{BODY}На миникарте будут отображаться <b>основные</b> огневые рубежи{/BODY}',
  'settings:showMiniSpotPoints': 'Отображать <b>второстепенные</b> огневые рубежи',
  'settings:showMiniSpotPointsTooltip': '{HEADER}Отображение <b>второстепенных</b> огневых рубежей{/HEADER}{BODY}На миникарте будут отображаться <b>второстепенные</b> огневые рубежи. Менее приоритетные чем основные{/BODY}',
  'settings:showEyeMarker': 'Отображать маркер стрельбы в 3D',
  'settings:showEyeMarkerTooltip': '{HEADER}Отображение маркер стрельбы в 3D{/HEADER}{BODY}На игровом поле будет отображаться маркеры стрельбы из ближайшего огневого рубежа, если он ближе 30 метров от танка{/BODY}',
  'settings:mouseSpotRays': 'Отображать направления стрельбы <b>рядом с курсором</b>',
  'settings:mouseSpotRaysTooltip': '{HEADER}Отображение направлений стрельбы <b>рядом с курсором</b>{/HEADER}{BODY}Линиями на миникарте будут отображаться направления стрельбы из огневого рубежа <b>рядом с курсором</b> (при наведение на миникарту){/BODY}',
  'settings:vehicleSpotRays': 'Отображать направления стрельбы <b>рядом с танком</b>',
  'settings:vehicleSpotRaysTooltip': '{HEADER}Отображение направлений стрельбы <b>рядом с танком</b>{/HEADER}{BODY}Линиями на миникарте будут отображаться направления стрельбы из огневого рубежа <b>рядом с танком</b>{/BODY}',
  'settings:heatmapLimit': 'Лимит количества точек на тепловых картах',
  'settings:heatmapLimitTooltip': '{HEADER}Лимит количества точек на тепловых картах{/HEADER}{BODY}Ограничивает максимальное количество клеточек на тепловой карте. Понизьте лимит, если у вас проседает FPS во время отображения тепловых карт.\nШаг тепловой карты не изменяется, с понижением лимита будут отображаться наиболее яркие области{/BODY}',
  'settings:interval': 'Интервал обновления',
  'settings:intervalFormat': '{{value}} сек.',
  'settings:intervalTooltip': '{HEADER}Интервал обновления{/HEADER}{BODY}Как часто будут обновляться позиции на миникарте (в секундах)\n\n<i>По умолчанию: 25/i>{/BODY}',
  'settings:showInfoMessages': 'Отображать информационные сообщения',
  'settings:showInfoMessagesTooltip': '{HEADER}Отображение информационных сообщений{/HEADER}{BODY}Включите, чтобы отображать информационные сообщения над миникартой.{/BODY}',
  'settings:reportHotkey': 'Сообщить об ошибке',
  'settings:reportHotkeyTooltip': '{HEADER}Сообщить об ошибке{/HEADER}{BODY}Нажмите эту клавишу в бою, если видите некорректную позицию{/BODY}',
  'settings:preferredServer': 'Сервер',
  'settings:preferredServerTooltip': '{HEADER}Сервер{/HEADER}{BODY}Выберите сервер к которому будет обращаться мод для запроса позиций.\n\n• Авто – будет использован основной сервер, после двух ошибок, мод перейдёт на резервный и запомнит этот выбор на текущую сессию.\n• OpenWG Network – прокси по наиболее продвинутому методу через мод OpenWG Network, <b>доступен только если мод установлен</b>\n• Основной – будет использоваться основной сервер\n• Резервный – будет использоваться резервный сервер\n• Резервный RU – будет использоваться резервный сервер на .ru домене\n• Резервный RU без SSL – будет использоваться резервный сервер на .ru домене по протоколу без шифрования (без SSL/TLS)\n• Телепорт МСК-1 – телепорт сервер OpenWG в Москву\n• Телепорт НБГ-1 – телепорт сервер OpenWG в Нюрнберг\n• Телепорт СПБ-1 – телепорт сервер OpenWG в Санкт-Петербург\n\n<i>Резервные RU сервера нужны для пользователей из России, у которых РКН блокирует всё остальное</i>{/BODY}',
  'settings:auto': 'Авто',
  'settings:main': 'Основной',
  'settings:alternative': 'Резервный',
  'settings:proxyRu': 'Резервный RU',
  'settings:proxyRuNoSsl': 'Резервный RU (без SSL)',
  'settings:teleportMsk1': 'Телепорт МСК-1',
  'settings:teleportNbg1': 'Телепорт НБГ-1',
  'settings:teleportSpb1': 'Телепорт СПБ-1',
  'settings:openwg.network': 'OpenWG Network',
  'settings:reset': 'Сбросить',
  'settings:never': 'Никогда',
  'settings:onAlt': 'По нажатию на Alt',
  'settings:mouseOver': 'При наведении курсора',
  'settings:always': 'Постоянно',
  'settings:small': 'Мало',
  'settings:medium': 'Средне',
  'settings:large': 'Много',
  'settings:unlimited': 'Безлимитно',
  'api.serverChanged': '\nСервер изменён на <b>%s</b>',
  'api.serverChangedHeader': 'Мод «Позиции от WotStat»',
  'battleMessage:showMinimapMarkers': 'Отображение позиций',
  'battleMessage:showIdealMarker': 'Отображение наилучшего маркера',
  'battleMessage:reportSended': 'Жалоба отправлена',
  'battleMessage:reportSendTimeLimit': 'Жалоба уже была отправлена',
  'hangarMessage:cannotResetFileLicense': 'Файловая лицензия не может быть сброшена. Пожалуйста, удалите файл лицензии вручную',
  'hangarMessage:licenseReset': 'Персональная лицензия сброшена',
  'updateMessage:header': 'Мод «Позиции от WotStat» успешно обновлён до версии {version}',
  'enterLicense.title': 'Активация лицензии «Позиции от WotStat»',
  'enterLicense.inputPlaceholder': 'Введите лицензионный ключ',
  'enterLicense.apply': 'Активировать',
  'enterLicense.serverError': 'Не удалось связаться с сервером активации, код ошибки: %s',
  'request.switchToAlternativeServer': 'Не удалось связаться с основным сервером, переключение на резервный до окончания игровой сессии',
  'greeting.serverError.title': 'Мод «Позиции от WotStat»',
  'greeting.serverError.message': 'Не удалось связаться с сервером, код ошибки: %s\n\nПопробуйте позже или обратитесь в службу поддержки в Discord: <a href=\'event:POSITION_WOTSTAT_EVENT_OPEN_URL:https://discord.gg/7K8W9JE6xU\'>@WotStat</a> или на электронную почту: support@wotstat.info',
  'releaseNotes:1.0.1': '• Адаптация для версии %s\n• Адаптация для режима %s\n• Исправлены незначительные ошибки' % (highlight('Lesta 1.27'), highlight('Натиск')),
  'releaseNotes:2.0.0': '<b>ВЕРСИЯ 2.0</b>\n\nГлобальное обновление, настоятельно рекомендуется %s с полным списком изменений.\n• Огневые рубежи\n• Направления для стрельбы\n• Тепловые карты\n• Новый алгоритм определения позиций' % (openurl('ознакомиться', 'https://positions.wotstat.info/whats-new-2')),
  'releaseNotes:2.0.1': '• Добавлена поддержка резервного сервера позиций. Он будет выбираться автоматически в случае недоступности основного. Принудительно переключить сервер можно в настройках мода',
  'releaseNotes:2.0.4': '• Добавлены два новых резервных сервера для игроков из России.\n• При ручном выборе сервера, теперь будет заново выводиться сообщение о лицензии.',
  'releaseNotes:2.0.5': '• Адаптация для версии %s\n• Улучшена система автообновления' % highlight('Lesta 1.37'),
  'releaseNotes:2.0.6': '• Добавлена поддержка резервных серверов через OpenWG Teleport для игроков из России (можно настроить в настройках).',
  'releaseNotes:2.0.7': '• В связи с участившимися блокировками от РКН, в качестве сервера по умолчанию на %s теперь используется %s. Вы всегда можете переключиться на основной или другие в настройках мода.' % (highlight('LESTA'), highlight('резервный RU сервер')),
}

EN = {
  'settings:modDisplayName': 'Positions by WotStat',
  'settings:showMinimapMarkers': 'Display positions on the minimap',
  'settings:showMinimapMarkersTooltip': '{HEADER}Efficiency positions{/HEADER}{BODY}Efficiency positions will be displayed on the minimap using markers{/BODY}',
  'settings:showIdealMarker': 'Display the <b>best</b> position in 3D',
  'settings:showIdealTooltip': '{HEADER}Display the <b>best</b> position in 3D{/HEADER}{BODY}The best position marker will be displayed on the battlefield if available{/BODY}',
  'settings:showAll3D': 'Display <b>all</b> positions in 3D',
  'settings:showAll3DTooltip': '{HEADER}Displaying all positions in 3D{/HEADER}{BODY}All positions will be displayed on the battlefield with 3D markers{/BODY}',
  'settings:showHeatmap': 'Show Efficiency Heatmap',
  'settings:showHeatmapTooltip': '{HEADER}Show a heatmap of <b>efficient</b> positions{/HEADER}{BODY}The minimap will display a heatmap of <b>efficient positions</b>{/BODY}',
  'settings:showPopularHeatmap': 'Show Popularity Heatmap',
  'settings:showPopularHeatmapTooltip': '{HEADER}Show a heatmap of <b>popular</b> positions{/HEADER}{BODY}The minimap will display a heatmap of <b>popular positions</b> (not necessarily efficient){/BODY}',
  'settings:showSpotPoints': 'Show <b>primary</b> firing positions',
  'settings:showSpotPointsTooltip': '{HEADER}Show <b>primary</b> firing positions{/HEADER}{BODY}The minimap will display the <b>primary</b> firing positions{/BODY}',
  'settings:showMiniSpotPoints': 'Show <b>secondary</b> firing positions',
  'settings:showMiniSpotPointsTooltip': '{HEADER}Show <b>secondary</b> firing positions{/HEADER}{BODY}The minimap will display the <b>secondary</b> firing positions. They are less prioritized than the primary ones{/BODY}',
  'settings:showEyeMarker': 'Show 3D shooting marker',
  'settings:showEyeMarkerTooltip': '{HEADER}Show 3D shooting marker{/HEADER}{BODY}On the battlefield, a shooting marker from the nearest firing position will be displayed if it is closer than 30 meters from the vehicle{/BODY}',
  'settings:mouseSpotRays': 'Show shooting directions <b>next to the cursor</b>',
  'settings:mouseSpotRaysTooltip': '{HEADER}Show shooting directions <b>next to the cursor</b>{/HEADER}{BODY}Lines on the minimap will display the shooting directions from the firing position <b>next to the cursor</b> (when hovering over the minimap){/BODY}',
  'settings:vehicleSpotRays': 'Show shooting directions <b>next to the vehicle</b>',
  'settings:vehicleSpotRaysTooltip': '{HEADER}Show shooting directions <b>next to the vehicle</b>{/HEADER}{BODY}Lines on the minimap will display the shooting directions from the firing position <b>next to the vehicle</b>{/BODY}',
  'settings:heatmapLimit': 'Heatmap cells limit',
  'settings:heatmapLimitTooltip': '{HEADER}Heatmap cells limit{/HEADER}{BODY}Limits the maximum number of cells in the heatmap. Lower the limit if your FPS drops while displaying heatmaps.\nThe heatmap granularity does not change; with a lower limit, only the brightest areas will be shown{/BODY}',
  'settings:interval': 'Update interval',
  'settings:intervalFormat': '{{value}} sec.',
  'settings:intervalTooltip': '{HEADER}Update interval{/HEADER}{BODY}How often the positions on the minimap will be updated (in seconds)\n\n<i>Default: 25</i>{/BODY}',
  'settings:showInfoMessages': 'Display information messages',
  'settings:showInfoMessagesTooltip': '{HEADER}Display information messages{/HEADER}{BODY}Enable to display information messages above the minimap.{/BODY}',
  'settings:reportHotkey': 'Report position',
  'settings:reportHotkeyTooltip': '{HEADER}Report an error{/HEADER}{BODY}Press this key in battle if you see an incorrect position{/BODY}',
  'settings:reset': 'Reset',
  'settings:never': 'Never',
  'settings:onAlt': 'On Alt press',
  'settings:mouseOver': 'On mouse over',
  'settings:always': 'Always',
  'settings:small': 'Few',
  'settings:medium': 'Moderate',
  'settings:large': 'Many',
  'settings:unlimited': 'Unlimited',
  'api.serverChanged': '\nServer changed to <b>%s</b>',
  'api.serverChangedHeader': 'Mod \'Positions by WotStat\'',
  'settings:preferredServer': 'Preferred server',
  'settings:preferredServerTooltip': '{HEADER}Preferred server{/HEADER}{BODY}Select the server to which the mod will connect to request positions.\n\n• Auto – the main server will be used, after two errors, the mod will switch to the backup server and remember this choice for the current session.\n• OpenWG Network – proxy via smart OpenWG Network mod, <b>available only if mod installed</b>\n• Backup – the backup server will be used\n• Main – the main server will be used\n• Backup – the backup server will be used\n• RU Proxy - the backup server on .ru domain\n• RU Proxy (no SSL) the backup server on .ru domain without secure (no SSL/TLS)\n• Teleport MSK-1 – OpenWG\'s teleport server to Moscow\n• Teleport NBG-1 – OpenWG\'s teleport server to Nuremberg\n• Teleport SPB-1 – OpenWG\'s teleport server to St. Petersburg\n\n <i>RU Proxy Backup servers are needed for Russian users because some providers block all others on the internet.</i>{/BODY}',
  'settings:auto': 'Auto',
  'settings:main': 'Main',
  'settings:alternative': 'Backup',
  'settings:proxyRu': 'RU Proxy',
  'settings:proxyRuNoSsl': 'RU Proxy (no SSL)',
  'settings:teleportMsk1': 'Teleport MSK-1',
  'settings:teleportNbg1': 'Teleport NBG-1',
  'settings:teleportSpb1': 'Teleport SPB-1',
  'settings:openwg.network': 'OpenWG Network',
  'battleMessage:showMinimapMarkers': 'Displaying positions',
  'battleMessage:showIdealMarker': 'Displaying the best marker',
  'battleMessage:reportSended': 'Report sent',
  'battleMessage:reportSendTimeLimit': 'Report has already been sent',
  'hangarMessage:cannotResetFileLicense': 'File license cannot be reset. Please delete the license file manually',
  'hangarMessage:licenseReset': 'Personal license reset',
  'updateMessage:header': 'The \'Positions by WotStat\' mod has been successfully updated to version {version}',
  'enterLicense.title': 'Activate Positions by WotStat',
  'enterLicense.inputPlaceholder': 'Enter the license key',
  'enterLicense.apply': 'Activate',
  'enterLicense.serverError': 'Failed to connect the activation server, error code: %s',
  'request.switchToAlternativeServer': 'Failed to connect to the main server, switching to the backup server until the end of the game session',
  'greeting.serverError.title': 'Mod \'Positions by WotStat\'',
  'greeting.serverError.message': 'Failed to connect the server, error code: %s\n\nTry again later or contact support in Discord: <a href=\'event:POSITION_WOTSTAT_EVENT_OPEN_URL:https://discord.gg/7K8W9JE6xU\'>@WotStat</a> or by email: support@wotstat.info',
  'releaseNotes:1.0.1': '• Adaptation for version %s\n• Adaptation for mode %s\n• Minor bugs fixed' % (highlight('Lesta 1.27'), highlight('Onslaught')),
  'releaseNotes:2.0.0': '<b>VERSION 2.0</b>\n\nGlobal update, it is strongly recommended read the %s.\n• Firing positions\n• Shooting directions\n• Heatmaps\n• Position detection algorithm' % (openurl('full list of changes', 'https://positions.wotstat.info/whats-new-2')),
  'releaseNotes:2.0.1': '• Added support for the backup positions server. It will be selected automatically if the main one is unavailable. You can force switch the server in the mod settings',
  'releaseNotes:2.0.4': '• Added two new backup servers for players from Russia.\n• When manually selecting a server, a license message will be displayed again.',
  'releaseNotes:2.0.5': '• Adaptation for version %s.\n• Improved auto-update system.' % highlight('Lesta 1.37'),
  'releaseNotes:2.0.6': '• Added support for backup servers via OpenWG Teleport for players from Russia.',
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
  
  def has(self, key):
    return key in self.current_localizations
  
  def translate(self, key):
    return self.t(key)
  
def t(key):
  return I18n.instance().t(key)

def has(key):
  return I18n.instance().has(key)
