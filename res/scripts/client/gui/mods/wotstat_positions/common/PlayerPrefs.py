import os

import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from external_strings_utils import unicode_from_utf8

from .ExceptionHandling import withExceptionHandling, logCurrentException
from .Logger import Logger

_preferences_path = unicode_from_utf8(BigWorld.wg_getPreferencesFilePath())[1]
PREFERENCES_PATH = os.path.normpath(os.path.join(os.path.dirname(_preferences_path), 'mods', 'wotstat.positions'))

logger = Logger.instance()

@withExceptionHandling()
def setup():
  if not os.path.isdir(PREFERENCES_PATH):
    os.makedirs(PREFERENCES_PATH)

setup()

_cache = {}

class PlayerPrefs:

  @staticmethod
  def get(key, default=None):
    # type: (str, Any) -> str

    if key in _cache:
      return _cache[key]
    
    if not os.path.exists(PREFERENCES_PATH):
      return default
    
    file = os.path.join(PREFERENCES_PATH, key)

    if not os.path.exists(file):
      return default
    
    try:
      with open(file, "rb") as f:
        rawData = f.read()
        if '\x00' in rawData:
          raise Exception("File contains null bytes")
        
        text = rawData.decode('utf-8')

        _cache[key] = text
        return text
    except Exception as e:
      logCurrentException("Failed to read preference file: %s" % key, level='ERROR')
      return default
    
  @staticmethod
  def set(key, value):
    # type: (str, Any) -> None
    
    try:
      _cache[key] = value
      with open(os.path.join(PREFERENCES_PATH, key), "wb") as f:
        f.write(value.encode('utf-8'))
    except Exception as e:
      logCurrentException("Failed to write preference file: %s" % key)

  @staticmethod
  def delete(key):
    # type: (str) -> None

    try:
      if key in _cache:
        del _cache[key]
      os.remove(os.path.join(PREFERENCES_PATH, key))
    except Exception as e:
      LOG_CURRENT_EXCEPTION()
      pass