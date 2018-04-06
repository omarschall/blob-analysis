#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 10:35:37 2018

@author: omarschall
"""
from __future__ import division
import numpy as np
import pickle
import argparse
import h5py
import os

from analyze_blobs import *
from ccf_stx_transform import *
from plot_utils import *
from openpyxl import Workbook

parser = argparse.ArgumentParser()
parser.add_argument('--masks_dir', help='The directory with the mask image files for the blob',
                    default='blob_masks')
parser.add_argument('--data_path', help='Path the data comes from for calculating cube strengths',
                    default='./data/575_ant_res=20um')
parser.add_argument('--save_path', help='Path for saving the excel sheet with the results',
                    default='./results/output_blobs.xlsx')
parser.add_argument('--frac_in_blob', help='Fraction of each cube required to both ' + \
                    'be in the parcellation and not overlap with other cubes.',
                    default=1)
parser.add_argument('--downsample_res', help='Resolution of the blob space',
                    default=50)
parser.add_argument('--cube_side', help='Length of each cube side in microns. '+\
                    'Recommend being an integer multiple of downsample_res.',
                    default=500)
parser.add_argument('--large_cube_side', help='Length of larger cubes used to ' +\
                    'make packing more efficient.',
                    default=600)

args = parser.parse_args()

wb = Workbook()
wb.remove_sheet(wb.get_active_sheet())

for mask_dir in os.listdir(args.masks_dir):

    print 'Loading '+mask_dir.split('_')[0]+' mask...'
    
    blob_mask = load_blob_mask(os.path.join(args.masks_dir, mask_dir))
    ds_blob_mask = downsample_blob_mask(blob_mask, target_res=args.downsample_res)
    
    #Define a blob object from this segmentation
    blob = Blob(ds_blob_mask, name=mask_dir[:-5])
    
    #Perform all the calculations
    print 'Finding cubes...'
    blob.get_cuboids(cuboid_side=float(args.cube_side),
                     large_cuboid_side=float(args.large_cube_side),
                     frac_in_blob=float(args.frac_in_blob))
    blob.get_ccf_and_stereotaxic_coordinates(ccf_to_stx)
    
    print 'Calculating cube strength...'
    blob.get_signal_strength(args.data_path)
    
    blob.get_anatomical_info()
    blob.write_blob_to_excel_sheet(wb, name=args.save_path)
    print 'Blob saved to excel sheet'
    print ' '