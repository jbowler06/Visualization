import sys
import argparse
import os.path

import numpy as np
from vispy import app, gloo, visuals

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
    def __init__(self, path, channel=0, start=0):
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
            self.sequence = ds.__iter__().next()
        else:
            self.sequence = Sequence.create('HDF5',path,'tzyxc')

        self.frame_counter = start
        self.step_size = 1
        self.channel = channel
        self.length = len(self.sequence)

        vol = self.sequence._get_frame(self.frame_counter).astype('float32')
        vol /= NORMING_VAL
        vol = np.clip(vol, 0, 1)

        surf = np.sum(vol,axis=0)[:,:,channel]/vol.shape[0]
        self.program['u_texture'] = surf
        
        surf2 = np.sum(vol,axis=1)[:,:,channel]/vol.shape[1]
        self.program2['u_texture'] = surf2

        surf3 = np.fliplr((np.sum(vol,axis=2)[:,:,channel]).T)/vol.shape[2]
        self.program3['u_texture'] = surf3

        self.text = visuals.TextVisual('',font_size=14,color='r',pos=(700, 700))
        self.text.text = "{} / {}".format(self.frame_counter, self.length)
        self.steptext = visuals.TextVisual('step_size: 1',font_size=10,color='r',pos=(700, 725))
        self.tr_sys = visuals.transforms.TransformSystem(self)

        self.timer = app.Timer(0.25, connect=self.on_timer, start=True)


    def on_key_press(self,event):
        if event.text == ' ' or event.text == 'p':
            if self.timer.running:
                self.timer.stop()
                self.steptext.text = "paused"
            else:
                self.timer.start()
                self.steptext.text = "step size: {}".format(self.step_size)
            self.update()
        
        if event.text == '.':
            if self.step_size == -1:
                self.step_size *= -1
            elif self.step_size > 0:
                self.step_size *= 2
            else:
                self.step_size /= 2
            self.steptext.text = "step size: {}".format(self.step_size)
            self.update()

        if event.text == ',':
            if self.step_size == 1:
                self.step_size /= -1
            elif self.step_size > 0:
                self.step_size /= 2
            else:
                self.step_size *= 2
            self.steptext.text = "step size: {}".format(self.step_size)
            self.update()



    def on_timer(self, event):
        self.frame_counter += self.step_size
        if self.frame_counter < 0 or self.frame_counter >= self.length:
            self.frame_counter -= self.step_size
            self.step_text.text = "end"
            return

        vol = self.sequence._get_frame(self.frame_counter).astype('float32')
        vol /= NORMING_VAL
        vol = np.clip(vol, 0, 1)

        surf = np.sum(vol,axis=0)[:,:,self.channel]/vol.shape[0]
        self.program['u_texture'] = surf

        surf = np.sum(vol,axis=1)[:,:,self.channel]/vol.shape[1]
        self.program2['u_texture'] = surf

        surf = np.fliplr((np.sum(vol,axis=2)[:,:,self.channel]).T)/vol.shape[2]
        self.program3['u_texture'] = surf

        self.text.text = "{} / {}".format(self.frame_counter, self.length)

        self.update()

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        gloo.clear('black')
        gloo.set_viewport(0, 0, *self.size)
        self.program.draw('triangle_strip')
        self.program2.draw('triangle_strip')
        self.program3.draw('triangle_strip')
        self.text.draw(self.tr_sys)
        self.steptext.draw(self.tr_sys)


def main(argv):
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-s', '--start_frame', action='store', type=int, default=0,
            help='starting frame for viewing the sequence')
    argParser.add_argument("path", action="store", type=str, 
            help="path to either .sima folder or imaging sequence")
    args = argParser.parse_args(argv)
    
    canvas = Canvas(args.path, start=args.start_frame)
    canvas.show()
    app.run()

if __name__ == '__main__':
    main(sys.argv[1:])
