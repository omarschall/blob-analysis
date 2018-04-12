#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 11:13:24 2018

@author: omarschall
"""

from __future__ import division
import numpy as np
import os
from PIL import Image
from skimage import io

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

def array_to_stack(array, stack_dir, binary=False):
    
    X = (array==0).astype(np.uint8)
    
    if not os.path.exists(stack_dir):
        os.mkdir(stack_dir)
    else:
        raise ValueError('An image stack with that path already exists.')

    for i in range(array.shape[0]):
        
        im = Image.fromarray((X[i,:,:]*255).astype(np.uint8), mode='L')
        im.save(os.path.join(stack_dir, 'mask-'+str(i+1).zfill(4)+'-0.png'))
    
def load_blob_mask(dir_path):
    
    slices = []
    i_xs = []
    for i, file_name in enumerate(sorted(os.listdir(dir_path))):
            
        i_xs.append(int(file_name.split('-')[1]))    
        
        im = io.imread(os.path.join(dir_path, file_name))
        
        #If the last two images are at the same AP coordinate, just combine them
        try:
            cond = i_xs[-1]==i_xs[-2]
        except IndexError:
            cond = False
        
        if cond:
            slices[-1] = ((slices[-1] + (im==0))>0).astype(np.int8)
        else:
            slices.append((im==0).astype(np.int8))
            
        if i==0:
            res = get_annotation_resolution(array=im, coronal_slice=True)
            
            
    i_start_x = min(i_xs) - 1
    i_stop_x  = max(i_xs)
    total_slices = int(13200/res)
    
    #print len(slices)
    
    for i in range(i_start_x):
        
        slices = [np.zeros_like(im)] + slices
        
    #print len(slices)
    
    for i in range(i_stop_x, total_slices):
        
        slices = slices + [np.zeros_like(im)]
    
    #print len(slices)
    
    blob_mask = np.array(slices)
    
    return blob_mask

def downsample_blob_mask(blob_mask, target_res=100):
    
    blob_points = np.array(np.where(blob_mask>0)).T
    
    res = get_annotation_resolution(blob_mask)
    
    new_blob_points = tuple(idx_to_idx(blob_points, res, target_res).T)
    new_blob_mask = get_blank_mask(target_res)
    new_blob_mask[new_blob_points] = 1
    
    return new_blob_mask

def AND_masks(dirs_list):
    
    arrays = [load_blob_mask(dir_path) for dir_path in dirs_list]
    
    #Set each mask's resolution to the lowest-resolution mask
    if len(set([get_annotation_resolution(array) for array in arrays]))>1:
        max_res = max([get_annotation_resolution(array) for array in arrays])
        arrays = [downsample_blob_mask(array, target_res=max_res) for array in arrays]
        
    result = np.ones_like(arrays[0])
    for array in arrays:
        result *= array
    
    return result
        
def OR_masks(dirs_list):
    
    arrays = [load_blob_mask(dir_path) for dir_path in dirs_list]
    
    #Set each mask's resolution to the lowest-resolution mask
    if len(set([get_annotation_resolution(array) for array in arrays]))>1:
        max_res = max([get_annotation_resolution(array) for array in arrays])
        arrays = [downsample_blob_mask(array, target_res=max_res) for array in arrays]
        
    result = np.zeros_like(arrays[0])
    for array in arrays:
        result += array
    
    return (result>0).astype(np.int8)
    
def subtract_masks(dir1, dir2):
    '''
    Returns a mask where the image stack in dir1 is active but not
    that in dir2, i.e. dir1 - dir2.
    '''
    
    array1, array2 = load_blob_mask(dir1), load_blob_mask(dir2)
    
    res1, res2 = get_annotation_resolution(array1), get_annotation_resolution(array2)
    if not res1==res2:
        max_res = max([res1, res2])
        array1, array2 = [downsample_blob_mask(array, target_res=max_res) for array in [array1, array2]]
        
    result = ((array1 - array2)>0).astype(np.int8)
    
    return result
        
        
    
    














    