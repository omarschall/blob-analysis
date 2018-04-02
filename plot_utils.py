#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 09:22:44 2017

@author: omarschall
"""

'''
PLOT UTILS

Functions useful for quickly visualizing 3D Allen data
'''


import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

class slice_image_array():
    '''
    An object for maintaining an adding to an array of slice images.
    '''
    
    def __init__(self, template, n_x, n_y, style='coronal', start=0, stop=None, plot_slice_index=True):
        
        self.n_x, self.n_y = n_x, n_y
        self.fig, self.axarr = plt.subplots(self.n_x, self.n_y)
        self.style = style
        self.start, self.stop = start, stop
        self.template = template
        
        if self.style=='coronal':
            self.n_z = self.template.shape[0]
        elif self.style=='horizontal':
            self.n_z = self.template.shape[1]
        elif self.style=='sagittal':
            self.n_z = self.template.shape[2]
        
        self.start_z = int(self.n_z*self.start)
        if self.stop is not None:
            self.n_z = int(self.n_z*(self.stop - self.start))       
        
        self.plot_images(template, plot_slice_index=plot_slice_index)
        
    def plot_images(self, voxel_array, cmap=plt.cm.gray, alpha=1, plot_slice_index=True,
                    vbounds=None):
        '''
        Plots an array of images from a voxel array, which has shape
        [AP, DV, ML]; origin in the most left, dorsal, anterior corner; and
        resolution given by the downloaded MouseConnectivityCache.
        '''
        
        for i in range(self.n_x):
            for j in range(self.n_y):
                
                k = self.n_x*i + j                      #Flatten index
                s = self.start_z + int(self.n_z/float(self.n_x*self.n_y)*k)
                if self.style=='coronal':
                    if vbounds is None:
                        self.axarr[i,j].imshow(voxel_array[s,:,:], cmap=cmap, alpha=alpha)
                    else:
                        self.axarr[i,j].imshow(voxel_array[s,:,:], vmin=vbounds[0], vmax=vbounds[1], cmap=cmap, alpha=alpha)
                elif self.style=='horizontal':
                    if vbounds is None:
                        self.axarr[i,j].imshow(voxel_array[:,s,:], cmap=cmap, alpha=alpha)
                    else:
                        self.axarr[i,j].imshow(voxel_array[:,s,:], vmin=vbounds[0], vmax=vbounds[1], cmap=cmap, alpha=alpha)
                elif self.style=='sagittal':
                    if vbounds is None:
                        self.axarr[i,j].imshow(voxel_array[:,:,s], cmap=cmap, alpha=alpha)
                    else:
                        self.axarr[i,j].imshow(voxel_array[:,:,s], vmin=vbounds[0], vmax=vbounds[1], cmap=cmap, alpha=alpha)
                self.axarr[i,j].set_xticks([])
                self.axarr[i,j].set_yticks([])
                if plot_slice_index:
                    if i==0 and j==0:
                        self.axarr[i,j].set_title('Slice index = '+str(s), fontsize=9)
                    else:
                        self.axarr[i,j].set_title(str(s), fontsize=9)
                
    def plot_scatter(self, points, marker='x', color='b'):
        '''
        Plots specific points in the resolution-dependent coordinate axis.
        
        The argument "points" should be a numpy array of shape [N, 3] where N
        is the number of points.
        '''
        
        for i in range(self.n_x):
            for j in range(self.n_y):
                
                k = self.n_x*i + j
                s = self.start_z + int(self.n_z/float(self.n_x*self.n_y)*k)
                if self.style=='coronal':
                    valid_pts = points[np.where(points[:,0]==s)[0],:]
                    self.axarr[i,j].scatter(valid_pts[:,2], valid_pts[:,1], marker=marker, color=color)
                elif self.style=='horizontal':
                    valid_pts = points[np.where(points[:,1]==s)[0],:]
                    self.axarr[i,j].scatter(valid_pts[:,2], valid_pts[:,0], marker=marker, color=color)
                elif self.style=='sagittal':
                    valid_pts = points[np.where(points[:,2]==s)[0],:]
                    self.axarr[i,j].scatter(valid_pts[:,1], valid_pts[:,0], marker=marker, color=color)
                    
                self.axarr[i,j].set_xticks([])
                self.axarr[i,j].set_yticks([])
                
def plot_projections_in_space(mcc, area_name, area_annotation, forward_proj_names, forward_proj_strengths, backward_projections, colors=['g', 'r']):
    '''
    
    '''
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    area_annotation = mask_annotation_by_hemisphere(area_annotation, 'left')
    area_cm = get_center_of_mass(mcc, 0, area_annotation)
    
    ax.scatter([area_cm[0]], [area_cm[1]], [area_cm[2]], linewidths=[10])
    
    for i, proj in enumerate(forward_projections):
        ax.plot()
        
        
    
    
    