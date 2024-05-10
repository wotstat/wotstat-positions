from .WotHookEvents import wotHookEvents
from ..common.Logger import Logger
from ..common.Settings import Settings, SettingsKeys
from . import IPositionRequester  # noqa: F401
from .LicenseManager import LicenseManager  # noqa: F401

logger = Logger.instance()
settings = Settings.instance()

class LifecycleStarter(object):

  def __init__(self, requester, licenseManager):
    # type: (IPositionRequester, LicenseManager) -> None
    
    wotHookEvents.Avatar_onBecomePlayer += self.__onBecomePlayer
    wotHookEvents.Avatar_onBecomeNonPlayer += self.__onBecomeNonPlayer

    self.__requester = requester
    self.__licenseManager = licenseManager
    self.__enabled = True

  def disable(self):
    self.__enabled = False

  def enable(self):
    self.__enabled = True

      
  def __onBecomePlayer(self, *a, **k):
    logger.debug("On become player")
    if settings.get(SettingsKeys.ENABLED) and \
        self.__licenseManager.hasLicense() and \
        not self.__licenseManager.isBlocked() and \
        self.__enabled:
      self.__requester.start()

  def __onBecomeNonPlayer(self, *a, **k):
    logger.debug("On become non player")
    self.__requester.stop()