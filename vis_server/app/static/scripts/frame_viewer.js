function FrameViewer() {
    this.playing = false;
    this.frameDelay = 166.66;
    this.dragScale = 400;
    this.current = 0;

    this.zoomLevel = -3.5;
    this.mainProjectionHeight = 2;
    this.mainProjectionWidth = 2;
    this.planeSelect = $('#plane_select');

    this.offset = { x:0, y:0 };

    this.mouseState = {
        mouseDown: false
    }

    this.isPlaying = function() {
        return this.playing;
    }

    this.getCurrentPlane = function() {
        return parseInt(this.planeSelect.val());
    };

    this.setCurrentPlane = function(plane) {
        this.planeSelect.val(
                Math.min(Math.max(0,plane),this.planeSelect.attr('max')));
        this.planeSelect.trigger('change');
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
                    thisViewer.setCurrentPlane(thisViewer.getCurrentPlane()+1);
                } else {
                    thisViewer.zoomLevel = Math.min(thisViewer.zoomLevel+0.1,-0.1);
                }
            } else {
                if ($('#volume_button').hasClass('selected')) {
                    $('#plane_select').val();
                    thisViewer.setCurrentPlane(Math.max(1,thisViewer.getCurrentPlane()-1));
                } else {
                    thisViewer.zoomLevel -= 0.1;
                }
            }
            if (!play) {
                frameContext.render();
            }
            roiContext.render();
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
                    frameContext.render();
                }
                roiContext.render();
            }
            mouseState.lastMouseX = event.clientX;
            mouseState.lastMouseY = event.clientY;
        });
    };
};
