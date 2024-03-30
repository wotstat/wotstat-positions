from .common.Logger import Logger

class WotstatPositions(object):
  def __init__(self):
    self.logger = Logger(prefix="[MOD_WOTSTAT_POS]", 
                         minLevel="INFO" if not DEBUG_MODE else "DEBUG",  # noqa: F821
                         onPrint=None)
    self.logger.info("INIT")
