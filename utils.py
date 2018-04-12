#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 11:13:24 2018

@author: omarschall
"""

from __future__ import division
import numpy as np
import os

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

def array_to_stack(array, stack_dir, overwrite=False):
    
    res = get_annotation_resolution(array)
    
    if not os.path.exists(stack_dir):
        os.mkdir(stack_dir)
    elif overwrite:
        os.rmdir(stack_dir)
        os.mkdir(stack_dir)
    else:
        raise ValueError('An image stack already exists, set overwrite to True.')

def load_blob_mask(dir_path):
    
    slices = []
    i_xs = []
    for i, file_name in enumerate(sorted(os.listdir(dir_path))):
            
        i_xs.append(int(file_name.split('-')[1]))    
        
        im = io.imread(os.path.join(dir_path, file_name))
        slices.append(im==0)
        
        if i==0:
            res = get_annotation_resolution(array=im, coronal_slice=True)
            
    i_start_x = min(i_xs) - 1
    i_stop_x  = max(i_xs)
    total_slices = int(13200/res)
    
    for i in range(i_start_x):
        
        slices = [np.zeros_like(im)] + slices
        
    for i in range(i_stop_x, total_slices):
        
        slices = slices + [np.zeros_like(im)]
        
    blob_mask = np.array(slices)
    
    return blob_mask

def downsample_blob_mask(blob_mask, target_res=100):
    
    blob_points = np.array(np.where(blob_mask>0)).T
    
    res = get_annotation_resolution(blob_mask)
    
    new_blob_points = tuple(idx_to_idx(blob_points, res, target_res).T)
    new_blob_mask = get_blank_mask(target_res)
    new_blob_mask[new_blob_points] = 1
    
    return new_blob_mask

def combine_masks(dirs_list):
    
    
    
    














    