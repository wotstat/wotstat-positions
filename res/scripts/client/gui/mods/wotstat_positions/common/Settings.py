import Keys
from Singleton import Singleton

from .ExeptionHandling import SendExceptionEvent
from .Logger import Logger
from .i18n import t

logger = Logger.instance()

class ShowVariants:
  NEVER = 0
  ON_ALT = 1
  ALWAYS = 2

DropdownVariants = [t('settings:never'), t('settings:onAlt'), t('settings:always')]

class SettingsKeys:
  ENABLED = 'enabled'
  UPDATE_INTERVAL = 'updateInterval'
  SHOW_AREA = 'showArea'
  SHOW_MINIMAP_MARKERS = 'showMinimapMarkers'
  SHOW_IDEAL_MARKER = 'showIdealMarker'
  SHOW_ALL_MARKERS_3D = 'showAllMarkers3D'
  REPORT_HOTKEY = 'reportHotkey'
  AREA_DENSITY = 'areaDensity'
  SHOW_INFO_MESSAGES = 'showInfoMessages'

class SettingsConstants:
  DENSITY_MIN = 0
  DENSITY_MAX = 100

class Settings(Singleton):

  @staticmethod
  def instance():
      return Settings()
  
  defaultSettings = {
    SettingsKeys.ENABLED: True,
    SettingsKeys.UPDATE_INTERVAL: 15,
    SettingsKeys.SHOW_AREA: ShowVariants.ON_ALT,
    SettingsKeys.SHOW_ALL_MARKERS_3D: ShowVariants.ON_ALT,
    SettingsKeys.SHOW_MINIMAP_MARKERS: ShowVariants.ALWAYS,
    SettingsKeys.SHOW_IDEAL_MARKER: ShowVariants.ALWAYS,
    SettingsKeys.AREA_DENSITY: 65,
    SettingsKeys.SHOW_INFO_MESSAGES: True,
    SettingsKeys.REPORT_HOTKEY: [Keys.KEY_F9],
  }

  settings = defaultSettings.copy()
  onSettingsChanged = SendExceptionEvent()

  def setup(self, name):
    self.name = name
    self.__settingsApiInit()
    self.__onModSettingsChanged(self.settings)
    logger.info('Settings initialized:\n%s' % str(self.settings))

  def get(self, name):
    return self.settings.get(name, None)
  
  def set(self, name, value):
    if name not in self.settings:
      logger.error('Setting %s not found' % name)

    self.settings[name] = value

    try:
      from gui.modsSettingsApi import g_modsSettingsApi
      g_modsSettingsApi.updateModSettings(self.name, self.settings)
    except:
      pass

  def __onModSettingsChanged(self, settings):
    self.settings = settings
    self.onSettingsChanged(settings)

  def __onModSettingsButtonPressed(self, varName, value):
    logger.info('Button pressed: %s; %s' % (varName, value))

  def __settingsApiInit(self):
    try:
      from gui.modsSettingsApi import g_modsSettingsApi, templates # type: ignore

      def onModSettingsChanged(name, settings):
        if name == self.name:
          self.__onModSettingsChanged(settings)

      def onButtonClicked(name, varName, value):
        if name == self.name:
          self.__onModSettingsButtonPressed(varName, value)

      settings = self.settings
      SK = SettingsKeys
      template = {
        'modDisplayName': t('settings:modDisplayName'),
        'enabled': True,
        'column1': [
          templates.createDropdown(t('settings:showArea'), SK.SHOW_AREA, DropdownVariants, settings[SK.SHOW_AREA], tooltip=t('settings:showAreaTooltip')),
          templates.createDropdown(t('settings:showMinimapMarkers'), SK.SHOW_MINIMAP_MARKERS, DropdownVariants, settings[SK.SHOW_MINIMAP_MARKERS], tooltip=t('settings:showMinimapMarkersTooltip')),
          templates.createDropdown(t('settings:showIdealMarker'), SK.SHOW_IDEAL_MARKER, DropdownVariants, settings[SK.SHOW_IDEAL_MARKER], tooltip=t('settings:showIdealTooltip')),
          templates.createDropdown(t('settings:showAll3D'), SK.SHOW_ALL_MARKERS_3D, DropdownVariants, settings[SK.SHOW_ALL_MARKERS_3D], tooltip=t('settings:showAll3DTooltip')),
        ],
        'column2': [
          templates.createSlider(t('settings:interval'), SK.UPDATE_INTERVAL, settings[SK.UPDATE_INTERVAL], 5, 120, 5,
                                 tooltip=t('settings:intervalTooltip'), width=350, format=t('settings:intervalFormat')),
          # TODO: reset button, but not refresh UI
          # templates.createSlider(t('settings:interval'), 'updateInterval', settings['updateInterval'], 5, 120, 5,
          #                        tooltip=t('settings:intervalTooltip'), width=350, format=t('settings:intervalFormat'),
          #                        button=templates.createButton(width=70, height=25, offsetTop=-33, offsetLeft=-52, text=t('settings:reset'))),
          templates.createSlider(t('settings:areaDensity'), SK.AREA_DENSITY, settings[SK.AREA_DENSITY], 
                                 SettingsConstants.DENSITY_MIN, SettingsConstants.DENSITY_MAX, 5, tooltip=t('settings:areaDensityTooltip'), width=350),
          templates.createCheckbox(t('settings:showInfoMessages'), SK.SHOW_INFO_MESSAGES, settings[SK.SHOW_INFO_MESSAGES], tooltip=t('settings:showInfoMessagesTooltip')),
          templates.createEmpty(), templates.createEmpty(), templates.createEmpty(), templates.createEmpty(),
          templates.createHotkey(t('settings:reportHotkey'), SK.REPORT_HOTKEY, settings[SK.REPORT_HOTKEY], tooltip=t('settings:reportHotkeyTooltip')),        
        ]
      }

      savedSettings = g_modsSettingsApi.getModSettings(self.name, template)
      if savedSettings:
        self.settings = savedSettings
        g_modsSettingsApi.registerCallback(self.name, onModSettingsChanged, onButtonClicked)
      else:
        self.settings = g_modsSettingsApi.setModTemplate(self.name, template, onModSettingsChanged, onButtonClicked)
    except:
      logger.info('Settings: modsSettingsApi not found')
