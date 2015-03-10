function initGL(canvas) {
    var gl
    try {
        gl = canvas.getContext("webgl",{preserveDrawingBuffer: true})
        gl.viewportWidth = canvas.width
        gl.viewportHeight = canvas.height
        return gl
    } catch (e) {
    }

    if (!gl) {
        alert("unable to initialize WebGL")
    }
    
    return null
}


function getShader(gl, id) {
    var shaderScript = document.getElementById(id)
    if (!shaderScript) {
        return null
    }

    var str = ""
    var k = shaderScript.firstChild
    while(k) {
        if (k.nodeType == 3) {
            str += k.textContent
        }
        k = k.nextSibling
    }

    var shader
    if (shaderScript.type == "x-shader/x-fragment") {
        shader = gl.createShader(gl.FRAGMENT_SHADER)
    } else if (shaderScript.type == "x-shader/x-vertex") {
        shader = gl.createShader(gl.VERTEX_SHADER)
    } else {
        return null
    }
    gl.shaderSource(shader, str)
    gl.compileShader(shader)

    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        alert(gl.getShaderInfoLog(shader))
        return null
    }

    return shader
}


function updateTextureData(texture) {
    gl.bindTexture(gl.TEXTURE_2D, texture)
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)
    //gl.texImage2D(gl.TEXTURE_2D, 0, gl.LUMINANCE, data.width, data.height-2, 0, gl.LUMINANCE, gl.UNSIGNED_BYTE, new Uint8Array(data.texture) )
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.LUMINANCE, gl.LUMINANCE, gl.UNSIGNED_BYTE, texture.image )
    gl.bindTexture(gl.TEXTURE_2D, null)
}


function squarePositionVerticies(size_x, size_y, z) {
    if (!z) {
        z = 0.0
    }
    size_x /= 2
    size_y /= 2
    var vertices = [
         size_x,  size_y,  z,
        -size_x,  size_y,  z,
         size_x, -size_y,  z,
        -size_x, -size_y,  z
    ]
    return vertices
}


function createSquareVertexPositionBuffer(gl, size_x, size_y) {
    var squareVertexPositionBuffer = gl.createBuffer()
    gl.bindBuffer(gl.ARRAY_BUFFER, squareVertexPositionBuffer)
    var vertices = squarePositionVerticies(size_x, size_y)
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertices), gl.STATIC_DRAW)
    squareVertexPositionBuffer.itemSize = 3
    squareVertexPositionBuffer.numItems = 4

    return squareVertexPositionBuffer
}


function textureVerticies(num_channels) {
    var y = 1.0
    if ((num_channels) && (num_channels == 2)) {
        y = 0.5
    }
    
    return textureCoords = [
            1.0, y,
            0.0, y,
            1.0, 0.0,
            0.0, 0.0
        ]
}

function createTextureCoordBuffer(num_channels) {
    var textureCoordBuffer = gl.createBuffer()
    gl.bindBuffer(gl.ARRAY_BUFFER, textureCoordBuffer)
    var textureCoords = textureVerticies(num_channels)
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(textureCoords), gl.STATIC_DRAW)
    textureCoordBuffer.itemSize = 2
    textureCoordBuffer.numItems = 4
    
    return textureCoordBuffer
}

function updateTextureRGBA(texture) {
    alert('function called - not implemented')
    var data = new Uint8Array([100, 0, 150, 200,100,0,0,255])
    gl.bindTexture(gl.TEXTURE_2D, texture)
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true)
    //gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, texture.image)
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.LUMINANCE, 4, 2, 0, gl.LUMINANCE, gl.UNSIGNED_BYTE,data )
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)
    gl.bindTexture(gl.TEXTURE_2D, null)
}


