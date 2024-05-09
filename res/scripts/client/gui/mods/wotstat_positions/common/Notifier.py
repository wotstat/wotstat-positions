from typing import List, Tuple  # noqa: F401

from Singleton import Singleton
from constants import BigWorld
from gui import SystemMessages
from notification.actions_handlers import NotificationsActionsHandlers

from .Logger import Logger
from .ExceptionHandling import withExceptionHandling, SendExceptionEvent
from ..main.WotHookEvents import wotHookEvents

logger = Logger.instance()

POSITION_WOTSTAT_EVENT_PREFIX = 'POSITION_WOTSTAT_EVENT'
POSITION_WOTSTAT_EVENT_OPEN_URL = 'POSITION_WOTSTAT_EVENT_OPEN_URL:'

class Notifier(Singleton):

  @staticmethod
  def instance():
    return Notifier()
  
  __isHangarLoaded = False
  __showTimer = None
  __notificationQueue = [] # type: List[Tuple[str, SystemMessages.SM_TYPE, str, any, any]]
  
  onEvent = SendExceptionEvent()
  
  def _singleton_init(self):
    wotHookEvents.onHangarLoaded += self.__onHangarLoaded
    wotHookEvents.onHangarDestroyed += self.__onHangarDestroyed

    self.old_handleAction = NotificationsActionsHandlers.handleAction
    NotificationsActionsHandlers.handleAction = self.events_handleAction

  @withExceptionHandling()
  def events_handleAction(self, obj, model, typeID, entityID, actionName):
    try:
      if actionName.startswith(POSITION_WOTSTAT_EVENT_OPEN_URL):
        target = actionName.split(POSITION_WOTSTAT_EVENT_OPEN_URL)[1]
        logger.info('Opening personal wotstat for %s' % target)
        BigWorld.wg_openWebBrowser(target)
      elif actionName.startswith(POSITION_WOTSTAT_EVENT_PREFIX):
        self.onEvent(actionName)
        logger.info('Event %s' % actionName)
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

  @withExceptionHandling()
  def showNotificationFromData(self, message):
    # type: (dict) -> None
  
    text = message.get('text', None)
    if text is None: return

    self.showNotification(text, 
                  SystemMessages.SM_TYPE.of(message.get('type', 'Information')),
                  message.get('priority', None),
                  message.get('messageData', None),
                  message.get('savedData', None))

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