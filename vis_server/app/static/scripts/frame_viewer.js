function FrameViewer() {
    this.playing = false;
    this.frameDelay = 166.66;
    this.dragScale = 400;

    this.zoomLevel = -3.5;
    this.mainProjectionHeight = 2;
    this.mainProjectionWidth = 2;

    this.offset = { x:0, y:0 };

    this.mouseState = {
        mouseDown: false
    }

    this.isPlaying = function() {
        return this.playing;
    }

    this.setPlaying = function(state) {
        this.playing = state;
    }

    this.getFrameRate = function() {
        return 1000/this.frameDelay;
    }

    this.setFrameRate = function(rate) {
        this.frameDelay = 1000/rate;
    }

    this.initMouse = function(gl_canvas) {
        var mouseState = this.mouseState;
        var play = this.playing;
        var thisViewer = this;
        gl_canvas.bind('DOMMouseScroll mousewheel', function(event) {
            if (event.originalEvent.wheelDelta > 0 || event.originalEvent.detail < 0) {
                if ($('#volume_button').hasClass('selected')) {
                    g_plane = Math.min(g_sequenceInfo.planes.length-1,g_plane+1);
                    showPlane(g_plane);
                } else {
                    thisViewer.zoomLevel = Math.min(thisViewer.zoomLevel+0.1,-0.1);
                }
            } else {
                if ($('#volume_button').hasClass('selected')) {
                    g_plane = Math.max(1,g_plane-1);
                    showPlane(g_plane);
                } else {
                    thisViewer.zoomLevel -= 0.1;
                }
            }
            if (!play) {
                drawScene();
            }
        });

        gl_canvas.bind('mousedown',function(){
            mouseState.mouseDown = true;
        });

        gl_canvas.bind('mouseup',function(){
            mouseState.mouseDown = false;
        });

        var dragScale = this.dragScale;
        gl_canvas.mousemove(function(event) {
            if (mouseState.mouseDown) {
                var dx = event.clientX - mouseState.lastMouseX;
                var dy = event.clientY - mouseState.lastMouseY;
                thisViewer.offset.x += dx/dragScale;
                thisViewer.offset.y -= dy/dragScale;

                if (!play) {
                    drawScene();
                }
            }
            mouseState.lastMouseX = event.clientX;
            mouseState.lastMouseY = event.clientY;
        });
    };
};
