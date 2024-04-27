import os

import BigWorld
from external_strings_utils import unicode_from_utf8

from .ExeptionHandling import withExceptionHandling

_preferences_path = unicode_from_utf8(BigWorld.wg_getPreferencesFilePath())[1]
CONFIG_PATH = os.path.normpath(os.path.join(os.path.dirname(_preferences_path), 'mods', 'wotstat.positions'))

@withExceptionHandling()
def setup():
  if not os.path.isdir(CONFIG_PATH):
    os.makedirs(CONFIG_PATH)

setup()

class PlayerPrefs:

  @staticmethod
  def get(key, default=None):
    # type: (str, Any) -> Any
    
    if not os.path.exists(CONFIG_PATH):
      return default
    
    try:
      with open(os.path.join(CONFIG_PATH, key), "r") as f:
        return f.read()
    except Exception as e:
      return default
    
  @staticmethod
  def set(key, value):
    # type: (str, Any) -> None
    
    try:
      with open(os.path.join(CONFIG_PATH, key), "w") as f:
        f.write(value)
    except Exception as e:
      pass
