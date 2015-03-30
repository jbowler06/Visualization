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
import matplotlib
import matplotlib.cm

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

import random

def getSequence(directory):
    if (os.path.splitext(directory)[-1] == '.sima'):
        ds = ImagingDataset.load(directory)
        seq = ds.__iter__().next()
    else:
        seq = Sequence.create('HDF5',directory,'tzyxc')
    return seq


def convertList16(arr):
    conv = lambda x: [int('0'+hex(int(x+0.5))[2:][:-2],16),int(hex(int(x+0.5))[2:][-2:],16)]
    return list(it.chain(*map(conv,arr)))


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
    norm_factors = {}
    for channel in xrange(seq.shape[4]):
        norm_factors['channel_' + str(channel)] = []
    
    for frame_index in [0,int(length/2),-1]:
        frame = seq._get_frame(frame_index)
        for channel in xrange(seq.shape[4]):
            subframe = frame[:,:,:,channel]
            factor = np.percentile(subframe[np.where(np.isfinite(subframe))],98)
            if np.isfinite(factor):
                norm_factors['channel_'+str(channel)] += [factor]

    json = {
        'planes': range(seq.shape[1]+1),
        'height': seq.shape[2],
        'width': seq.shape[3],
        'max': length
    }

    for channel in norm_factors.keys():
        json[channel] = int(np.nanmean(norm_factors[channel]))

    return jsonify(**json)

@app.route('/getChannels/<directory>')
def getChannels(directory):
    ds_path = directory.replace(':!','/')

    if (os.path.splitext(ds_path)[-1] == '.sima'):
        ds = ImagingDataset.load(ds_path)
        channels = ds.channel_names
    else:
        seq = Sequence.create('HDF5',ds_path,'tzyxc')
        channels = ['channel_' + str(idx) for idx in range(seq.shape[4])]

    if (len(channels) > 1):
        channels += ['overlay']
    return render_template('select_list.html',options=channels) 


@app.route('/getLabels', methods=['GET','POST'])
def getLabels():
    ds_path = request.form.get('path')
    try:
        dataset = ImagingDataset.load(ds_path)
    except:
        return ''

    labels = dataset.ROIs.keys()
    return render_template('select_list.html',options=labels)


def convertToBin(arr):
    dat = arr.reshape((1,arr.shape[0]))

    img = Image.fromarray(dat.astype('uint8'),'L')
    strBuffer = StringIO.StringIO()
    img.save(strBuffer, 'png')
    strBuffer.seek(0)

    imageString = "data:image/png;base64,"+base64.b64encode(strBuffer.read())

    return (imageString)


@app.route('/getRois', methods=['GET','POST'])
def getRois():
    ds_path = request.form.get('path')
    label = request.form.get('label')   
    
    dataset = ImagingDataset.load(ds_path)
    convertedRois = {}
    rois = dataset.ROIs[label]
    for roi in rois:
        poly = roi.polygons[0]
        coords = []
        
        for x,y in zip(*poly.exterior.coords.xy):
            coords += [np.max((0,x)), np.max((0,y))]
            
        try:
            convertedRois[roi.label] = convertList16(coords)
        except:
            import pdb; pdb.set_trace()

    return jsonify(**convertedRois)

@app.route('/getFrames', methods=['GET','POST'])
def getFrames():
    ds_path = request.form.get('path')
    requestFrames = request.form.getlist('frames[]',type=int)
    normingVal = request.form.getlist('normingVal[]', type=float)
    sequenceId = request.form.get('sequenceId')
    channel = request.form.get('channel')
    planes = request.form.getlist('planes[]',type=int)
    if planes is None:
        planes = [0]

    quality = 40
    if channel == 'overlay':
        channel = None

    ds = None
    if (os.path.splitext(ds_path)[-1] == '.sima'):
        ds = ImagingDataset.load(ds_path)
        seq = ds.__iter__().next()
        channel = ds._resolve_channel(channel)
    else:
        seq = Sequence.create('HDF5',ds_path,'tzyxc')
        if channel:
            channel = int(channel.split('_')[-1])

    end = False
    frames = {}
    for frame_number in requestFrames:
        norming_val = normingVal[:]
        if frame_number > len(seq)-1 or frame_number < -1:
            end = True
            continue
        elif frame_number == -1 and ds is not None:
            vol = ds.time_averages
            for channel in xrange(vol.shape[3]):
                subframe = vol[:,:,:,channel]
                factor = np.nanmax(subframe)
                if np.isfinite(factor):
                    norming_val[channel] = factor
            end = True
        else:
            vol = seq._get_frame(frame_number)

        if channel is not None:
            vol = vol[:,:,:,channel]
            vol /= ((norming_val[channel])/255)
            vol = np.clip(vol, 0, 255)
        else:
            vol = np.hstack((vol[:,:,:,0]/norming_val[0],vol[:,:,:,1]/norming_val[1]))
            vol*=255
        frames['frame_'+str(frame_number)] = {};
        
        for plane in planes:
            if plane == 0:
                zsurf = np.nanmean(vol,axis=0)
            else:
                zsurf = vol[plane-1,:,:]
            img = Image.fromarray(zsurf.astype('uint8'),'L')
            img_io_z = StringIO.StringIO()
            img.save(img_io_z, 'jpeg', quality=quality)
            img_io_z.seek(0)

            if plane == 0:
                ysurf = np.nanmean(vol,axis=1)
            else:
                ysurf = np.zeros((vol.shape[0],vol.shape[2]))
                ysurf[plane-1,:]=np.nanmean(zsurf,axis=0)
            img = Image.fromarray(ysurf.astype('uint8'),'L')
            img_io_y = StringIO.StringIO()
            img.save(img_io_y, 'jpeg', quality=quality)
            img_io_y.seek(0)

            if plane == 0:
                xsurf = np.nanmean(vol,axis=2).T
            else:
                xsurf = np.zeros((vol.shape[1],vol.shape[0]))
                xsurf[:,plane-1]=np.nanmean(zsurf,axis=1).T
            img = Image.fromarray(xsurf.astype('uint8'),'L')
            img_io_x = StringIO.StringIO()
            img.save(img_io_x, 'jpeg', quality=quality)
            img_io_x.seek(0)
            
            frames['frame_'+str(frame_number)][plane] = {
                'z':base64.b64encode(img_io_z.read()),
                'y':base64.b64encode(img_io_y.read()),
                'x':base64.b64encode(img_io_x.read())
            }

    return jsonify(end=end,sequenceId=sequenceId,**frames)


@app.route('/getFolders/<directory>')
def getFolders(directory):
    directory = directory.replace(':!','/')
    subfolders = [os.path.basename(fname) for fname in
        glob.glob(os.path.join(directory,'*')) if os.path.isdir(fname) or os.path.splitext(fname)[-1] =='.h5']
    subfolders = ['']+sorted(subfolders)
    return render_template('select_list.html',options=subfolders) 

@app.route('/saveImage', methods=['GET','POST'])
def saveImage():
    image = request.form.get('image')
    filename = request.form.get('filename')
    fh = open("/home/jack/movie/"+filename, "wb")
    fh.write(image.decode('base64'))
    fh.close()
    return jsonify(status='complete')
