import BigWorld

from .common.ServerLoggerBackend import ServerLoggerBackend
from .common.Logger import Logger, SimpleLoggerBackend
from .common.Config import Config
from .common.ModUpdator import ModUpdator
from .common.Settings import Settings, SettingsKeys, ShowVariants
from .common.HotKeys import HotKeys
from .common.i18n import t
from .common.BattleMessages import showPlayerMessage
from .main.LifecycleStarter import LifecycleStarter
from .main.PositionRequester import PositionRequester
from .main.MarkerDrawer import MarkerDrawer


DEBUG_MODE = '{{DEBUG_MODE}}'
CONFIG_PATH = './mods/configs/wotstat.positions/config.cfg'

logger = Logger.instance()
hotkeys = HotKeys.instance()
settings = Settings.instance()

class WotstatPositions(object):
  def __init__(self):
    logger.debug("Starting WotStatPositions")

    self.config = Config(CONFIG_PATH)

    version = self.config.get("version")
    logger.debug("Config loaded. Version: %s" % version)
  
    logger.setup([
      SimpleLoggerBackend(prefix="[MOD_WOTSTAT_POS]", minLevel="INFO" if not DEBUG_MODE else "DEBUG"),
      ServerLoggerBackend(url=self.config.get('lokiURL'),
                          prefix="[MOD_WOTSTAT_POS]",
                          source="mod_positions",
                          modVersion=version,
                          minLevel="INFO")
    ])

    updator = ModUpdator(modName="wotstat.positions",
                         currentVersion=version,
                         ghUrl=self.config.get('ghURL'))
    updator.updateToGitHubReleases(lambda status: logger.info("Update status: %s" % status))

    settings = Settings.instance()
    settings.onSettingsChanged += self.__onSettingsChanged
    settings.setup("wotstat_positions")

    drawer = MarkerDrawer()
    requseter = PositionRequester(serverUrl=self.config.get('serverURL'), drawer=drawer)
    self.markerDrawer = LifecycleStarter(requseter)

    HotKeys.instance().onCommand += self.__onCommand

  def __onSettingsChanged(self, settings):
    hotkeys.updateCommandHotkey("toggleArea", settings.get(SettingsKeys.AREA_CHANGE_KEY))
    hotkeys.updateCommandHotkey("toggleMarkers", settings.get(SettingsKeys.MARKERS_CHANGE_KEY))
    hotkeys.updateCommandHotkey("toggleIdealMarker", settings.get(SettingsKeys.IDEAL_CHANGE_KEY))

    logger.debug("Hotkeys commands updated")

  def __onCommand(self, command):
    if not settings.get(SettingsKeys.ENABLED): return
    if not getattr(BigWorld.player(), 'inWorld', False): return

    def change(key):
      current = settings.get(key)
      target = {
        ShowVariants.NEVER: ShowVariants.ON_ALT,
        ShowVariants.ON_ALT: ShowVariants.ALWAYS,
        ShowVariants.ALWAYS: ShowVariants.NEVER,
      }[current]
      settings.set(key, target)

      nameByKey = {
        ShowVariants.ON_ALT: 'settings:onAlt',
        ShowVariants.ALWAYS: 'settings:always',
        ShowVariants.NEVER: 'settings:never',
      }

      showPlayerMessage('%s: %s' % (t('battleMessage:%s' % key), t(nameByKey[target])))
      logger.info('Change setting %s to %s' % (key, target))
      
    settingsByCommand = {
      'toggleArea': 'showArea',
      'toggleMarkers': 'showMiniMarkers',
      'toggleIdealMarker': 'showIdealMarker',
    }

    if command in settingsByCommand:
      change(settingsByCommand[command])