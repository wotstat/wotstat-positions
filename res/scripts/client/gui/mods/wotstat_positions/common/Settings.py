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
  SHOW_MINI_MARKERS = 'showMiniMarkers'
  SHOW_IDEAL_MARKER = 'showIdealMarker'
  AREA_CHANGE_KEY = 'areaChangeKey'
  MARKERS_CHANGE_KEY = 'markersChangeKey'
  IDEAL_CHANGE_KEY = 'idealChangeKey'
  AREA_DENSITY = 'areaDensity'

class SettingsConstants:
  DENSITY_MIN = 0
  DENSITY_MAX = 100

class Settings(Singleton):

  @staticmethod
  def instance():
      return Settings()
  
  defaultSettings = {
    SettingsKeys.ENABLED: True,
    SettingsKeys.UPDATE_INTERVAL: 30,
    SettingsKeys.SHOW_AREA: ShowVariants.ON_ALT,
    SettingsKeys.SHOW_MINI_MARKERS: ShowVariants.ALWAYS,
    SettingsKeys.SHOW_IDEAL_MARKER: ShowVariants.ALWAYS,
    SettingsKeys.AREA_CHANGE_KEY: [Keys.KEY_LCONTROL, Keys.KEY_P],
    SettingsKeys.MARKERS_CHANGE_KEY: [Keys.KEY_LCONTROL, Keys.KEY_K],
    SettingsKeys.IDEAL_CHANGE_KEY: [Keys.KEY_LCONTROL, Keys.KEY_L],
    SettingsKeys.AREA_DENSITY: 65,
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
          templates.createDropdown(t('settings:showMiniMarkers'), SK.SHOW_MINI_MARKERS, DropdownVariants, settings[SK.SHOW_MINI_MARKERS], tooltip=t('settings:showMiniMarkersTooltip')),
          templates.createDropdown(t('settings:showIdealMarker'), SK.SHOW_IDEAL_MARKER, DropdownVariants, settings[SK.SHOW_IDEAL_MARKER], tooltip=t('settings:showIdealTooltip')),
          templates.createHotkey(t('settings:areaChangeKey'), SK.AREA_CHANGE_KEY, settings[SK.AREA_CHANGE_KEY], tooltip=t('settings:areaChangeKeyTooltip')),
          templates.createHotkey(t('settings:markersChangeKey'), SK.MARKERS_CHANGE_KEY, settings[SK.MARKERS_CHANGE_KEY], tooltip=t('settings:markersChangeKeyTooltip')),
          templates.createHotkey(t('settings:idealChangeKey'), SK.IDEAL_CHANGE_KEY, settings[SK.IDEAL_CHANGE_KEY], tooltip=t('settings:idealChangeKeyTooltip')),
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
