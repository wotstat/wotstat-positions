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
  import flash.events.Event;

  public class MinimapOverlay extends AbstractView {

    public var py_log:Function;

    private var isInitialized:Boolean = false;
    private var heatmap:Sprite = null;
    private var popularHeatmap:Sprite = null;
    private var spotPoints:Sprite = null;

    private var overlayWidth:Number = 0;
    private var overlayHeight:Number = 0;

    private var hits:Vector.<Vector.<Object>> = new Vector.<Vector.<Object>>();
    private var spotPointsData:Vector.<Object> = new Vector.<Object>();

    private var heatmapData:Vector.<Object> = new Vector.<Object>();
    private var popularHeatmapData:Vector.<Object> = new Vector.<Object>();
    private var currentHeatmapIndex:int = 0;
    private var currentPopularHeatmapIndex:int = 0;
    private var heatmapMultiplier:Number = 1;
    private var popularHeatmapMultiplier:Number = 1;

    public function MinimapOverlay() {
      super();
      App.instance.addEventListener(MouseEvent.MOUSE_MOVE, onMouseMove);
      App.instance.addEventListener(Event.ENTER_FRAME, onFrame);
    }

    override protected function onDispose():void {
      App.instance.removeEventListener(MouseEvent.MOUSE_MOVE, onMouseMove);
      App.instance.removeEventListener(Event.ENTER_FRAME, onFrame);
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

          heatmap = new Sprite();
          popularHeatmap = new Sprite();
          spotPoints = new Sprite();

          heatmap.cacheAsBitmap = true;
          popularHeatmap.cacheAsBitmap = true;
          spotPoints.cacheAsBitmap = true;

          isInitialized = true;

          if (battlePage.minimap is Minimap) {
            var minimap:Minimap = battlePage.minimap as Minimap;
            var index:int = minimap.entriesContainer.getChildIndex(minimap.entriesContainer.flags);
            minimap.entriesContainer.addChildAt(heatmap, index);
            minimap.entriesContainer.addChildAt(popularHeatmap, index + 1);
            minimap.entriesContainer.addChildAt(spotPoints, index + 2);

            overlayWidth = minimap.background.width;
            overlayHeight = minimap.background.height;

            heatmap.x = spotPoints.x = popularHeatmap.x = -overlayWidth / 2;
            heatmap.y = spotPoints.y = popularHeatmap.y = -overlayHeight / 2;
          }
          else if (battlePage.minimap is EpicMinimap) {
            var eipcMinimap:EpicMinimap = battlePage.minimap as EpicMinimap;
            eipcMinimap.background.addChild(popularHeatmap);
            eipcMinimap.background.addChild(heatmap);
            eipcMinimap.background.addChild(spotPoints);

            overlayHeight = eipcMinimap.background.originalHeight;
            overlayWidth = eipcMinimap.background.originalWidth;
          }
        }
      }

    }

    public function as_setupSpotPoints(points:Array):void {
      if (spotPoints == null)
        return;

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

      redrawSpots();
    }

    public function as_setupHeatmap(x:Array, y:Array, weight:Array, multiplier:Number):void {
      if (heatmap == null)
        return;

      if (x.length != y.length || x.length != weight.length || y.length != weight.length)
        return;

      heatmap.graphics.clear();
      currentHeatmapIndex = 0;
      heatmapData = new Vector.<Object>();
      for (var i:int = 0; i < x.length; i++) {
        heatmapData.push([x[i], y[i], weight[i]]);
      }
      heatmapMultiplier = multiplier;
    }

    public function as_setupPopularHeatmap(x:Array, y:Array, weight:Array, multiplier:Number):void {
      if (popularHeatmap == null)
        return;

      if (x.length != y.length || x.length != weight.length || y.length != weight.length)
        return;

      popularHeatmap.graphics.clear();
      currentPopularHeatmapIndex = 0;
      popularHeatmapData = new Vector.<Object>();
      for (var i:int = 0; i < x.length; i++) {
        popularHeatmapData.push([x[i], y[i], weight[i]]);
      }
      popularHeatmapMultiplier = multiplier;
    }

    public function as_clear():void {
      if (heatmap == null)
        return;
      heatmap.graphics.clear();
    }

    private function drawHeatmapDot(ctx:Graphics, x:Number, y:Number, weight:Number, color:uint, multiplier:Number):void {
      ctx.beginFill(color, Math.max(0, Math.min(1, weight * 2)));
      var size:Number = weight * overlayWidth * multiplier * 1.2;
      ctx.drawRect(x * overlayWidth - size / 2, overlayHeight - (y * overlayHeight) - size / 2, size, size);
    }

    private function convert(x:Number, y:Number):Array {
      return [x * overlayWidth, overlayHeight - y * overlayHeight];
    }

    private function redrawSpots():void {
      var ctx:Graphics = spotPoints.graphics;
      ctx.clear();

      ctx.lineStyle(0);
      ctx.beginFill(0x00FF00, 1);
      for (var i:int = 0; i < spotPointsData.length; i++) {
        var point:Object = spotPointsData[i];
        ctx.drawCircle(point[0], point[1], point[2] * 1.5);
      }
      ctx.endFill();

      var x:Number = spotPoints.mouseX;
      var y:Number = spotPoints.mouseY;

      if (x / overlayWidth < 0 || x / overlayWidth > 1 || y / overlayHeight < 0 || y / overlayHeight > 1)
        return;

      for (i = 0; i < hits.length; i++) {
        const hit:Vector.<Object> = hits[i];

        const pX:Number = spotPointsData[i][0];
        const pY:Number = spotPointsData[i][1];

        const mouseDistance:Number = Math.sqrt(Math.pow((x - pX) / overlayWidth, 2) + Math.pow((y - pY) / overlayHeight, 2));

        if (mouseDistance > 0.03)
          continue;


        const alpha:Number = Math.min(1, 1 - Math.max(0, mouseDistance - 0.01) / 0.02);
        py_log("mouseDistance: " + mouseDistance + ", alpha: " + alpha + ", x: " + x + ", y: " + y + ", pX: " + pX + ", pY: " + pY);

        for (var j:int = 0; j < hit.length; j++) {
          var spot:Object = hit[j];
          ctx.lineStyle(0.5, 0x00FF00, Math.min(1, Math.max(0, alpha * spot[2])));
          ctx.moveTo(pX, pY);
          ctx.lineTo(spot[0], spot[1]);
        }
      }
    }

    private function onMouseMove(e:MouseEvent):void {
      var x:Number = spotPoints.mouseX / overlayWidth;
      var y:Number = spotPoints.mouseY / overlayHeight;

      // if (x < 0 || x > 1 || y < 0 || y > 1)
      // return;

      // trace("x: " + x + ", y: " + y);
      // py_log("x: " + x + ", y: " + y);

      this.redrawSpots();
    }

    private function onFrame(e:Event):void {
      if (currentHeatmapIndex < heatmapData.length) {
        var ctx:Graphics = heatmap.graphics;
        for (var i:int = 0; i < 50 && currentHeatmapIndex < heatmapData.length; i++) {
          drawHeatmapDot(ctx,
              heatmapData[currentHeatmapIndex][0],
              heatmapData[currentHeatmapIndex][1],
              heatmapData[currentHeatmapIndex][2],
              0xFFFF00,
              heatmapMultiplier);
          currentHeatmapIndex++;
        }
      }

      if (currentPopularHeatmapIndex < popularHeatmapData.length) {
        ctx = popularHeatmap.graphics;
        for (i = 0; i < 50 && currentPopularHeatmapIndex < popularHeatmapData.length; i++) {
          drawHeatmapDot(ctx,
              popularHeatmapData[currentPopularHeatmapIndex][0],
              popularHeatmapData[currentPopularHeatmapIndex][1],
              popularHeatmapData[currentPopularHeatmapIndex][2],
              0x00FFFF,
              popularHeatmapMultiplier);
          currentPopularHeatmapIndex++;
        }

        if (currentPopularHeatmapIndex == popularHeatmapData.length) {
          py_log("popularHeatmapData done");
          popularHeatmap.cacheAsBitmap = true;
        }
      }
    }

  }
}