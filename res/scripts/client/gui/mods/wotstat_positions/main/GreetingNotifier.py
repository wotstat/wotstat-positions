
import json
from functools import partial

import BigWorld
from helpers import getClientLanguage
from gui import SystemMessages

from .WotHookEvents import wotHookEvents
from ..common.PlayerPrefs import PlayerPrefs
from ..common.Logger import Logger
from ..common.Notifier import Notifier
from ..common.ExeptionHandling import withExceptionHandling

LANGUAGE = getClientLanguage()
logger = Logger.instance()
notifier = Notifier.instance()


class GreetingNotifier():

  def __init__(self, serverUrl):
    self.__waitForHangar = False
    self.__isFirstHangarLoad = True
    self.__serverUrl = serverUrl

    wotHookEvents.onLoggedOn += self.__onLoggedOn
    wotHookEvents.onHangarLoaded += self.__onHangarLoaded

  def __onLoggedOn(self, data):
    self.__waitForHangar = True

  def __onHangarLoaded(self):
    if not self.__waitForHangar: return
    self.__waitForHangar = False

    if self.__isFirstHangarLoad:
      self.__isFirstHangarLoad = False
      self.__firstGameOpenGreeting()
      
    self.__gameOpenGreeting()

  @withExceptionHandling()
  def __getQueryPostfix(self, visibleKey):
    query = {
      'name': BigWorld.player().name,
      'id': BigWorld.player().databaseID,
      'language': LANGUAGE,
      'lastVisible': PlayerPrefs.get(visibleKey),
    }
    
    return '&'.join(['%s=%s' % (k, v) for k, v in query.items()])
  
  def __messageResponse(self, visibleKey, data):
    if data.responseCode != 200:
      logger.error('Greeting response status is not 200: %s' % data.responseCode)
      return
    
    body = data.body
    if not body:
      logger.error('Response body is empty')
      return
    
    parsed = None
    try:
      parsed = json.loads(body)
    except ValueError:
      logger.error('Response body is not a valid JSON: %s' % body)
      return
    

    if 'message' not in parsed:
      logger.error('Response body has no message')
      return
    
    if 'lastVisible' in parsed:
      PlayerPrefs.set(visibleKey, parsed['lastVisible'])

    message = parsed['message']

    if 'text' not in message:
      logger.error('Response body has no message text')
      return
    
    notifier.showNotification(message['text'], 
                              SystemMessages.SM_TYPE.of(message.get('type', 'Information')),
                              message.get('priority', None),
                              message.get('messageData', None),
                              message.get('savedData', None))
    
    
  # При первом открытии игры
  def __firstGameOpenGreeting(self):
    logger.debug('Requesting first greeting message')
    pass

  # При каждом перезаходе (например смена сервера)
  def __gameOpenGreeting(self):
    logger.debug('Requesting greeting message')
    visibleKey = 'lastVisibleGreeting'
    url = '/greeting?' + self.__getQueryPostfix(visibleKey)
    BigWorld.fetchURL(self.__serverUrl + url, partial(self.__messageResponse, visibleKey), method='GET')

  # При каждом выходе в ангар 
  def __hangarOpenGreeting(self):
    logger.debug('Requesting hangar greeting message')
    pass