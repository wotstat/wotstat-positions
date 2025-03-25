import BigWorld
from frameworks.wulf.gui_constants import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.framework.application import AppEntry

from ..common.i18n import t
from ..common.Logger import Logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from .LicenseManager import LicenseManager

ENTER_LICENSE_WINDOW = "WOTSTAT_POSITIONS_ENTER_LICENSE_WINDOW"

logger = Logger.instance()

class EnterLicenseWindow(AbstractWindowView):
  
  def __init__(self, ctx=None):
    super(EnterLicenseWindow, self).__init__(ctx)
    self.__licenseManager = ctx.get('licenseManager', None) # type: LicenseManager
  
  def onWindowClose(self):
    self.destroy()
  
  def py_enterLicense(self, license):
    if self.__licenseManager:
      self.__licenseManager.processEnterLicense(license)
    else:
      logger.error('No license manager')
    BigWorld.callback(0, lambda: self.onWindowClose())

  def py_t(self, key):
    return t(key)

def setup():
  settingsViewSettings = ViewSettings(
    ENTER_LICENSE_WINDOW,
    EnterLicenseWindow,
    "wotstat.positions.EnterLicenseWindow.swf",
    WindowLayer.TOP_WINDOW,
    None,
    ScopeTemplates.VIEW_SCOPE,
  )
  g_entitiesFactories.addSettings(settingsViewSettings)
  

def show(licenseManager):
  # type: (LicenseManager) -> None
  
  appLoader = dependency.instance(IAppLoader) # type: IAppLoader
  app = appLoader.getApp() # type: AppEntry
  app.loadView(SFViewLoadParams(ENTER_LICENSE_WINDOW), ctx={ 'licenseManager': licenseManager  })