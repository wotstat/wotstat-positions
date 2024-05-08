import collections

import BigWorld
from Singleton import Singleton
from gui import InputHandler
import Keys

from .ExceptionHandling import SendExceptionEvent

class SPECIAL_KEYS:
	KEY_ALT, KEY_CONTROL, KEY_SHIFT = range(-1, -4, -1)
	SPECIAL_TO_KEYS = {
		KEY_ALT: (Keys.KEY_LALT, Keys.KEY_RALT),
		KEY_CONTROL: (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL),
		KEY_SHIFT: (Keys.KEY_LSHIFT, Keys.KEY_RSHIFT),
	}
	KEYS_TO_SPECIAL = {}
	for special, keys in SPECIAL_TO_KEYS.items():
		for key in keys:
			KEYS_TO_SPECIAL[key] = special
	ALL = SPECIAL_TO_KEYS.keys()
	
class HotKeys(Singleton):

  @staticmethod
  def instance():
      return HotKeys()
  
  onCommand = SendExceptionEvent()

  def _singleton_init(self):
    self.__commands = {}
    InputHandler.g_instance.onKeyDown += self.__onKeyDown
  
  def updateCommandHotkey(self, command, keys):
    if not keys:
      return
    
    self.__commands[command] = self.__migrateKeys(keys)
  
  def __fireCommand(self, command):
     self.onCommand(command)

  def __onKeyDown(self, event):
    if not event.isKeyDown():
       return

    for command, keys in self.__commands.iteritems():
      if self.__checkKeySet(keys):
        BigWorld.callback(0, lambda: self.__fireCommand(command))
        return True
    return False
     
  def __checkKeySet(self, keys):
    if not keys:
      return False
    
    return all(map(self.__isKeyDown, keys))
	
  def __isKeyDown(self, key):
    if key in SPECIAL_KEYS.SPECIAL_TO_KEYS:
      if not any(map(BigWorld.isKeyDown, SPECIAL_KEYS.SPECIAL_TO_KEYS[key])):
        return False
    elif not BigWorld.isKeyDown(key):
      return False
    return True

  def __migrateKeys(self, keys):
    migrated = set()
    for key in keys:
      if isinstance(key, collections.Iterable):
        # Make flat set of keys
        migrated |= self.__migrateKeys(key)
      else:
        # Migrate special keys to virtual keys
        migrated.add(SPECIAL_KEYS.KEYS_TO_SPECIAL.get(key, key))
    return migrated