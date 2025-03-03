from typing import Any, List, Tuple, Dict # noqa: F401

import BigWorld
from gui.shared.personality import ServicesLocator
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager # noqa: F401
from gui.Scaleform.daapi.view.battle.shared.minimap.component import MinimapComponent # noqa: F401
from gui.Scaleform.daapi.view.battle.shared.minimap import plugins
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import ENTRY_SYMBOL_NAME, CONTAINER_NAME, TRANSFORM_FLAG, clampMinimapSizeIndex
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import CommonMarkerType, MARKER_SYMBOL_NAME
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from frameworks.wulf import WindowLayer
from Math import Vector2, Vector3, Vector4, createTranslationMatrix
from gui.battle_control import minimap_utils
from helpers.dependency import instance

from ..common.Logger import Logger
from ..common.Settings import Settings
from ..common.ExceptionHandling import withExceptionHandling
from . import IPositionDrawer, PositionPoint, Spots # noqa: F401

logger = Logger.instance()
settings = Settings.instance()

CULL_DISTANCE = 1800
MIN_SCALE = 50.0
BOUNDS = Vector4(30, 30, 90, -15)
INNER_BOUNDS = Vector4(15, 15, 70, -35)
BOUNDS_MIN_SCALE = Vector2(1.0, 0.8)
MIN_Y_OFFSET = 1.2
MAX_Y_OFFSET = 2.2
DISTANCE_FOR_MIN_Y_OFFSET = 400
MAX_Y_BOOST = 1.4
BOOST_START = 120

MIN_AREA_STEP = 10
MAX_AREA_STEP = 40

