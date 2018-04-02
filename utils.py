#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 11:13:24 2018

@author: omarschall
"""

from __future__ import division
import numpy as np

def get_annotation_resolution(array, coronal_slice=False):
    '''
    Accepts as an argument an array
    
    Returns the resolution of the data in microns based on the shape
    of the array.
    '''
    ccf_x_size = 13200
    ccf_y_size = 8000
    ccf_z_size = 11400
    
    if coronal_slice:
        return int(ccf_z_size/array.shape[-1])
    else:
        return int(ccf_x_size/array.shape[0])

def idx_to_ccf(idx, resolution):
    '''
    Accepts as an argument a list of 3 elements representing
    a (resolution-dependent) index for an array of a given
    resolution.
    
    Returns a ccf coordinate [AP, DV, ML] in microns.
    '''
    
    if type(idx)==list:
        return [int(q*resolution) for q in idx]
    if type(idx)==np.ndarray:
        return np.round(idx*resolution).astype(np.int)
    
def idx_to_idx(idx, res1, res2):
    '''
    Similar to ccf_to_idx() and idx_to_ccf(), translates directly between
    two resolution-dependent coordinate frames
    '''

    if type(idx)==list:
        return [int(q*res1/res2) for q in idx]
    if type(idx)==np.ndarray:
        return (idx*res1/res2).astype(np.int)
    
def get_blank_mask(res):
    
    base_dims = np.array([13200, 8000, 11400])
    dims = tuple((base_dims/res).astype(np.int))
    
    return np.zeros(dims)
    