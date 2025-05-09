
import json

import BigWorld, Keys
from helpers import getClientLanguage
from gui import SystemMessages

from .WotHookEvents import wotHookEvents
from ..common.PlayerPrefs import PlayerPrefs
from ..common.Logger import Logger
from ..common.Notifier import Notifier
from ..common.ExceptionHandling import SendExceptionEvent, withExceptionHandling
from ..common.i18n import t
from ..common.Api import Api
from ..constants import POSITION_WOTSTAT_EVENT_ENTER_LICENSE, POSITION_WOTSTAT_EVENT_RESET_LICENSE
from .LicenseManager import LicenseManager, LicenseType # noqa: F401

LANGUAGE = getClientLanguage()
logger = Logger.instance()
notifier = Notifier.instance()


LAST_VISIBLE_GREETING_PLAYER_PREFS_KEY = 'lastVisibleGreeting'

class GreetingNotifier():

  onGameOpen = SendExceptionEvent()
  onFirstGameOpen = SendExceptionEvent()

  def __init__(self, api, licenseManager):
    # type: (Api, LicenseManager) -> None

    self.__waitForHangar = False
    self.__isFirstHangarLoad = True
    self.__api = api
    self.__licenseManager = licenseManager

    wotHookEvents.onLoggedOn += self.__onLoggedOn
    wotHookEvents.onHangarLoaded += self.__onHangarLoaded

    notifier.onEvent += self.__onEventClicked

  def __onLoggedOn(self, data):
    self.__waitForHangar = True

  def __onHangarLoaded(self):
    if not self.__waitForHangar: return
    self.__waitForHangar = False

    if self.__isFirstHangarLoad:
      self.__isFirstHangarLoad = False
      self.__firstGameOpenGreeting()
      
    self.__gameOpenGreeting()
  
  def __onEventClicked(self, event):
    # type: (str) -> None

    if event.startswith(POSITION_WOTSTAT_EVENT_ENTER_LICENSE):
      logger.info('Opening license')
      if BigWorld.isKeyDown(Keys.KEY_LALT) or BigWorld.isKeyDown(Keys.KEY_RALT):
        self.__licenseManager.requestInGameUI()
      else:
        self.__licenseManager.request()
    elif event.startswith(POSITION_WOTSTAT_EVENT_RESET_LICENSE):
      logger.info('Resetting license')
      self.__resetLicense()

  def __messageResponse(self, data):
    if data.responseCode != 200:
      logger.error('Greeting response status is not 200: %s' % data.responseCode)
      notifier.showNotification(t('greeting.serverError.message') % data.responseCode, SystemMessages.SM_TYPE.WarningHeader, None, {'header': t('greeting.serverError.title')})
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
    
    lastVisible = parsed.get('lastVisible', None)
    if lastVisible:
      PlayerPrefs.set(LAST_VISIBLE_GREETING_PLAYER_PREFS_KEY, lastVisible)

    message = parsed.get('message', None)
    if message:
      if 'text' in message:
        notifier.showNotificationFromData(message)
      else:
        logger.error('Message text is not found in response: %s' % parsed)
  
  @withExceptionHandling()
  def __getRequestParams(self):
    # type: () -> dict
    return {
      'name': BigWorld.player().name,
      'id': BigWorld.player().databaseID,
      'language': LANGUAGE,
      'lastVisible': PlayerPrefs.get(LAST_VISIBLE_GREETING_PLAYER_PREFS_KEY),
      'licenseType': self.__licenseManager.getLicenseType(),
      'license': self.__licenseManager.getLicense()
    }    

  # При первом открытии игры
  def __firstGameOpenGreeting(self):
    logger.debug('Requesting first greeting message')
    self.onFirstGameOpen()
    pass

  # При каждом перезаходе (например смена сервера)
  def __gameOpenGreeting(self):
    logger.debug('Requesting greeting message')
    self.onGameOpen()
    self.__api.greeting(self.__getRequestParams(), self.__messageResponse)

  # При каждом выходе в ангар 
  def __hangarOpenGreeting(self):
    logger.debug('Requesting hangar greeting message')
    pass

  def __resetLicense(self):
    licenseType = self.__licenseManager.getLicenseType()

    if licenseType == LicenseType.FILE:
      notifier.showNotification(t('hangarMessage:cannotResetFileLicense'), SystemMessages.SM_TYPE.Warning)
    elif licenseType != LicenseType.NONE:
      self.__licenseManager.resetLicense()
      notifier.showNotification(t('hangarMessage:licenseReset'), SystemMessages.SM_TYPE.Information)
      self.__api.afterReset(self.__getRequestParams(), self.__messageResponse)
        