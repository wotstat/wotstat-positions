package wotstat.positions {
  import net.wg.infrastructure.base.AbstractView;
  import net.wg.data.constants.generated.LAYER_NAMES;
  import net.wg.gui.components.containers.MainViewContainer;
  import net.wg.gui.battle.views.BaseBattlePage;
  import flash.display.DisplayObject;
  import flash.display.Sprite;
  import net.wg.gui.battle.views.minimap.Minimap;
  import net.wg.gui.battle.views.minimap.EpicMinimap;
  import flash.display.Graphics;
  import flash.events.MouseEvent;
  import net.wg.gui.components.controls.Image;
  import flash.geom.Matrix;

  public class MinimapOverlay extends AbstractView {

    private const MOUSE_DIRECTION_THRESHOLD:Number = 0.04;
    private const VEHICLE_DIRECTION_THRESHOLD:Number = 0.04;

    public var py_log:Function;

    private var isInitialized:Boolean = false;
    private var spotPoints:Sprite = null;
    private var spotDirections:Sprite = null;

    private var heatmap:Heatmap = new Heatmap(0xFFFF00, 250, -1);
    private var popularHeatmap:Heatmap = new Heatmap(0x00FFFF, 250, -1);

    private var overlayWidth:Number = 1;
    private var overlayHeight:Number = 1;

    private var hits:Vector.<Vector.<Object>> = new Vector.<Vector.<Object>>();
    private var spotPointsData:Vector.<Object> = new Vector.<Object>();
    private var spotPointImage:Image = new Image();

    private var vehiclePosition:Array = [0, 0];

    public function MinimapOverlay() {
      super();
      App.instance.addEventListener(MouseEvent.MOUSE_MOVE, onMouseMove);
      spotPointImage.source = "wotstatPositionsAssets/spot-point.png";
    }

    override protected function onDispose():void {
      App.instance.removeEventListener(MouseEvent.MOUSE_MOVE, onMouseMove);
      heatmap.dispose();
      popularHeatmap.dispose();
      super.onDispose();
    }

    override protected function configUI():void {
      super.configUI();

      var viewContainer:MainViewContainer = App.containerMgr.getContainer(LAYER_NAMES.LAYER_ORDER.indexOf(LAYER_NAMES.VIEWS)) as MainViewContainer;

      if (viewContainer != null && !isInitialized) {

        for (var i:int = 0; i < viewContainer.numChildren; ++i) {
          var child:DisplayObject = viewContainer.getChildAt(i);

          if (!(child is BaseBattlePage))
            continue;

          var battlePage:BaseBattlePage = child as BaseBattlePage;

          spotPoints = new Sprite();
          spotPoints.cacheAsBitmap = true;
          spotDirections = new Sprite();
          isInitialized = true;

          if (battlePage.minimap is Minimap) {
            var minimap:Minimap = battlePage.minimap as Minimap;
            var index:int = minimap.entriesContainer.getChildIndex(minimap.entriesContainer.flags);
            minimap.entriesContainer.addChildAt(popularHeatmap, index);
            minimap.entriesContainer.addChildAt(heatmap, index + 1);
            minimap.entriesContainer.addChildAt(spotDirections, index + 2);
            minimap.entriesContainer.addChildAt(spotPoints, index + 3);

            overlayWidth = minimap.background.width;
            overlayHeight = minimap.background.height;

            heatmap.x = spotPoints.x = popularHeatmap.x = spotDirections.x = -overlayWidth / 2;
            heatmap.y = spotPoints.y = popularHeatmap.y = spotDirections.y = -overlayHeight / 2;
          }
          else if (battlePage.minimap is EpicMinimap) {
            var eipcMinimap:EpicMinimap = battlePage.minimap as EpicMinimap;
            eipcMinimap.background.addChild(popularHeatmap);
            eipcMinimap.background.addChild(heatmap);
            eipcMinimap.background.addChild(spotDirections);
            eipcMinimap.background.addChild(spotPoints);

            overlayHeight = eipcMinimap.background.originalHeight;
            overlayWidth = eipcMinimap.background.originalWidth;
          }

          heatmap.setSize(overlayWidth, overlayHeight);
          popularHeatmap.setSize(overlayWidth, overlayHeight);
        }
      }
    }

    public function as_setupSpotPoints(points:Array):void {
      if (spotPoints == null)
        return;

      spotPointsData = new Vector.<Object>();
      hits = new Vector.<Vector.<Object>>();
      for (var i:int = 0; i < points.length; i++) {
        var point:Object = points[i];
        var pos:Array = convert(point.position[0], point.position[1]);

        var hit:Vector.<Object> = new Vector.<Object>();

        for (var j:int = 0; j < point.hits.length; j++) {
          var spot:Object = point.hits[j];
          var spotPos:Array = convert(spot[0], spot[1]);
          hit.push([spotPos[0], spotPos[1], 0.2 + spot[2]]);
        }

        spotPointsData.push([pos[0], pos[1], point.position[2]]);
        hits.push(hit);
      }

      redrawSpotPoints();
      redrawSpotDirections();
    }

    public function as_setupHeatmap(x:Array, y:Array, weight:Array, multiplier:Number):void {
      if (heatmap == null)
        return;

      heatmap.setupHeatmap(x, y, weight, multiplier);
    }

    public function as_setupPopularHeatmap(x:Array, y:Array, weight:Array, multiplier:Number):void {
      if (popularHeatmap == null)
        return;

      popularHeatmap.setupHeatmap(x, y, weight, multiplier);
    }

    public function as_setRelativeVehiclePosition(x:Number, y:Number):void {
      vehiclePosition = [x, 1 - y];
      redrawSpotDirections();
    }

    public function as_clear():void {
      heatmap.clear();
      popularHeatmap.clear();
      spotPointsData = new Vector.<Object>();
      hits = new Vector.<Vector.<Object>>();
      redrawSpotPoints();
      redrawSpotDirections();
    }

    private function convert(x:Number, y:Number):Array {
      return [x * overlayWidth, overlayHeight - y * overlayHeight];
    }

    private function redrawSpotPoints():void {
      var ctx:Graphics = spotPoints.graphics;
      ctx.clear();

      for (var i:int = 0; i < spotPointsData.length; i++) {
        const targetWidth:Number = 15 * spotPointsData[i][2];
        const scale:Number = targetWidth / spotPointImage.bitmapData.width;
        const offsetX:Number = spotPointsData[i][0] - targetWidth / 2;
        const offsetY:Number = spotPointsData[i][1] - targetWidth / 2;

        const matrix:Matrix = new Matrix();
        matrix.scale(scale, scale);
        matrix.translate(offsetX, offsetY);

        ctx.beginBitmapFill(spotPointImage.bitmapData, matrix, false, true);
        ctx.drawRect(offsetX, offsetY, targetWidth, targetWidth);
        ctx.endFill();
      }
    }

    private function redrawSpotDirections():void {
      if (spotDirections == null)
        return;

      var ctx:Graphics = spotDirections.graphics;
      ctx.clear();

      var x:Number = spotPoints.mouseX / overlayWidth;
      var y:Number = spotPoints.mouseY / overlayHeight;

      const mouseThresholdSqr:Number = MOUSE_DIRECTION_THRESHOLD * MOUSE_DIRECTION_THRESHOLD;
      const vehicleThresholdSqr:Number = VEHICLE_DIRECTION_THRESHOLD * VEHICLE_DIRECTION_THRESHOLD;

      for (var i:uint = 0; i < hits.length; i++) {
        const hit:Vector.<Object> = hits[i];

        const pX:Number = spotPointsData[i][0] / overlayWidth;
        const pY:Number = spotPointsData[i][1] / overlayHeight;

        const mouseDistanceSqr:Number = Math.pow(x - pX, 2) + Math.pow(y - pY, 2);
        const vehicleDistanceSqr:Number = Math.pow(vehiclePosition[0] - pX, 2) + Math.pow(vehiclePosition[1] - pY, 2);

        if (mouseDistanceSqr > mouseThresholdSqr && vehicleDistanceSqr > vehicleThresholdSqr)
          continue;


        const mouseDistance:Number = Math.sqrt(mouseDistanceSqr);
        const vehicleDistance:Number = Math.sqrt(vehicleDistanceSqr);

        const alpha:Number = Math.max(
            Math.min(1, 1 - Math.max(0, mouseDistance - 0.02) / 0.02),
            Math.min(1, 1 - Math.max(0, vehicleDistance - 0.02) / 0.02)
          );

        for (var j:int = 0; j < hit.length; j++) {
          var spot:Object = hit[j];
          ctx.lineStyle(0.3, 0xFFEAB8, Math.min(1, Math.max(0, alpha * spot[2])));
          ctx.moveTo(pX * overlayWidth, pY * overlayHeight);
          ctx.lineTo(spot[0], spot[1]);
        }
      }
    }

    private function onMouseMove(e:MouseEvent):void {
      var x:Number = spotPoints.mouseX / overlayWidth;
      var y:Number = spotPoints.mouseY / overlayHeight;

      if (x < 0 || x > 1 || y < 0 || y > 1)
        return;

      this.redrawSpotDirections();
    }
  }
}