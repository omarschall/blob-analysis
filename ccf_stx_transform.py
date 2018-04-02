#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 17:13:24 2018

@author: omarschall
"""

from __future__ import division
import numpy as np

M, b = [np.array([[ 9.5521161e+02, -6.7981140e+01,  4.8597738e-02],
                  [ 6.2880299e+01,  9.1714026e+02, -1.8200886e+01],
                  [-2.8511507e+01,  1.3497596e+01,  9.6519373e+02]], dtype=np.float32),
        np.array([5318.8037, 1457.4587, 5820.442], dtype=np.float32)]

def stx_to_ccf(x):
    
    x = np.array(x)
    
    return np.dot(x, M) + b

def ccf_to_stx(y, invert_AP=True):
    
    y = np.array(y)
    
    M_inv = np.linalg.inv(M)
    
    x = np.dot(y - b, M_inv)
    
    if invert_AP:
        try:
            x[:,0] *= -1
        except IndexError:
            x[0] *= -1
    
    return x