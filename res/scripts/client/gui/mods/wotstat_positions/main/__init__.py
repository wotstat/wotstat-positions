from typing import List, Tuple  # noqa: F401

class IPositionRequester(object):
  def start(self):
    pass

  def stop(self):
    pass

class IPositionDrawer(object):

  def isReady(self):
    return False

  def drawPoints(self, points):
    # type: (List[PositionPoint]) -> None
    pass

  def drawIdealPoints(self, points):
    # type: (List[PositionPoint]) -> None
    pass

  def drawMarkers3D(self, points):
    # type: (List[PositionPoint]) -> None
    pass
  
  def drawEyeMarkers(self, points):
    # type: (List[Spots.Point]) -> None
    pass

  def clear(self):
    pass

  def reset(self):
    pass

class Heatmap(object):
  def __init__(self, points, step):
    # type: (List[Tuple[float, float, float]], float) -> None
    self.points = points
    self.step = step
    
class Spots(object):
  
  class Point(object):
    def __init__(self, position, hits):
      # type: (Tuple[float, float, float], List[Tuple[float, float, float]]) -> None
      self.position = position
      self.hits = hits
  
  def __init__(self, points):
    # type: (List[Point]) -> None
    self.points = points

class PositionPoint(object):
  def __init__(self, efficiency, position):
    # type: (float, Tuple[float, float]) -> None
    self.efficiency = efficiency
    self.position = position