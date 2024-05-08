from Avatar import PlayerAvatar
from Vehicle import Vehicle
from helpers import dependency

from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.shared.utils import IHangarSpace

from ..common.ExceptionHandling import SendExceptionEvent
from ..common.OverrideLib import g_overrideLib


class WotHookEvents:
  __connectionMgr = dependency.descriptor(IConnectionManager) # type: IConnectionManager
  __hangarSpace = dependency.descriptor(IHangarSpace) # type: IHangarSpace

  def __init__(self):
    # DI
    self.__connectionMgr.onConnected += self.__onConnected
    self.__connectionMgr.onLoggedOn += self.__onLoggedOn
    self.__hangarSpace.onSpaceCreate += self.__onHangarSpaceCreate
    self.__hangarSpace.onSpaceDestroy += self.__onHangarSpaceDestroy

    self.listeners = {}
    
    self.onConnected = SendExceptionEvent()
    self.onLoggedOn = SendExceptionEvent()
    self.onHangarLoaded = SendExceptionEvent()
    self.onHangarDestroyed = SendExceptionEvent()
    self.Avatar_onBecomePlayer = SendExceptionEvent()
    self.Avatar_onBecomeNonPlayer = SendExceptionEvent()
    self.Vehicle_onEnterWorld = SendExceptionEvent()
    self.Vehicle_onHealthChanged = SendExceptionEvent()
    self.PlayerAvatar_onArenaPeriodChange = SendExceptionEvent()
   
  def __onConnected(self):
    self.onConnected()

  def __onLoggedOn(self, data):
    self.onLoggedOn(data)

  def __onHangarSpaceCreate(self):
    self.onHangarLoaded()

  def __onHangarSpaceDestroy(self, data):
    self.onHangarDestroyed(data)


wotHookEvents = WotHookEvents()

@g_overrideLib.registerEvent(PlayerAvatar, 'onBecomePlayer')
def onBecomePlayer(self, *a, **k):
  wotHookEvents.Avatar_onBecomePlayer(self, *a, **k)

@g_overrideLib.registerEvent(PlayerAvatar, 'onBecomeNonPlayer')
def onBecomeNonPlayer(self, *a, **k):
  wotHookEvents.Avatar_onBecomeNonPlayer(self, *a, **k)

@g_overrideLib.registerEvent(Vehicle, 'onEnterWorld')
def onEnterWorld(self, *a, **k):
  wotHookEvents.Vehicle_onEnterWorld(self, *a, **k)

@g_overrideLib.registerEvent(Vehicle, 'onHealthChanged')
def onHealthChanged(self, *a, **k):
  wotHookEvents.Vehicle_onHealthChanged(self, *a, **k)

@g_overrideLib.registerEvent(PlayerAvatar, '_PlayerAvatar__onArenaPeriodChange')
def onArenaPeriodChange(self, *a, **k):
  wotHookEvents.PlayerAvatar_onArenaPeriodChange(self, *a, **k)