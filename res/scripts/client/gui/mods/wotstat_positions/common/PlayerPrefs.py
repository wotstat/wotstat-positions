import os

import BigWorld
from external_strings_utils import unicode_from_utf8

from .ExceptionHandling import withExceptionHandling

_preferences_path = unicode_from_utf8(BigWorld.wg_getPreferencesFilePath())[1]
PREFERENCES_PATH = os.path.normpath(os.path.join(os.path.dirname(_preferences_path), 'mods', 'wotstat.positions'))

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
    
    try:
      with open(os.path.join(PREFERENCES_PATH, key), "r") as f:
        return f.read()
    except Exception as e:
      return default
    
  @staticmethod
  def set(key, value):
    # type: (str, Any) -> None
    
    try:
      _cache[key] = value
      with open(os.path.join(PREFERENCES_PATH, key), "w") as f:
        f.write(value)
    except Exception as e:
      pass

  @staticmethod
  def delete(key):
    # type: (str) -> None

    try:
      del _cache[key]
      os.remove(os.path.join(PREFERENCES_PATH, key))
    except Exception as e:
      pass