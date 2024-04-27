from typing import List, Tuple  # noqa: F401

from Singleton import Singleton
from constants import BigWorld
from gui import SystemMessages
from notification.actions_handlers import NotificationsActionsHandlers

from .Logger import Logger
from .ExeptionHandling import withExceptionHandling
from ..main.WotHookEvents import wotHookEvents

logger = Logger.instance()

OPEN_POSITION_WOTSTAT_EVENT = 'OPEN_POSITION_WOTSTAT_EVENT:'

class Notifier(Singleton):

  @staticmethod
  def instance():
    return Notifier()
  
  __isHangarLoaded = False
  __showTimer = None
  __notificationQueue = [] # type: List[Tuple[str, SystemMessages.SM_TYPE, str, any, any]]
  
  def _singleton_init(self):
    wotHookEvents.onHangarLoaded += self.__onHangarLoaded
    wotHookEvents.onHangarDestroyed += self.__onHangarDestroyed

    self.old_handleAction = NotificationsActionsHandlers.handleAction
    NotificationsActionsHandlers.handleAction = self.events_handleAction

  @withExceptionHandling()
  def events_handleAction(self, obj, model, typeID, entityID, actionName):
    try:
      if actionName.startswith(OPEN_POSITION_WOTSTAT_EVENT):
        target = actionName.split(OPEN_POSITION_WOTSTAT_EVENT)[1]
        logger.info('Opening personal wotstat for %s' % target)
        BigWorld.wg_openWebBrowser(target)
      else:
        self.old_handleAction(obj, model, typeID, entityID, actionName)
    except:
      self.old_handleAction(obj, model, typeID, entityID, actionName)


  @withExceptionHandling()
  def showNotification(self, text, type=SystemMessages.SM_TYPE.Information, priority=None, messageData=None, savedData=None):
    # type: (str, SystemMessages.SM_TYPE, str, any, any) -> None
    
    if self.__isHangarLoaded:
      logger.info("Showing notification: [%s-%s] %s; Data: %s" % (type, priority, text, messageData))
      SystemMessages.pushMessage(text, type, priority, messageData, savedData)
    else:
      self.__notificationQueue.append((text, type, priority, messageData, savedData))


  def __onHangarLoaded(self):
    if self.__isHangarLoaded: return
    self.__isHangarLoaded = True

    def showNotifications():
      for notification in self.__notificationQueue:
        SystemMessages.pushMessage(notification[0], notification[1], notification[2], notification[3], notification[4])
      self.__notificationQueue = []
      self.__showTimer = None

    self.__showTimer = BigWorld.callback(1, showNotifications)

  def __onHangarDestroyed(self, *a, **k):
    self.__isHangarLoaded = False
    if self.__showTimer:
      BigWorld.cancelCallback(self.__showTimer)
      self.__showTimer = None