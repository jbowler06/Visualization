import sys
import argparse
import os.path

import numpy as np
from vispy import app, gloo

from sima import Sequence
from sima import ImagingDataset

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


# This value was derived as the 95th percentile of testing experiment volume.
# TODO: determine a better metric (or dynamic update) for this
NORMING_VAL = 2194

class Canvas(app.Canvas):
    def __init__(self, path, channel=0):
        app.Canvas.__init__(self, position=(300, 100),
                            size=(800, 800), keys='interactive')

        self.program = gloo.Program(vertex, fragment)
        self.program['a_position'] = [(-1., -.5, 0.), (-1., +1.,0.),
                                      (+0.5, -.5, 0.), (+0.5, +1,0.)]
        self.program['a_texcoord'] = [(0., 0.), (0., +1),
                                      (+1., 0.), (+1, +1)]

        self.program2 = gloo.Program(vertex, fragment)
        self.program2['a_position'] = [(-1., -1., 0.), (-1., -0.55,0.),
                                      (+0.5, -1., 0.), (+0.5, -0.55,0.)]
        self.program2['a_texcoord'] = [(0., 0.), (0., +1.),
                                      (+1., 0.), (+1., +1.)]

        self.program3 = gloo.Program(vertex, fragment)
        self.program3['a_position'] = [(0.55, -0.5, 0.), (0.55, +1.,0.),
                                      (+1., -0.5, 0.), (+1., +1.,0.)]
        self.program3['a_texcoord'] = [(0., 0.), (0., +1.),
                                      (+1., 0.), (+1., +1.)]
       
        if os.path.splitext(path)[-1] == '.sima':
            ds = ImagingDataset.load(path)
            seq = ds.__iter__().next()
        else:
            seq = Sequence.create('HDF5',path,'tzyxc')

        self.channel = channel
        self.sequence_iterator = seq.__iter__()
        vol = self.sequence_iterator.next().astype('float32')
        vol /= NORMING_VAL
        vol = np.clip(vol, 0, 1)

        surf = np.sum(vol,axis=0)[:,:,channel]/vol.shape[0]
        self.program['u_texture'] = surf
        
        surf2 = np.sum(vol,axis=1)[:,:,channel]/vol.shape[1]
        self.program2['u_texture'] = surf2.astype('float32')

        surf3 = np.fliplr((np.sum(vol,axis=2)[:,:,channel]).T)/vol.shape[2]
        self.program3['u_texture'] = surf3.astype('float32')

        self.timer = app.Timer(0.25, connect=self.on_timer, start=True)


    def on_key_press(self,event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()

    def on_timer(self, event):
        try:
            vol = self.sequence_iterator.next().astype('float32')
        except StopIteration:
            self.timer.stop()
            return

        vol /= NORMING_VAL
        vol = np.clip(vol, 0, 1)

        surf = np.sum(vol,axis=0)[:,:,self.channel]/vol.shape[0]
        self.program['u_texture'] = surf


        surf = np.sum(vol,axis=1)[:,:,self.channel]/vol.shape[1]
        self.program2['u_texture'] = surf

        surf = np.fliplr((np.sum(vol,axis=2)[:,:,self.channel]).T)/vol.shape[2]
        self.program3['u_texture'] = surf

        self.update()

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        self.program.draw('triangle_strip')
        self.program2.draw('triangle_strip')
        self.program3.draw('triangle_strip')


def main(argv):
    argParser = argparse.ArgumentParser()
    argParser.add_argument("path", action="store", type=str, 
            help="path to either .sima folder or imaging sequence")
    args = argParser.parse_args(argv)
    path = args.path
    #path = '/Volumes/data/Nathan/2photon/rewardRemapping/nd125/02112015/day1-session-002/day1-session-002_Cycle00001_Element00001.h5'
    
    canvas = Canvas(path)
    canvas.show()
    app.run()

if __name__ == '__main__':
    main(sys.argv[1:])
