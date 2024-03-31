from .common.ServerLoggerBackend import ServerLoggerBackend
from .common.Logger import Logger, SimpleLoggerBackend
from .common.Config import Config
from .main.LifecycleStarter import LifecycleStarter
from .main.PositionRequester import PositionRequester
from .main.MarkerDrawer import MarkerDrawer

DEBUG_MODE = '{{DEBUG_MODE}}'
CONFIG_PATH = './mods/configs/wotstat_positions/config.cfg'

class WotstatPositions(object):
  def __init__(self):
    logger = Logger.instance()

    logger.debug("Starting WotStatPositions")

    self.config = Config(CONFIG_PATH)

    logger.debug("Config loaded. Version: %s" % self.config.get("version"))
  
    logger.setup([
      SimpleLoggerBackend(prefix="[MOD_WOTSTAT_POS]", minLevel="INFO" if not DEBUG_MODE else "DEBUG"),
      ServerLoggerBackend(url=self.config.get('lokiURL'),
                          prefix="[MOD_WOTSTAT_POS]",
                          source="mod_positions",
                          modVersion=self.config.get('version'),
                          minLevel="INFO")
    ])

    logger.debug("Logger setup done")

    drawer = MarkerDrawer()
    requseter = PositionRequester(self.config.get('serverURL'), drawer)
    self.markerDrawer = LifecycleStarter(requseter)

    logger.debug("MarkerDrawer created")
