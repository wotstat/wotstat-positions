import BigWorld

from .WotHookEvents import wotHookEvents
from ..common.Logger import Logger

from . import IPositionDrawer

logger = Logger.instance()

class MarkerDrawer(IPositionDrawer):

  def __init__(self):
    pass

  def clear(self):
    logger.debug("Clearing markers")