class MarkerDrawer(IPositionDrawer):
  __minimap = None # type: MinimapComponent
  __markerManager = None # type: MarkersManager

  __markers = {
    ENTRY_SYMBOL_NAME.LOCATION_MARKER: [],
    ENTRY_SYMBOL_NAME.NAVIGATION_POINT_MARKER: [],
    ENTRY_SYMBOL_NAME.VEHICLE: []
  } # type: Dict[str, List[Marker]]
  __freeMarkers = {
    ENTRY_SYMBOL_NAME.LOCATION_MARKER: [],
    ENTRY_SYMBOL_NAME.NAVIGATION_POINT_MARKER: [],
    ENTRY_SYMBOL_NAME.VEHICLE: []
  } # type: Dict[str, List[Marker]]

  __worldMarkers = {
    MARKER_SYMBOL_NAME.NAVIGATION_MARKER: [],
    MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER: []
  } # type: Dict[str, List[WorldMarker]]
  __freeWorldMarkers = {
    MARKER_SYMBOL_NAME.NAVIGATION_MARKER: [],
    MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER: []
  } # type: Dict[str, List[WorldMarker]]


  def __init__(self):
    self.__minimap = None
    self.__markerManager = None

  def __getMarkerManager(self):
    # type: () -> MarkersManager | None
    battle = ServicesLocator.appLoader.getDefBattleApp()
    if not battle: return None

    if not battle.containerManager: return None
    
    view = battle.containerManager.getContainer(WindowLayer.VIEW).getView()
    if not view: return None
    if not view._external: return None
    if len(view._external) < 2: return None
    
    return view._external[1]
  
  def __getMinimap(self):
    # type: () -> MinimapComponent | None
    battle = ServicesLocator.appLoader.getDefBattleApp()
    if not battle: return None
    
    view = battle.containerManager.getContainer(WindowLayer.VIEW).getView()
    if not view: return None
    
    return view.components.get(BATTLE_VIEW_ALIASES.MINIMAP, None)

  @withExceptionHandling()
  def isReady(self):
    if not self.__markerManager or not self.__markerManager.isCreated():
      manager = self.__getMarkerManager()
      if not manager: return False
      
      if not hasattr(manager, '_MarkersManager__canvas'): return False
      if not manager._MarkersManager__canvas: return False

    if self.__markerManager and self.__markerManager.isCreated():
      if not hasattr(self.__markerManager, '_MarkersManager__canvas'): return False
      if not self.__markerManager._MarkersManager__canvas: return False


    if not self.__minimap or not self.__minimap.isCreated():
      minimap = self.__getMinimap()
      if not minimap: return False

    if self.__minimap and self.__minimap.isCreated():
      if not hasattr(self.__minimap, '_MinimapComponent__component'): return False
      if not self.__minimap._MinimapComponent__component: return False

    return True

  @withExceptionHandling()
  def drawPoints(self, points):
    # type: (List[PositionPoint]) -> None
    
    for point in points:
      position = point.position
      efficiency = point.efficiency
      marker = self.__createMarker((position[0], position[1]), ENTRY_SYMBOL_NAME.LOCATION_MARKER, CONTAINER_NAME.ICONS)
      if marker:
        marker.setScale(efficiency)

  @withExceptionHandling()
  def drawIdealPoints(self, points):
    # type: (List[PositionPoint]) -> None

    for point in points:
      position = point.position
      markerMinimap = self.__createMarker(position, ENTRY_SYMBOL_NAME.NAVIGATION_POINT_MARKER, CONTAINER_NAME.ICONS)
      if markerMinimap:
        markerMinimap.setScale(1)
  
  eyeMarkers = []
  @withExceptionHandling()
  def drawEyeMarkers(self, points):
    # type: (List[Spots.Point]) -> None
    
    for marker in self.eyeMarkers:
      self.clearMarker(marker)
      
    self.eyeMarkers = []
    
    for point in points:
      for ray in point.hits:
        position = [ray[0], ray[1]]
        marker = self.__createWorldMarker(position, -1, MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER)
        marker.invokeMarker('init', ['eye', 0, 720, -1, '', 'green'])
        marker.setMinScale(30)
        self.eyeMarkers.append(marker)
  
  @withExceptionHandling()
  def drawMarkers3D(self, points):
    # type: (List[PositionPoint]) -> None
    for point in points:
      position = point.position
      marker = self.__createWorldMarker(position, 0, MARKER_SYMBOL_NAME.NAVIGATION_MARKER)
      if marker:
        marker.setRenderInfo(MIN_SCALE, BOUNDS, INNER_BOUNDS, CULL_DISTANCE, BOUNDS_MIN_SCALE)
        marker.setLocationOffset(MIN_Y_OFFSET, MAX_Y_OFFSET, DISTANCE_FOR_MIN_Y_OFFSET, MAX_Y_BOOST, BOOST_START)

  @withExceptionHandling()
  def clearMarker(self, marker):
    # type: (Marker | WorldMarker) -> None
  
    if isinstance(marker, Marker):
      markerType = marker.markerType()
      if marker in self.__markers[markerType] and marker not in self.__freeMarkers[markerType]:
        self.__freeMarkers[markerType].append(marker)
        marker.setActive(False)
      
    if isinstance(marker, WorldMarker):
      markerType = marker.markerType()
      if marker in self.__worldMarkers[markerType] and marker not in self.__freeWorldMarkers[markerType]:
        self.__freeWorldMarkers[markerType].append(marker)
        marker.setActive(False)

  @withExceptionHandling()
  def clear(self):
    for key, value in self.__markers.items():
      for marker in value:
        marker.setActive(False)
        
        if marker not in self.__freeMarkers[key]:
          self.__freeMarkers[key].append(marker)

    for key, value in self.__worldMarkers.items():
      for marker in value:
        marker.setActive(False)
      
        if marker not in self.__freeWorldMarkers[key]:
          self.__freeWorldMarkers[key].append(marker)

  @withExceptionHandling()
  def reset(self):
    for key in self.__markers.keys():
      self.__markers[key] = []
      self.__freeMarkers[key] = []

    for key in self.__worldMarkers.keys():
      self.__worldMarkers[key] = []
      self.__freeWorldMarkers[key] = []

    self.__minimap = None
    self.__markerManager = None

  @withExceptionHandling()
  def __createMarker(self, position, markerType, container, scale=1.0, active=True):
    # type: (Tuple[float, float], str, str, float, bool) -> Marker
    
    markers = self.__freeMarkers[markerType]
    if len(markers) > 0:
      marker = markers.pop()
      marker.setPosition(position)
      marker.setScale(scale)
      marker.setActive(active)
      return marker

    if not self.__minimap or not self.__minimap.isCreated():
      self.__minimap = self.__getMinimap()

    if not self.__minimap:
      return

    markerScales = [0.8, 1.1]
    minimapSizeIndex = clampMinimapSizeIndex(AccountSettings.getSettings('minimapSize'))

    p = float(minimapSizeIndex - plugins._MINIMAP_MIN_SCALE_INDEX) / float(plugins._MINIMAP_MAX_SCALE_INDEX - plugins._MINIMAP_MIN_SCALE_INDEX)
    baseScale = p * markerScales[0] + (1 - p) * markerScales[1]

    logger.debug('Create new marker: %s' % str(position))
    marker = Marker(position, markerType, container, scale, self.__minimap, baseScale)
    self.__markers[markerType].append(marker)

    return marker
  
  @withExceptionHandling()
  def __createWorldMarker(self, position, yOffset, markerType, minimapMarker=None, active=True):
    # type: (Tuple[float, float], float, str, Marker | None, bool) -> WorldMarker

    markers = self.__freeWorldMarkers[markerType]
    if len(markers) > 0:
      marker = markers.pop()
      marker.setPosition(position)
      marker.setActive(active)
      marker.setupMinimapMarker(minimapMarker)
      return marker

    if not self.__markerManager or not self.__markerManager.isCreated():
      self.__markerManager = self.__getMarkerManager()

    if not self.__markerManager:
      return
    
    logger.debug('Create new world marker: %s' % str(position))
    marker = WorldMarker(position, yOffset, markerType, self.__markerManager, active)
    marker.setupMinimapMarker(minimapMarker)
    self.__worldMarkers[markerType].append(marker)

    return marker

