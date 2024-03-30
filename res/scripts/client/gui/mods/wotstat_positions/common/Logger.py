
LEVELS_ORDER = {
  "DEBUG" : 0, 
  "INFO" : 1, 
  "WARN" : 2, 
  "ERROR" : 3, 
  "EXCEPTION" : 4
}

def getLevelOrder(level):
  return LEVELS_ORDER[level] if level in LEVELS_ORDER else -1

class Logger(object):
  def __init__(self, prefix, minLevel = "INFO", onPrint = None):
    self.prefix = prefix
    self.minLevelOrder = getLevelOrder(minLevel)
    self.onPrint = onPrint

  def printlog(self, level, log):
    if getLevelOrder(level) >= self.minLevelOrder:
      print("%s[%s]: %s" % (self.prefix, level, str(log)))

    if self.onPrint:
      self.onPrint(level, str(log))

  def debug(self, log):
    self.printlog("DEBUG", log)

  def info(self, log):
    self.printlog("INFO", log)

  def warn(self, log):
    self.printlog("WARN", log)

  def error(self, log):
    self.printlog("ERROR", log)

  def exception(self, log):
    self.printlog("EXCEPTION", log)