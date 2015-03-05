function FrameBuffer(maxLength) {
    this.maxLength = maxLength
    this.frameDelta = 1
    this.current = -1
    this.buffer = {}
    this.keys = []
    this.requested = []
    this.currentKey = -1
    this.maxSortedIndex = -1
    this.full = false

    this.length = function() { 
        return Object.keys(this.buffer).length 
    }

    this.set_next = function(nextValue) {
        this.current = nextValue-this.frameDelta
        this.reorderKeys()
        this.currentKey = this.keys.indexOf(this.current)
    }

    this.set_frameDelta = function(aFrameDelta) {
        if (this.frameDela == aFrameDelta) {
            return
        }
        this.frameDelta = aFrameDelta
        this.reorderKeys()
        this.currentKey = this.keys.indexOf(this.current)
    }

    this.has_next = function() {
        return this.keys[this.currentKey+1] == this.current + this.frameDelta
        //return this.keys.indexOf(this.current + this.frameDelta) != -1
    }

    this.next = function() { 
        return this.keys[this.currentKey+1]
    }

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

    this.keyFind = function(element,index,array,current,delta) {
        if (index == 0) {
            return array.length == 1   
        } if (index == array.length-1) {
            return true
        }
        return ((array[index+1]-element != delta) && (element > current))
    }
    
    this.isFull = function() {
        if (this.keys.length < this.maxLength) {
            return false
        }
        
        if (this.keys.length >= this.maxLength) {
            if (this.keys.length-this.currentKey > this.maxLength*2/3) {

            return true
            }
        }

        return this.full
    }

    this.addFrame = function(index,frame) {
        index = parseInt(index)
        delete this.requested[this.requested.indexOf(index)]
        this.buffer[index] = frame
        this.keys.push(index)

        this.reorderKeys()

        this.full = false
        while ((this.keys.length >= this.maxLength)&&(!this.full)) {
            if (this.currentKey > this.maxLength/3) {
                delete this.buffer[this.keys.shift()]
                this.currentKey--
            } else if (this.keys[this.keys.length-1] == this.maxSortedIndex) {
                this.full = true
            } else {
                delete this.buffer[this.keys.pop()]
            }
        }

        if (this.currentKey == -1) {
            this.currentKey = this.keys.indexOf(this.current)
        }
    }

    this.popFrame = function(index) {
        if (this.keys[this.currentKey+1] != index) {
            alert('requested to play frame doesn\'t exist')
            return false
        }

        if (this.currentKey > this.maxLength/3) {
            delete this.buffer[this.keys.shift()]
            this.currentKey--
            this.full = false
        }
        this.current = index
        this.currentKey++
        
        return this.buffer[index]
    }

    this.next_request = function(numFrames) {
        var requestQueue = []
        var frame = this.current+this.frameDelta
        while (requestQueue.length < numFrames) {
            if ((this.keys.indexOf(frame) == -1)&&(this.requested.indexOf(frame) == -1)) {
                requestQueue.push(frame)
                this.requested.push(frame)
            }
            frame += this.frameDelta
        }
        return requestQueue
    }
}
