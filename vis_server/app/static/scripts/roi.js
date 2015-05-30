function roi(label,color) {
    this.label = label;
    this.color = color;
    this.mask = {};
    this.display = true;

    this.widthScale = g_frameViewer.mainProjectionWidth/g_sequenceInfo.width;
    this.widthConst = g_frameViewer.mainProjectionWidth/2;

    this.heightScale = g_frameViewer.mainProjectionHeight/g_sequenceInfo.height;
    this.heightConst = g_frameViewer.mainProjectionHeight-g_frameViewer.mainProjectionHeight/2;
    
    this.segments = []
    this.points = []

    this.setPoints = function(roiPoints) {
        this.points = roiPoints;
        this.type = 'polygons';
        for (var plane in roiPoints) {
            this.segments[parseInt(plane)] = [];
            for (var seg = 0; seg  < roiPoints[plane].length; seg++) {
                var segment = {}
                segment.polyBuffer = roiContext.createBuffer();
                segment.polyBuffer.points = [];
                
                var ec = earcut([roiPoints[plane][seg]],true);
                var tris = ec.vertices;
                for (var i=0; i < tris.length; i++) {
                    if (i%2 == 0) {
                        segment.polyBuffer.points.push(tris[i]*this.widthScale-this.widthConst)
                    } else {
                        segment.polyBuffer.points.push(
                            g_frameViewer.mainProjectionHeight*(1/2-tris[i]/g_sequenceInfo.height));
                        segment.polyBuffer.points.push(0);
                    }
                }

                segment.boundaryBuffer = roiContext.createBuffer();
                segment.boundaryBuffer.points = [];
                for (var i=0; i < roiPoints[plane][seg].length; i++) {
                    segment.boundaryBuffer.points.push(roiPoints[plane][seg][i][0]*this.widthScale-this.widthConst)
                    segment.boundaryBuffer.points.push(
                        g_frameViewer.mainProjectionHeight*(1/2-roiPoints[plane][seg][i][1]/g_sequenceInfo.height));
                    segment.boundaryBuffer.points.push(0);
                }

                roiContext.bindBuffer(roiContext.ARRAY_BUFFER, segment.boundaryBuffer);
                roiContext.bufferData(roiContext.ARRAY_BUFFER, new Float32Array(segment.boundaryBuffer.points), roiContext.STATIC_DRAW);
                segment.boundaryBuffer.itemSize = 3;
                segment.boundaryBuffer.numItems = segment.boundaryBuffer.points.length/3;

                roiContext.bindBuffer(roiContext.ARRAY_BUFFER, segment.polyBuffer);
                roiContext.bufferData(roiContext.ARRAY_BUFFER, new Float32Array(segment.polyBuffer.points), roiContext.STATIC_DRAW);
                segment.polyBuffer.itemSize = 3;
                segment.polyBuffer.numItems = segment.polyBuffer.points.length/3;

                segment.indicesBuffer = roiContext.createBuffer();
                roiContext.bindBuffer(roiContext.ELEMENT_ARRAY_BUFFER, segment.indicesBuffer);
                roiContext.bufferData(roiContext.ELEMENT_ARRAY_BUFFER, new Uint16Array(ec.indices), roiContext.STATIC_DRAW);
                segment.indicesBuffer.itemSize = 1;
                segment.indicesBuffer.numItems = ec.indices.length;

                this.segments[parseInt(plane)].push(segment);
            }
        }
    }

    this.addPoint = function(plane,segment,point) {
        
        if (typeof(this.points[plane]) === "undefined") {
            this.points[plane] = [];
        }

        if (typeof(this.points[plane][segment]) === "undefined") {
            this.points[plane][segment] = [];
        }

        this.points[plane][segment].push(point);
        this.setPoints(this.points);
    }

    this.getSegments = function(plane) {
        if (typeof this.segments[plane] == 'undefined') {
            return [];
        }

        return this.segments[plane]
    }

    this.setMask = function (projections) {
        this.type = 'mask'
        this.mask = projections
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
