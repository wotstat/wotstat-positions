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

class Settings(Singleton):

  @staticmethod
  def instance():
      return Settings()
  
  defaultSettings = {
    'enabled': True,
    'updateInterval': 30,
    'showArea': ShowVariants.ALWAYS,
    'showMiniMarkers': ShowVariants.NEVER,
    'showIdealMarker': ShowVariants.ALWAYS,
    'areaChangeKey': [Keys.KEY_LCONTROL, Keys.KEY_P],
    'markersChangeKey': [Keys.KEY_LCONTROL, Keys.KEY_K],
    'idealChangeKey': [Keys.KEY_LCONTROL, Keys.KEY_L],
    'areaDensity': 20.0,
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
      template = {
        'modDisplayName': t('settings:modDisplayName'),
        'enabled': True,
        'column1': [
          templates.createDropdown(t('settings:showArea'), 'showArea', DropdownVariants, settings['showArea'], tooltip=t('settings:showAreaTooltip')),
          templates.createDropdown(t('settings:showMiniMarkers'), 'showMiniMarkers', DropdownVariants, settings['showMiniMarkers'], tooltip=t('settings:showMiniMarkersTooltip')),
          templates.createDropdown(t('settings:showIdealMarker'), 'showIdealMarker', DropdownVariants, settings['showIdealMarker'], tooltip=t('settings:showIdealTooltip')),
          templates.createHotkey(t('settings:areaChangeKey'), 'areaChangeKey', settings['areaChangeKey'], tooltip=t('settings:areaChangeKeyTooltip')),
          templates.createHotkey(t('settings:markersChangeKey'), 'markersChangeKey', settings['markersChangeKey'], tooltip=t('settings:markersChangeKeyTooltip')),
          templates.createHotkey(t('settings:idealChangeKey'), 'idealChangeKey', settings['idealChangeKey'], tooltip=t('settings:idealChangeKeyTooltip')),
        ],
        'column2': [
          templates.createSlider(t('settings:interval'), 'updateInterval', settings['updateInterval'], 5, 120, 5,
                                 tooltip=t('settings:intervalTooltip'), width=350, format=t('settings:intervalFormat')),
          # TODO: reset button, but not refresh UI
          # templates.createSlider(t('settings:interval'), 'updateInterval', settings['updateInterval'], 5, 120, 5,
          #                        tooltip=t('settings:intervalTooltip'), width=350, format=t('settings:intervalFormat'),
          #                        button=templates.createButton(width=70, height=25, offsetTop=-33, offsetLeft=-52, text=t('settings:reset'))),
          templates.createSlider(t('settings:areaDensity'), 'areaDensity', settings['areaDensity'], 5, 50, 5, tooltip=t('settings:areaDensityTooltip'), width=350),
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
