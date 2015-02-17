from vispy import app, gloo
from sima import Sequence
import numpy as np

vertex = """
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;
void main()
{
    gl_Position = vec4(a_position, 0.0, 1.0);
    v_texcoord = a_texcoord;

}
"""

fragment = """
uniform sampler2D u_texture;
varying vec2 v_texcoord;
uniform float u_time;

void main() {
    vec4 clr1 = texture2D(u_texture, v_texcoord);
    gl_FragColor = vec4(clr1.rgb,1.0);
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, position=(300, 100),
                            size=(800, 800), keys='interactive')

        self.program = gloo.Program(vertex, fragment)
        self.program['a_position'] = [(-1., -.5, 0.), (-1., +1.,0.),
                                      (+0.5, -.5, 0.), (+0.5, +1,0.)]
        self.program['a_texcoord'] = [(0., 0.), (0., +1),
                                      (+1., 0.), (+1, +1)]
        self.program['u_time'] = 0.0

        self.program2 = gloo.Program(vertex, fragment)
        self.program2['a_position'] = [(-1., -1., 0.), (-1., -0.55,0.),
                                      (+0.5, -1., 0.), (+0.5, -0.55,0.)]
        self.program2['a_texcoord'] = [(0., 0.), (0., +1.),
                                      (+1., 0.), (+1., +1.)]
        self.program2['u_time'] = 0.0

        self.program3 = gloo.Program(vertex, fragment)
        self.program3['a_position'] = [(0.55, -0.5, 0.), (0.55, +1.,0.),
                                      (+1., -0.5, 0.), (+1., +1.,0.)]
        self.program3['a_texcoord'] = [(0., 0.), (0., +1.),
                                      (+1., 0.), (+1., +1.)]
        self.program3['u_time'] = 0.0
       
        path = '/Volumes/data/Nathan/2photon/rewardRemapping/nd125/02112015/day1-session-002/day1-session-002_Cycle00001_Element00001.h5'
        #path =  '/Volumes/data/Nathan/2photon/acuteRemapping/nd118/12172014/z-series-004/z-series-004_Cycle00001_Element00001.h5'
        seq = Sequence.create('HDF5',path,'tzyxc')
        self.sequence_iterator = seq.__iter__()
        vol = self.sequence_iterator.next()
        """
        self.vol_iter = vol.__iter__()
        surf = self.vol_iter.next()[:,:,0]
        """
        surf = np.sum(vol,axis=0)[:,:,0]
        surf /= np.max(surf)
        self.program['u_texture'] = surf.astype('float32')
        
        surf2 = np.sum(vol,axis=2)[:,:,0]
        surf2 /= np.max(surf2)
        self.program2['u_texture'] = surf2.astype('float32')

        surf3 = (np.sum(vol,axis=1)[:,:,0]).T
        surf3 /= np.max(surf3)
        self.program3['u_texture'] = surf3.astype('float32')

        self.timer = app.Timer(0.5, connect=self.on_timer, start=True)

    def on_timer(self, event):
        """
        self.program['u_time'] = event.elapsed
        try: 
            surf = self.vol_iter.next()[:,:,0]
        except:
            self.vol_iter = self.sequence_iterator.next().__iter__()
            surf = self.vol_iter.next()[:,:,0]
        surf /= np.max(surf)
        """
        
        vol = self.sequence_iterator.next()

        surf = np.sum(vol,axis=0)[:,:,0]
        surf /= np.max(surf)
        self.program['u_texture'] = surf.astype('float32')


        surf = np.sum(vol,axis=1)[:,:,0]
        surf /= np.max(surf)
        self.program2['u_texture'] = surf.astype('float32')

        surf = (np.sum(vol,axis=2)[:,:,0]).T
        surf /= np.max(surf)
        self.program3['u_texture'] = surf.astype('float32')

        self.update()

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        self.program.draw('triangle_strip')
        self.program2.draw('triangle_strip')
        self.program3.draw('triangle_strip')

if __name__ == '__main__':
    canvas = Canvas()
    canvas.show()
    app.run()
