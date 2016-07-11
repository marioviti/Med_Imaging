import os
import math
import numpy as np
import nibabel as nib

def allPositive(array):
    return array + abs(array.min())

def loadNii(niiImagePath, c_contiguos=True, canonical=False):
    image = nib.load(niiImagePath)
    return allPositive( niiToArray(image, c_contiguos, canonical) )

def getNumpyDataFormat(img):
    headerDataTypelabel = img.header['datatype']
    for i in range(0, len(nib.nifti1._dtdefs)):
        if nib.nifti1._dtdefs[i][0] == headerDataTypelabel:
            return nib.nifti1._dtdefs[i][2]

def niiToArray(niiImg, c_contiguos=True, canonical=False):
    dataType = getNumpyDataFormat(niiImg)
    sizeof_hdr = niiImg.header['sizeof_hdr']
    scl_slope = niiImg.header['scl_slope']
    scl_inter = niiImg.header['scl_inter']
    if math.isnan(sizeof_hdr):
        sizeof_hdr = 1
    if math.isnan(scl_slope):
        scl_slope = 1
    if math.isnan(scl_inter):
        scl_inter = 0
    if canonical:
        aligendImage = nib.as_closest_canonical(niiImg)
    else:
        aligendImage = niiImg
    INroughData = aligendImage.get_data()
    if c_contiguos and not INroughData.flags['C_CONTIGUOUS']:
        INroughData = INroughData.T
    return INroughData * scl_slope + scl_inter
