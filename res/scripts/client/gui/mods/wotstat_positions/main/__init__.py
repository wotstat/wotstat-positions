from typing import List, Tuple

class IPositionRequester(object):
  def start(self):
    pass

  def stop(self):
    pass

class IPositionDrawer(object):
  def drawPoints(self, points):
    # type: (List[PositionPoint]) -> None
    pass

  def drawPolygons(self, polygons):
    pass

  def drawIdealPoints(self, points):
    pass

  def clear(self):
    pass

  def reset(self):
    pass

class PositionPoint(object):
  def __init__(self, efficiency, position):
    # type: (float, Tuple[float, float]) -> None
    self.efficiency = efficiency
    self.position = position