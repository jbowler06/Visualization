function FrameBuffer(sequenceId,maxLength) {
    this.maxLength = maxLength
    this.frameDelta = 1
    this.current = -1
    this.buffer = {}
    this.keys = []
    this.requested = []
    this.currentKey = -1
    this.maxSortedIndex = -1
    this.full = false
    this.sequenceId = sequenceId
    this.incommingBuffer = []

    this.length = function() { 
        return Object.keys(this.buffer).length 
    }

    this.set_next = function(nextValue) {
        this.current = nextValue-this.frameDelta
    }

    this.set_frameDelta = function(aFrameDelta) {
        if (this.frameDela == aFrameDelta) {
            return
        }
        this.frameDelta = aFrameDelta
    }

    this.has_next = function() {
        if (this.buffer[this.current + this.frameDelta]) {
            return true
        }

        return false
    }

    this.next = function() { 
        return this.current + this.frameDelta
    }

    /*
    this.reorderKeys = function() {
        if (this.sorting) return;
        this.sorting = true
        var current = this.current
        var delta = this.frameDelta
        var sortFunc = this.sortKeys
        var keyFind = this.keyFind
        this.keys.sort(function(a,b){return sortFunc(a,b,current,delta)}) 
        this.maxSortedIndex = this.keys.find(function(element,index,array){
            return keyFind(element,index,array,current,delta)
        })
        this.sorting = false
    }
    */
    
    this.sortKeys = function(a,b,current,delta) {
        var a_comp = (a-current)%delta
        var b_comp = (b-current)%delta

        if (!a_comp && b_comp){
            return -1
        } else if (a_comp && !b_comp){
            return 1
        } else {
            return (a-b)*delta
        }
    }
    
    
    this.isFull = function() {
        var len = this.length()
        if (len < this.maxLength) {
            return false
        } else {
            var currentKey = this.keys.indexOf(""+this.current)
            if (currentKey == -1) {
                return false
            }

            var endKey = this.keys[this.keys.length-1]
            if ((currentKey > 2*this.maxLength/3)||(this.maxSortedIndex != endKey)) {
                return false
            }
        }
        
        return true
    }

    this.sortKeys = function() {
        var current = this.current
        var delta = this.frameDelta

        this.keys = Object.keys(this.buffer)
        this.keys.sort(function(a,b) {
            var a_comp = (a-current)%delta
            var b_comp = (b-current)%delta

            if (!a_comp && b_comp){
                return -1
            } else if (a_comp && !b_comp){
                return 1
            } else {
                return (a-b)*delta
            }
        })

        this.maxSortedIndex = this.keys.find(function(element,index,array) {
            if (index == 0) {
                return array.length == 1   
            } if (index == array.length-1) {
                return true
            }
            return ((array[index+1]-element != delta) && (element > current))
        })

        return this.keys
    }

    this.addFrame = function(index,frame) {
        index = parseInt(index)
        this.requested.splice(this.requested.indexOf(index),1)
        this.buffer[parseInt(index)] = frame
        
        var keys = this.sortKeys()
        var currentKey = keys.indexOf(""+this.current)

        var len = this.length()
        while (len > this.maxLength) {
            if (currentKey > this.maxLength/3) {
                delete this.buffer[""+keys.shift()]
                currentKey--
                len--
            } else if (this.maxSortedIndex == this.keys[len-1]) {
                break
            } else {
                delete this.buffer[""+this.keys.pop()]
                len--
            }
        }
    }

    this.popFrame = function(index) {
        if (!this.buffer[index]) {
            alert('requested to play frame doesn\'t exist')
            return false
        }
        this.current = index
        return this.buffer[index]
    }

    this.next_request = function(numFrames) {
        var requestQueue = []
        var frame = this.current+this.frameDelta
        var keys = Object.keys(this.buffer)
        
        while (requestQueue.length < numFrames) {
            if ((!this.buffer[frame]) && (this.requested.indexOf(frame) == -1)) {
                requestQueue.push(frame)
                this.requested.push(frame)
            }
            frame += this.frameDelta
        }
        return requestQueue
    }
}
