from .WotHookEvents import wotHookEvents
from ..common.Logger import Logger
from . import IPositionRequester  # noqa: F401

logger = Logger.instance()

class LifecycleStarter(object):

  def __init__(self, requester):
    # type: (IPositionRequester) -> None
    
    wotHookEvents.Avatar_onBecomePlayer += self.__onBecomePlayer
    wotHookEvents.Avatar_onBecomeNonPlayer += self.__onBecomeNonPlayer

    self.__requester = requester
      
  def __onBecomePlayer(self, *a, **k):
    logger.debug("On become player")
    self.__requester.start()

  def __onBecomeNonPlayer(self, *a, **k):
    logger.debug("On become non player")
    self.__requester.stop()