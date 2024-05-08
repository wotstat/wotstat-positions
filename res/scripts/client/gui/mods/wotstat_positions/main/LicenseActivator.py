import websocket
import uuid
import json

import BigWorld
from helpers import getClientLanguage
from gui import SystemMessages

from ..common.Logger import Logger
from ..common.Notifier import Notifier

LANGUAGE = getClientLanguage()

logger = Logger.instance()
notifier = Notifier.instance()

class LicenseActivator(object):

  uuid = str(uuid.uuid4())
  client = None

  def __init__(self, url):
    self.__wsUrl = url.replace('http://', 'ws://').replace('https://', 'wss://') + '/api/v1/activation/wot'
    self.__activatorPage = '%s/request-licence-key?requestId=' % url

  def request(self):
    logger.info("Requesting license with: %s" % self.uuid)

    if not self.client:
      self.client = websocket.Client()
      listener = self.client.listener # type: websocket.Listener
      listener.onOpened += self.__onWebsocketOpened
      listener.onClosed += self.__onWebsocketClosed
      listener.onMessage += self.__onWebsocketMessage

    BigWorld.wg_openWebBrowser(self.__activatorPage + self.uuid)
    targetUrl = '%s/%s?language=%s' % (self.__wsUrl, self.uuid, LANGUAGE)
    if self.client.status != websocket.ConnectionStatus.Opened or self.client.status != websocket.ConnectionStatus.Opening:
      self.client.open(targetUrl, reconnect=True)


  def __onWebsocketOpened(self, server):
    logger.info('onWebsocketOpened')
    
  def __onWebsocketClosed(self, server, code, reason):
    logger.info('onWebsocketClosed %s %s %s' % (str(server), str(code), str(reason)))

  def __onWebsocketMessage(self, code, payload):
    logger.info('onWebsocketMessage %s %s' % (str(code), str(payload)))
    if code == websocket.OpCode.Text:
      try:
        data = json.loads(payload)
        key = data.get('key', None)
        if key:
          logger.info('Set key: %s' % key)

          self.client.sendText('ACTIVATED')
          self.client.close()
          self.uuid = str(uuid.uuid4())
          

        message = data.get('message', None)
        if message and message.get('text', None):
          notifier.showNotification(message.get('text'), 
                        SystemMessages.SM_TYPE.of(message.get('type', 'Information')),
                        message.get('priority', None),
                        message.get('messageData', None),
                        message.get('savedData', None))

      except:
        logger.error('Failed to parse JSON from payload %s' % payload)
      