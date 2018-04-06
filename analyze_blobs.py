#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 17:09:13 2018

@author: omarschall
"""

from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import pickle
from skimage import io
import os
import sys
import h5py
from utils import *
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache

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

class Blob():
    
    def __init__(self, mask, name='Blob1'):
        '''
        Initiate with a 3D mask indicating where the points should be.
        '''
        
        self.resolution     = get_annotation_resolution(mask)
        self.mask           = mask
        self.points         = np.array(np.where(mask>0)).T
        self.name           = name
        self.params         = {'blob_resolution' : get_annotation_resolution(mask)}
        
    def get_cuboids(self, cuboid_side=500, large_cuboid_side=600, frac_in_blob=1):
        
        self.cuboid_side        = cuboid_side
        self.large_cuboid_side  = large_cuboid_side
        self.frac_in_blob       = frac_in_blob
        
        self.params['cube_side']        = cuboid_side
        self.params['large_cube_side']  = large_cuboid_side
        self.params['frac_in_blob']     = frac_in_blob
        
        leftovers = np.copy(self.mask)
        cuboid_mask = np.zeros_like(self.mask)
        cuboid_points = []
        n = int(np.round((cuboid_side/self.resolution)/2))
        self.n = n
        n_big = int((large_cuboid_side/self.resolution)//2)
        
        stop_cond = False
        while not stop_cond:
            
            stop_cond = True
            
            for k in range(self.points.shape[0]):

                x, y, z = self.points[k,:]
                
                big_cuboid = leftovers[x-n_big:x+n_big, y-n_big:y+n_big, z-n_big:z+n_big]
                
                if np.sum(big_cuboid)/big_cuboid.size >= frac_in_blob:
                    continue
                
                cuboid = leftovers[x-n:x+n, y-n:y+n, z-n:z+n]
                
                if np.sum(cuboid)/cuboid.size >= frac_in_blob:
                    cuboid_points.append([x, y, z])
                    leftovers[x-n:x+n, y-n:y+n, z-n:z+n] = 0
                    cuboid_mask[x-n:x+n, y-n:y+n, z-n:z+n] = 1
                    stop_cond = False
                    
        self.cuboid_mask = cuboid_mask
        self.cuboid_points = np.array(cuboid_points)

    def get_ccf_and_stereotaxic_coordinates(self, f_transform):
        
        self.cuboid_ccf_coords = np.array([idx_to_ccf(cuboid_point, self.resolution) for cuboid_point in self.cuboid_points])
        self.cuboid_stx_coords = np.array([np.round(f_transform(ccf_coord), 2) for ccf_coord in self.cuboid_ccf_coords])
        
    def get_signal_strength(self, proj_data):
        
        #Get data in correct forma
        if type(proj_data)==str:
            f = h5py.File(proj_data, 'r')
            proj_res = int(13200/f['proj_values'].shape[0])
            X = f['proj_values']
        elif type(proj_data)==np.ndarray:
            X = proj_data
            proj_res = get_annotation_resolution(X)
        else:
            raise TypeError("'proj_data' must either be a path to h5py file or numpy array")
        
        n = int(np.round((self.cuboid_side/proj_res)/2))
        self.cuboid_strengths = []
        
        for [x, y, z] in self.cuboid_points:
            
            #Transform into coordinates of projection data
            x_, y_, z_ = idx_to_idx([x, y, z], self.resolution, proj_res)
            self.cuboid_strengths.append(X[x_-n:x_+n, y_-n:y_+n, z_-n:z_+n].mean())
        
        try:
            f.close()
        except UnboundLocalError:
            pass
            
    def get_anatomical_info(self):
        
        manifest_path = './connectivity/mouse_connectivity_manifest.json'
        mcc = MouseConnectivityCache(resolution=self.resolution, manifest_file=manifest_path)
        tree = mcc.get_structure_tree()
        annotation, _ = mcc.get_annotation_volume()
            
        self.areas_in_blob = list(set([tree.get_structures_by_id([i])[0]['acronym'] for i in annotation[np.where(self.mask>0)] if i>0]))
        
        self.cuboid_center_areas = [tree.get_structures_by_id([i])[0]['acronym'] for i in annotation[tuple(self.cuboid_points.T)] if i>0]
        
    def write_blob_to_excel_sheet(self, workbook, name='results.xlsx'):
        
        #Hyperparameters sheet
        workbook.create_sheet(self.name+' params')
        sheet = workbook.get_sheet_by_name(self.name+' params')
        
        for i, key in enumerate(self.params.keys()):
            
            sheet.cell(row=i+1, column=1).value = key
            sheet.cell(row=i+1, column=2).value = self.params[key]
        
        #Results sheet
        workbook.create_sheet(self.name)
        sheet = workbook.get_sheet_by_name(self.name)
        
        sheet.cell(row=1, column=1).value = 'Cube Index'
        sheet.cell(row=1, column=2).value = 'Cube Center Area'
        sheet.cell(row=1, column=3).value = 'Cube CCF (AP)'
        sheet.cell(row=1, column=4).value = 'Cube CCF (DV)'
        sheet.cell(row=1, column=5).value = 'Cube CCF (ML)'
        sheet.cell(row=1, column=6).value = 'Cube Stereotaxic (AP)'
        sheet.cell(row=1, column=7).value = 'Cube Stereotaxic (DV)'
        sheet.cell(row=1, column=8).value = 'Cube Stereotaxic (ML)'
        sheet.cell(row=1, column=9).value = 'Relative projection strength'
        
        for i_cube in range(len(self.cuboid_center_areas)):
            
            sheet.cell(row=i_cube+2, column=1).value = i_cube
            sheet.cell(row=i_cube+2, column=2).value = self.cuboid_center_areas[i_cube]
            sheet.cell(row=i_cube+2, column=3).value = self.cuboid_ccf_coords[i_cube][0]
            sheet.cell(row=i_cube+2, column=4).value = self.cuboid_ccf_coords[i_cube][1]
            sheet.cell(row=i_cube+2, column=5).value = self.cuboid_ccf_coords[i_cube][2]
            sheet.cell(row=i_cube+2, column=6).value = self.cuboid_stx_coords[i_cube][0]
            sheet.cell(row=i_cube+2, column=7).value = self.cuboid_stx_coords[i_cube][1]
            sheet.cell(row=i_cube+2, column=8).value = self.cuboid_stx_coords[i_cube][2]
            sheet.cell(row=i_cube+2, column=9).value = self.cuboid_strengths[i_cube]
            
        workbook.save(name)
            
        
        
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
