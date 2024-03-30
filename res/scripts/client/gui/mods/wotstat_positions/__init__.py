from .common.ServerLoggerBackend import ServerLoggerBackend
from .common.Logger import Logger, SimpleLoggerBackend

class WotstatPositions(object):
  def __init__(self):

    # read config
  
    Logger.instance().setup([
      SimpleLoggerBackend(prefix="[MOD_WOTSTAT_POS]", minLevel="INFO" if not DEBUG_MODE else "DEBUG"),  # noqa: F821
      ServerLoggerBackend(url="https://loki.wotstat.info/loki/api/v1/push",
                          prefix="[MOD_WOTSTAT_POS]",
                          source="mod_positions",
                          modVersion="1.0.0",
                          minLevel="INFO")
    ])
