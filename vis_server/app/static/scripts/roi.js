function roi(label,color) {
    this.label = label;
    this.color = color;
    this.points = [];
    this.pointsGl = [];
    this.glBuffer = roiContext.createBuffer();

    this.widthScale = g_frameViewer.mainProjectionWidth/g_sequenceInfo.width;
    this.widthConst = g_frameViewer.mainProjectionWidth/2;

    this.heightScale = g_frameViewer.mainProjectionHeight/g_sequenceInfo.height;
    this.heightConst = g_frameViewer.mainProjectionHeight-g_frameViewer.mainProjectionHeight/2;
    this.setPoints = function(roiPoints) {
        this.points = roiPoints
        for (var i=0; i < roiPoints.length; i++) {
            if (i%2 == 0) {
                this.pointsGl.push(roiPoints[i]*this.widthScale-this.widthConst)
            } else {
                this.pointsGl.push(
                    g_frameViewer.mainProjectionHeight*(1/2-roiPoints[i]/g_sequenceInfo.height));
                this.pointsGl.push(0.0);
            }
        }
        roiContext.bindBuffer(roiContext.ARRAY_BUFFER, this.glBuffer);
        roiContext.bufferData(roiContext.ARRAY_BUFFER, new Float32Array(this.pointsGl), roiContext.STATIC_DRAW);
        this.glBuffer.itemSize = 3;
        this.glBuffer.numItems = this.pointsGl.length/3;
    }

    /*
    this.setPointsBin = function(roiInfo) {
        var roiObj = this;
        var context = 
                $('<canvas width="'+roiInfo.length+'" height="1" style="display:none">',
                    {'class':roiInfo.label+'_buffer',
                     'id':'myId'})
                        .appendTo('body')[0]
                        .getContext("2d");
        var buffer = new Image();
        buffer.src = roiInfo.points
        buffer.onload = function() {
            context.drawImage(this,0,0);
            var contextData = context.getImageData(0,0,roiInfo.length,1).data;
            var count = 0;
            for (var i=0; i < contextData.length; i+=8) {
                var val = contextData[i]*256+contextData[i+4] + roiInfo.min_val
                roiObj.points.push(val);
                if (count%2 == 0) {
                    roiObj.pointsGl.push(val*roiObj.widthScale-roiObj.widthConst)
                } else {
                    val = g_sequenceInfo.height-val;
                    val *= g_frameViewer.mainProjectionHeight/g_sequenceInfo.height;
                    val -= g_frameViewer.mainProjectionHeight/2;
                    roiObj.pointsGl.push(val);
                    roiObj.pointsGl.push(0.0);
                }
                count++;
            }
            roiContext.bindBuffer(roiContext.ARRAY_BUFFER, roiObj.glBuffer);
            roiContext.bufferData(roiContext.ARRAY_BUFFER, new Float32Array(roiObj.pointsGl), roiContext.STATIC_DRAW);
            roiObj.glBuffer.itemSize = 3;
            roiObj.glBuffer.numItems = roiObj.pointsGl.length/3;
            buffer = null;
            $('.'+roiInfo.label+'_buffer').remove();
            drawShapes(roiContext);
        }
    }*/
}
