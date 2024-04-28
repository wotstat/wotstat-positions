import BigWorld

from .common.ServerLoggerBackend import ServerLoggerBackend
from .common.Logger import Logger, SimpleLoggerBackend
from .common.Config import Config
from .common.ModUpdater import ModUpdater
from .common.Settings import Settings, SettingsKeys
from .common.HotKeys import HotKeys
from .common.PlayerPrefs import PlayerPrefs
from .main.LifecycleStarter import LifecycleStarter
from .main.PositionRequester import PositionRequester
from .main.MarkerDrawer import MarkerDrawer
from .main.GreetingNotifier import GreetingNotifier


DEBUG_MODE = '{{DEBUG_MODE}}'
CONFIG_PATH = './mods/configs/wotstat.positions/config.cfg'

class PlayerPrefsKeys:
  LAST_VERSION = 'lastVersion'

logger = Logger.instance()
hotkeys = HotKeys.instance()
settings = Settings.instance()

class WotstatPositions(object):
  def __init__(self):
    logger.info("Starting WotStatPositions")

    self.config = Config(CONFIG_PATH)

    version = self.config.get("version")
    logger.info("Config loaded. Version: %s" % version)
  
    logger.setup([
      SimpleLoggerBackend(prefix="[MOD_WOTSTAT_POS]", minLevel="INFO" if not DEBUG_MODE else "DEBUG"),
      ServerLoggerBackend(url=self.config.get('lokiURL'),
                          prefix="[MOD_WOTSTAT_POS]",
                          source="mod_positions",
                          modVersion=version,
                          minLevel="INFO")
    ])

    updator = ModUpdater(modName="wotstat.positions",
                         currentVersion=version,
                         ghUrl=self.config.get('ghURL'))
    updator.updateToGitHubReleases(lambda status: logger.info("Update status: %s" % status))

    settings = Settings.instance()
    settings.onSettingsChanged += self.__onSettingsChanged
    settings.setup("wotstat_positions")

    drawer = MarkerDrawer()
    self.requseter = PositionRequester(serverUrl=self.config.get('serverURL'), drawer=drawer)
    self.markerDrawer = LifecycleStarter(self.requseter)
    
    GreetingNotifier(serverUrl=self.config.get('serverURL'))

    PlayerPrefs.set(PlayerPrefsKeys.LAST_VERSION, version)

    HotKeys.instance().onCommand += self.__onCommand

  def __onSettingsChanged(self, settings):
    hotkeys.updateCommandHotkey("sendReport", settings.get(SettingsKeys.REPORT_HOTKEY))
    logger.debug("Hotkeys commands updated")

  def __onCommand(self, command):
    if not settings.get(SettingsKeys.ENABLED): return
    if not getattr(BigWorld.player(), 'inWorld', False): return

    if command == 'sendReport':
      self.requseter.sendReport()