class Marker():
  def __init__(self, position, markerType, container, scale, minimap, baseScale, active=True):
    # type: (Tuple[float, float], str, str, float, MinimapComponent, float, bool) -> Marker
    self.__position = position
    self.__markerType = markerType
    self.__container = container
    self.__minimap = minimap
    self.__baseScale = baseScale
    self.__scale = scale
    self.__isActive = active

    self.handle = self.__minimap.addEntry(self.__markerType, self.__container, self.__createMatrix(),
                                          active=active, transformProps=TRANSFORM_FLAG.FULL)

  def markerType(self):
    return self.__markerType

  def setPosition(self, position):
    # type: (Tuple[float, float]) -> None
    self.__position = position
    self.__minimap.setMatrix(self.handle, self.__createMatrix())
    
  def setScale(self, scale):
    # type: (float) -> None
    self.__scale = scale
    self.__minimap.setMatrix(self.handle, self.__createMatrix())

  def setActive(self, active):
    # type: (bool) -> None
    if self.__isActive == active:
      return
    
    self.__isActive = active
    self.__minimap.setActive(self.handle, active)

  def invoke(self, methodName, *args):
    # type: (str, *Any) -> None
    self.__minimap.invoke(self.handle, methodName, *args)

  def remove(self):
    self.__minimap.delEntry(self.handle)

  def __createMatrix(self):
    size = self.__baseScale * self.__scale
    pos = Vector3(self.__position[0], 0, self.__position[1])
    return minimap_utils.makePositionAndScaleMatrix(Vector3(pos), (size, 1.0, size))

class WorldMarker():

  __MARKER_TYPE_BY_SYMBOL = {
    MARKER_SYMBOL_NAME.NAVIGATION_MARKER: CommonMarkerType.LOCATION,
    MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER: CommonMarkerType.NORMAL
  }

  def __init__(self, position, yOffset, markerSymbol, manager, active=True):
    # type: (Tuple[float, float], float, str, MarkersManager, bool) -> WorldMarker

    self.__position = position
    self.__markerSymbol = markerSymbol
    self.__manager = manager
    self.__isActive = active

    matrix = createTranslationMatrix(self.__getTerrainHeightAt(position))
    self.handle = self.__manager.createMarker(self.__markerSymbol, matrix, active, self.__MARKER_TYPE_BY_SYMBOL[self.__markerSymbol])

  def markerType(self):
    return self.__markerSymbol

  def setupMinimapMarker(self, marker):
    # type: (Marker) -> None
    self.minimapMarker = marker

  def setPosition(self, position):
    # type: (Tuple[float, float]) -> None
    self.__position = position
    self.__manager.setMarkerMatrix(self.handle, createTranslationMatrix(self.__getTerrainHeightAt(position)))
    if self.minimapMarker:
      self.minimapMarker.setPosition(position)

  def setActive(self, active):
    # type: (bool) -> None
    if self.__isActive == active:
      return
    
    self.__isActive = active
    self.__manager.setMarkerActive(self.handle, active)
    if self.minimapMarker:
      self.minimapMarker.setActive(active)

  def setFocus(self, focus):
    # type: (bool) -> None
    self.__manager.setMarkerObjectInFocus(self.handle, focus)

  def setRenderInfo(self, minScale, bounds, innerBounds, cullDistance, markerBoundsScale):
    self.__manager.setMarkerRenderInfo(self.handle, minScale, bounds, innerBounds, cullDistance, markerBoundsScale)

  def setLocationOffset(self, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart):
    self.__manager.setMarkerLocationOffset(self.handle, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart)
  
  def invokeMarker(self, *signature):
    # type: (str, *Any) -> None
    self.__manager.invokeMarker(self.handle, *signature)
    
  def setMinScale(self, scale):
    self.__manager.setMarkerMinScale(self.handle, scale)
  
  def setSticky(self, sticky):
    # type: (bool) -> None
    self.__manager.setMarkerSticky(self.handle, sticky)

  def remove(self):
    self.__manager.destroyMarker(self.handle)

  def __getTerrainHeightAt(self, position):
    # type: (Tuple[float, float]) -> Tuple[float, float, float]
    x = position[0]
    z = position[1]
    spaceID = BigWorld.player().spaceID
    collisionWithTerrain = BigWorld.wg_collideSegment(spaceID, Vector3(x, 1000.0, z), Vector3(x, -1000.0, z), 128)
    return collisionWithTerrain.closestPoint if collisionWithTerrain is not None else (x, 0, z)