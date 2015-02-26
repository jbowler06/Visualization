function FrameBuffer(maxLength, frameDelta) {
    this.maxLength = maxLength
    this.frameDelta = frameDelta
    this.current = -1
    this.buffer = {}


    this.length = function() { 
        return Object.keys(this.buffer).length 
    }

    this.next = function() { 
        return this.current + this.frameDelta 
    }

    this.min = function() {
        if (this.current < 0) {
            return 0
        }
        var sorted = Object.keys(this.buffer).sort(function(a,b){return a-b})
        return sorted[0]
    }
    
    this.max = function() {
        if (this.current < 0) {
            return 0
        }
        var sorted = Object.keys(this.buffer).sort(function(a,b){return b-a})
        return sorted[0]
    }
}
