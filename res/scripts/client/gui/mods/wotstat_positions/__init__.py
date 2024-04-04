from .common.ServerLoggerBackend import ServerLoggerBackend
from .common.Logger import Logger, SimpleLoggerBackend
from .common.Config import Config
from .common.ModUpdator import ModUpdator
from .common.Settings import Settings
from .common.HotKeys import HotKeys
from .main.LifecycleStarter import LifecycleStarter
from .main.PositionRequester import PositionRequester
from .main.MarkerDrawer import MarkerDrawer

DEBUG_MODE = '{{DEBUG_MODE}}'
CONFIG_PATH = './mods/configs/wotstat.positions/config.cfg'

class WotstatPositions(object):
  def __init__(self):
    logger = Logger.instance()

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
    settings.onSettingsChanged += self.onSettingsChanged
    settings.setup("wotstat_positions")

    drawer = MarkerDrawer()
    requseter = PositionRequester(serverUrl=self.config.get('serverURL'),
                                  requestPeriod=5,
                                  drawer=drawer)
    self.markerDrawer = LifecycleStarter(requseter)

    logger.debug("MarkerDrawer created")

  def onSettingsChanged(self, settings):
    hotkeys = HotKeys.instance()
    settings = Settings.instance()

    hotkeys.updateCommandHotkey("toggleArea", settings.get("areaChangeKey"))
    hotkeys.updateCommandHotkey("toggleMarkers", settings.get("markersChangeKey"))
    hotkeys.updateCommandHotkey("toggleIdealMarker", settings.get("idealChangeKey"))
