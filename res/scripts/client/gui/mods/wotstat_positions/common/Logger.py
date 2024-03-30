from Singleton import Singleton

LEVELS_ORDER = {
  "DEBUG" : 0, 
  "INFO" : 1, 
  "WARN" : 2, 
  "ERROR" : 3, 
  "CRITICAL" : 4
}

def getLevelOrder(level):
  return LEVELS_ORDER[level] if level in LEVELS_ORDER else -1

class SimpleLoggerBackend:
  def __init__(self, prefix, minLevel="INFO"):
    self.prefix = prefix
    self.minLevelOrder = getLevelOrder(minLevel)

  def printlog(self, level, log):
    if getLevelOrder(level) >= self.minLevelOrder:
      print("%s[%s]: %s" % (self.prefix, level, str(log)))

class Logger(Singleton):

  @staticmethod
  def instance():
      return Logger()
  
  def _singleton_init(self):
    self.isSetup = False
    self.backends = []
    self.preSetupQueue = []

  def setup(self, backends):
    self.backends = backends
    self.isSetup = True

    for log in self.preSetupQueue:
      self.printlog(log[0], log[1])
    
    self.preSetupQueue = []

  def printlog(self, level, log):
    if not self.isSetup:
      self.preSetupQueue.append((level, log))
      return
    
    for backend in self.backends:
      backend.printlog(level, log)

  def debug(self, log):
    self.printlog("DEBUG", log)

  def info(self, log):
    self.printlog("INFO", log)

  def warn(self, log):
    self.printlog("WARN", log)

  def error(self, log):
    self.printlog("ERROR", log)

  def critical(self, log):
    self.printlog("CRITICAL", log)