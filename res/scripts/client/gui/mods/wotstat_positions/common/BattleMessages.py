from gui.Scaleform.genConsts.BATTLE_MESSAGES_CONSTS import BATTLE_MESSAGES_CONSTS
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.framework import WindowLayer
from gui.shared.personality import ServicesLocator
from gui.Scaleform.daapi.view.battle.shared.messages.fading_messages import _COLOR_TO_METHOD

from .Logger import Logger

logger = Logger.instance()

def showPlayerMessage(message, color=BATTLE_MESSAGES_CONSTS.COLOR_YELLOW):
  # type: (BATTLE_MESSAGES_CONSTS, str) -> None
  _showMessage(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, color, message)
  logger.debug('Show player message: %s' % message)

def showVehicleMessage(message, color=BATTLE_MESSAGES_CONSTS.COLOR_YELLOW):
  # type: (BATTLE_MESSAGES_CONSTS, str) -> None
  _showMessage(BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES, color, message)
  logger.debug('Show vehicle message: %s' % message)


def _showMessage(viewName, color, message):
  view = _getView(viewName)
  if not view: return logger.error('[ShowPlayerMessage]: view is None')

  fnName = _COLOR_TO_METHOD.get(color)
  fn = getattr(view, fnName, None)
  if not fn: return logger.error('[ShowPlayerMessage]: method is None')
  fn('key', message)


def _getView(name):
  # type: (str) -> object
  app = ServicesLocator.appLoader.getDefBattleApp()
  if not app: return logger.error('[BattleMessages]: BattleApp is None')

  battlePage = app.containerManager.getContainer(WindowLayer.VIEW).getView()
  if not battlePage: return logger.error('[BattleMessages]: BattlePage is None')

  return battlePage.components.get(name, None)