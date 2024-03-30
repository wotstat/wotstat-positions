import sys
from traceback import format_exception
import excepthook
from debug_utils import _addTagsToMsg, _makeMsgHeader, LOG_CURRENT_EXCEPTION, _src_file_trim_to, _g_logLock
from Event import Event

def __currentExeptionToString(tags=None, frame=1):
  msg = _makeMsgHeader(sys._getframe(frame)) + '\n'
  etype, value, tb = sys.exc_info()
  msg += ''.join(format_exception(etype, value, tb, None))
  with _g_logLock:
    line = ''
    line += '[EXCEPTION]' + _addTagsToMsg(tags, msg)
    extMsg = excepthook.extendedTracebackAsString(_src_file_trim_to, None, None, etype, value, tb)
    if extMsg:
      line += '[EXCEPTION]' + _addTagsToMsg(tags, extMsg)
  return line

def withExceptionHandling(logger=None):
  def wrapper(func):
    try:
      func()
    except:
      LOG_CURRENT_EXCEPTION()
      if logger:
        logger.exception(__currentExeptionToString())

  return wrapper
  
class SendExceptionEvent(Event):
  def __init__(self, logger=None):
    super(SendExceptionEvent, self).__init__(None)
    self.logger = logger

  def __call__(self, *args, **kwargs):
    for delegate in self[:]:
      try:
        delegate(*args, **kwargs)
      except:
        LOG_CURRENT_EXCEPTION()
        if self.logger:
          self.logger.exception(__currentExeptionToString())