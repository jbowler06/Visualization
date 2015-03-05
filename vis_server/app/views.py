from app import app
import config

from sys import path
import numpy as np
import traceback
path.insert(0,config.analysis)
path.insert(0,config.analysis+'/automaticScripts')

import os.path
import itertools as it
import glob
import cPickle as pickle
import base64
import urllib

from flask import render_template
from flask import request
from flask import jsonify
from flask import url_for
from flask import send_file
from flask import send_from_directory
from flask import make_response

from .decorators import async
from sima import ImagingDataset
from sima import Sequence

from PIL import Image
import StringIO
import struct

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/getInfo', methods=['GET','POST'])
def getInfo():
    ds_path = request.form.get('path')
    if (os.path.splitext(ds_path)[-1] == '.sima'):
        ds = ImagingDataset.load(ds_path)
        seq = ds.__iter__().next()
    else:
        seq = Sequence.create('HDF5',ds_path,'tzyxc')

    length = len(seq)
    frames = []
    for frame_index in [0,int(length/2),-1]:
        frame = seq._get_frame(frame_index)
        if len(frame[np.where(np.logical_not(np.isnan(frame)))]) > 0:
            frames += [np.percentile(frame[np.where(np.logical_not(np.isnan(frame)))],95)]

    normalizingVal = np.nanmean(frames)

    return jsonify(max=length, normalizingValue=int(normalizingVal), 
                   height=seq.shape[2],width=seq.shape[3])

@app.route('/getChannels/<directory>')
def getChannels(directory):
    ds_path = directory.replace(':!','/')

    if (os.path.splitext(ds_path)[-1] == '.sima'):
        ds = ImagingDataset.load(ds_path)
        channels = ds.channel_names
    else:
        seq = Sequence.create('HDF5',ds_path,'tzyxc')
        channels = ['channel_' + str(idx) for idx in range(seq.shape[4])]

    return render_template('select_list.html',options=channels) 


@app.route('/getFrame/<frame_number>', methods=['GET','POST'])
def getFrame(frame_number):
    ds_path = '/data/Nathan/2photon/rewardRemapping/nd125/02112015/day1-session-003/day1-session-003.sima'
    NORMING_VAL = 2194/255
    channel = 0
    ds = ImagingDataset.load(ds_path)
    seq = ds.__iter__().next()
    vol = seq._get_frame(int(frame_number))
    vol /= NORMING_VAL
    vol = np.clip(vol, 0, 255)

    surf = np.nanmean(vol,axis=0)[:,:,channel]
    img = Image.fromarray(surf.astype('uint8'),'L')
    img_io_z = StringIO.StringIO()
    img.save(img_io_z, 'jpeg', quality=40)
    img_io_z.seek(0)

    surf = np.nanmean(vol,axis=1)[:,:,channel]
    img = Image.fromarray(surf.astype('uint8'),'L')
    img_io_y = StringIO.StringIO()
    img.save(img_io_y, 'jpeg', quality=40)
    img_io_y.seek(0)

    surf = np.fliplr(np.nanmean(vol,axis=2)[:,:,channel].T)
    img = Image.fromarray(surf.astype('uint8'),'L')
    img_io_x = StringIO.StringIO()
    img.save(img_io_x, 'jpeg', quality=40)
    img_io_x.seek(0)

    return jsonify(
        z_projection=base64.b64encode(img_io_z.read()),
        y_projection=base64.b64encode(img_io_y.read()),
        x_projection=base64.b64encode(img_io_x.read()))

@app.route('/getFrames', methods=['GET','POST'])
def getFrames():
    ds_path = request.form.get('path')
    step = request.form.get('frameDelta', type=int)
    requestFrames = request.form.get('frames').split(',')
    norming_val = request.form.get('normingVal', type=int)/255
    channel = request.form.get('channel')
    if (os.path.splitext(ds_path)[-1] == '.sima'):
        ds = ImagingDataset.load(ds_path)
        seq = ds.__iter__().next()
        channel = ds._resolve_channel(channel)
    else:
        seq = Sequence.create('HDF5',ds_path,'tzyxc')
        channel = int(channel.split('_')[-1])

    end = False
    frames = {}
    for frame_number in requestFrames:
        frame_number = int(frame_number)
        if frame_number > len(seq)-1 or frame_number < 0:
            end = True
            continue

        vol = seq._get_frame(frame_number)
        vol /= norming_val
        vol = np.clip(vol, 0, 255)
        surf = np.nanmean(vol,axis=0)[:,:,channel]
        img = Image.fromarray(surf.astype('uint8'),'L')
        img_io_z = StringIO.StringIO()
        img.save(img_io_z, 'jpeg', quality=40)
        img_io_z.seek(0)

        surf = np.nanmean(vol,axis=1)[:,:,channel]
        img = Image.fromarray(surf.astype('uint8'),'L')
        img_io_y = StringIO.StringIO()
        img.save(img_io_y, 'jpeg', quality=40)
        img_io_y.seek(0)

        surf = np.fliplr(np.nanmean(vol,axis=2)[:,:,channel].T)
        img = Image.fromarray(surf.astype('uint8'),'L')
        img_io_x = StringIO.StringIO()
        img.save(img_io_x, 'jpeg', quality=40)
        img_io_x.seek(0)
        
        frames['frame_'+str(frame_number)] = {
            'z':base64.b64encode(img_io_z.read()),
            'y':base64.b64encode(img_io_y.read()),
            'x':base64.b64encode(img_io_x.read())
        }

    return jsonify(end=end,**frames)

@app.route('/getFolders/<directory>')
def getFolders(directory):
    directory = directory.replace(':!','/')
    subfolders = [os.path.basename(fname) for fname in
        glob.glob(os.path.join(directory,'*')) if os.path.isdir(fname) or os.path.splitext(fname)[-1] =='.h5']
    subfolders = ['']+subfolders
    return render_template('select_list.html',options=subfolders) 

@app.route('/saveImage', methods=['GET','POST'])
def saveImage():
    image = request.form.get('image')
    filename = request.form.get('filename')
    fh = open("/home/jack/movie/"+filename, "wb")
    fh.write(image.decode('base64'))
    fh.close()
    return jsonify(status='complete')
