import BigWorld

from .WotHookEvents import wotHookEvents
from ..common.Logger import Logger

logger = Logger.instance()

class MarkerDrawer(object):

  def __init__(self):
    wotHookEvents.Avatar_onBecomePlayer += self.__onBecomePlayer
    wotHookEvents.Avatar_onBecomeNonPlayer += self.__onBecomeNonPlayer
      
  def __onBecomePlayer(self, *a, **k):
    logger.debug("On become player")

  def __onBecomeNonPlayer(self, *a, **k):
    logger.debug("On become non player")