# from gui.mods.wotstat_positions.test.messages import testNotification

import BigWorld
import json

from ..common.Logger import Logger
from ..common.Notifier import Notifier
from ..common.Config import Config
from .. import CONFIG_PATH

logger = Logger.instance() 
config = Config(CONFIG_PATH)

def testNotification(language='ru', license=None):
  def onResponse(data):
    if data.responseCode != 200:
      logger.error('Response status is not 200: %s' % data.responseCode)
      return

    body = data.body
    if not body:
      logger.error('Response body is empty')
      return
    
    parsed = json.loads(body)

    for msg in parsed.get('messages'):
      Notifier.instance().showNotificationFromData(msg)

  BigWorld.fetchURL(config.get('baseURL') + '/api/v1/test/messages/all?language=%s&license=%s' % (language, license), onResponse, 'GET', None, None)
