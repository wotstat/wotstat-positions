import Keys
from Singleton import Singleton

from .ExceptionHandling import SendExceptionEvent
from .Logger import Logger
from .i18n import t

logger = Logger.instance()

class ShowVariants:
  NEVER = 0
  ON_ALT = 1
  ALWAYS = 2

class OverlayShowVariants:
  NEVER = 0
  MOUSE_OVER = 1
  ON_ALT = 2
  ALWAYS = 3

class HeatmapLimitVariants:
  SMALL = 0
  MEDIUM = 1
  LARGE = 2
  UNLIMITED = 3

DropdownVariants = [t('settings:never'), t('settings:onAlt'), t('settings:always')]
OverlayDropdownVariants = [t('settings:never'), t('settings:mouseOver'), t('settings:onAlt'), t('settings:always')]
HeatmapLimitDropdownVariants = [t('settings:small'), t('settings:medium'), t('settings:large'), t('settings:unlimited')]

class SettingsKeys:
  ENABLED = 'enabled'
  UPDATE_INTERVAL = 'updateInterval'
  SHOW_MINIMAP_MARKERS = 'showMinimapMarkers'
  SHOW_IDEAL_MARKER = 'showIdealMarker'
  SHOW_ALL_MARKERS_3D = 'showAllMarkers3D'
  REPORT_HOTKEY = 'reportHotkey'
  SHOW_INFO_MESSAGES = 'showInfoMessages'
  SHOW_HEATMAP = 'showHeatmap'
  SHOW_POPULAR_HEATMAP = 'showPopularHeatmap'
  SHOW_SPOT_POINTS = 'showSpotPoints'
  SHOW_MINI_SPOT_POINTS = 'showMiniSpotPoints'
  SHOW_EYE_MARKERS = 'showEyeMarkers'
  VEHICLE_SPOT_RAYS = 'vehicleSpotRays'
  MOUSE_SPOT_RAYS = 'mouseSpotRays'
  HEATMAP_LIMIT = 'heatmapLimit'

class Settings(Singleton):

  @staticmethod
  def instance():
      return Settings()
  
  defaultSettings = {
    SettingsKeys.ENABLED: True,
    SettingsKeys.UPDATE_INTERVAL: 25,
    SettingsKeys.SHOW_ALL_MARKERS_3D: ShowVariants.ON_ALT,
    SettingsKeys.SHOW_MINIMAP_MARKERS: ShowVariants.ALWAYS,
    SettingsKeys.SHOW_IDEAL_MARKER: ShowVariants.ALWAYS,
    SettingsKeys.SHOW_INFO_MESSAGES: True,
    SettingsKeys.REPORT_HOTKEY: [Keys.KEY_F9],
    SettingsKeys.SHOW_HEATMAP: ShowVariants.ALWAYS,
    SettingsKeys.SHOW_POPULAR_HEATMAP: ShowVariants.ALWAYS,
    SettingsKeys.HEATMAP_LIMIT: HeatmapLimitVariants.UNLIMITED,
    SettingsKeys.SHOW_SPOT_POINTS: OverlayShowVariants.ALWAYS,
    SettingsKeys.SHOW_MINI_SPOT_POINTS: OverlayShowVariants.MOUSE_OVER,
    SettingsKeys.SHOW_EYE_MARKERS: ShowVariants.ON_ALT,
    SettingsKeys.VEHICLE_SPOT_RAYS: True,
    SettingsKeys.MOUSE_SPOT_RAYS: True,
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
          templates.createDropdown(t('settings:showIdealMarker'), SK.SHOW_IDEAL_MARKER, DropdownVariants, settings[SK.SHOW_IDEAL_MARKER], tooltip=t('settings:showIdealTooltip')),
          templates.createDropdown(t('settings:showAll3D'), SK.SHOW_ALL_MARKERS_3D, DropdownVariants, settings[SK.SHOW_ALL_MARKERS_3D], tooltip=t('settings:showAll3DTooltip')),
          templates.createDropdown(t('settings:showEyeMarker'), SK.SHOW_EYE_MARKERS, DropdownVariants, settings[SK.SHOW_EYE_MARKERS], tooltip=t('settings:showEyeMarkerTooltip')),
          templates.createDropdown(t('settings:showMinimapMarkers'), SK.SHOW_MINIMAP_MARKERS, DropdownVariants, settings[SK.SHOW_MINIMAP_MARKERS], tooltip=t('settings:showMinimapMarkersTooltip')),
          templates.createDropdown(t('settings:showHeatmap'), SK.SHOW_HEATMAP, DropdownVariants, settings[SK.SHOW_HEATMAP], tooltip=t('settings:showHeatmapTooltip')),
          templates.createDropdown(t('settings:showPopularHeatmap'), SK.SHOW_POPULAR_HEATMAP, DropdownVariants, settings[SK.SHOW_POPULAR_HEATMAP], tooltip=t('settings:showPopularHeatmapTooltip')),
          templates.createDropdown(t('settings:heatmapLimit'), SK.HEATMAP_LIMIT, HeatmapLimitDropdownVariants, settings[SK.HEATMAP_LIMIT], tooltip=t('settings:heatmapLimitTooltip')),
        ],
        'column2': [
          # TODO: reset button, but not refresh UI
          # templates.createSlider(t('settings:interval'), 'updateInterval', settings['updateInterval'], 5, 120, 5,
          #                        tooltip=t('settings:intervalTooltip'), width=350, format=t('settings:intervalFormat'),
          #                        button=templates.createButton(width=70, height=25, offsetTop=-33, offsetLeft=-52, text=t('settings:reset'))),
          templates.createDropdown(t('settings:showSpotPoints'), SK.SHOW_SPOT_POINTS, OverlayDropdownVariants, settings[SK.SHOW_SPOT_POINTS], tooltip=t('settings:showSpotPointsTooltip')),
          templates.createDropdown(t('settings:showMiniSpotPoints'), SK.SHOW_MINI_SPOT_POINTS, OverlayDropdownVariants, settings[SK.SHOW_MINI_SPOT_POINTS], tooltip=t('settings:showMiniSpotPointsTooltip')),
          templates.createCheckbox(t('settings:mouseSpotRays'), SK.MOUSE_SPOT_RAYS, settings[SK.MOUSE_SPOT_RAYS], tooltip=t('settings:mouseSpotRaysTooltip')),
          templates.createCheckbox(t('settings:vehicleSpotRays'), SK.VEHICLE_SPOT_RAYS, settings[SK.VEHICLE_SPOT_RAYS], tooltip=t('settings:vehicleSpotRaysTooltip')),
          
          templates.createSlider(t('settings:interval'), SK.UPDATE_INTERVAL, settings[SK.UPDATE_INTERVAL], 15, 120, 5,
                                 tooltip=t('settings:intervalTooltip'), width=350, format=t('settings:intervalFormat')),
          templates.createCheckbox(t('settings:showInfoMessages'), SK.SHOW_INFO_MESSAGES, settings[SK.SHOW_INFO_MESSAGES], tooltip=t('settings:showInfoMessagesTooltip')),
          templates.createEmpty(), templates.createEmpty(), templates.createEmpty(), templates.createEmpty(), templates.createEmpty(),
          templates.createEmpty(), templates.createEmpty(), templates.createEmpty(), templates.createEmpty(), templates.createEmpty(),
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
