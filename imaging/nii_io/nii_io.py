import os
import math
import numpy as np
import nibabel as nib

nii_io_cache_dir ="/tmp/"
nii_io_cache_name ="temp_"
nii_extension = ".nii"
nii_cache_curr_cnt = '0'
nii_io_path_cache_current_img = ""

def next_cache_path(reset=False):
    #nii_io_path_cache_current_img = nii_io_cache_dir+nii_io_cache_name+nii_cache_curr_cnt+nii_extension
    #nii_cache_curr_cnt=`int(nii_cache_curr_cnt)+1`
    #if reset:
    #    nii_cache_curr_cnt = '0'
    return nii_io_cache_dir+nii_io_cache_name+nii_extension

def basicLoadNii(nii_image_path, c_contiguos=True):
    img_ = nib.load(nii_image_path)
    img_data = img_.get_data()
    if c_contiguos and np.isfortran(img_data):
        img_data = img_data.T
    return (img_.header, img_.affine, img_data)

def loadNii(nii_image_path, c_contiguos=True, scale=1.0):
    """
    returns (header, affine, data_array).
    It performs the following operations:
        - voxel values are shifted to positive interval.
        - scaling is obtained by multiplying the 6 apposite values of the affine matrix.
        thus using /tmp storage to save transdormed image.
        http://nipy.org/nibabel/nifti_images.html#data-scaling
    note: returns numpy.memmap.
        http://docs.scipy.org/doc/numpy/reference/generated/numpy.memmap.html
    """
    img_ = nib.load(nii_image_path)
    if not scale == 1.0:
        affine_ = scale*(np.copy(img_.affine))
        data_ = img_.get_data()
        #restore translation
        #affine_[0,3] = img_.affine[0,3]
        #affine_[1,3] = img_.affine[1,3]
        #affine_[2,3] = img_.affine[2,3]
        img_ = apply_transformation(data_,affine_)
    img_data = img_.get_data()
    if c_contiguos and np.isfortran(img_data):
        img_data = img_data.T
    return (img_.header, img_.affine, img_data)

def saveNii(nii_image_path, array_data, affine_=np.eye(4, dtype=float), header_=None):
    array_img = nib.Nifti1Image(array_data, affine_, header_)
    nib.save(array_img, nii_image_path)

def apply_transformation(img_data,affine_):
    """
    This method applies transformation by saving temporary items in /tmp.
    Data returned will still point to data stored in the /tmp directory.
    This has 2 main consequences.
        - original data is not affected by the transformation.
        - you cannot completely rely on the data, either copy it or repeform transformation on original data.
    """
    path_ = next_cache_path()
    saveNii(path_ ,img_data, affine_)
    flipped_img = nib.load(path_)
    return flipped_img

def allPositive(array):
    return array + abs(array.min())

def getNumpyDataFormat(img):
    headerDataTypelabel = img.header['datatype']
    for i in range(0, len(nib.nifti1._dtdefs)):
        if nib.nifti1._dtdefs[i][0] == headerDataTypelabel:
            return nib.nifti1._dtdefs[i][2]

def niiToArray(niiImg, c_contiguos=True, canonical=False):
    if canonical:
        rough_data = nib.as_closest_canonical(niiImg).get_data()
    else:
        rough_data = niiImg.get_data()
    print np.isfortran(rough_data)
    #if c_contiguos and np.isfortran(rough_data):
    #    rough_data = rough_data.T
    if c_contiguos and not rough_data.flags['C_CONTIGUOUS']:
        rough_data = rough_data.T
    return rough_data

def old_niiToArray(niiImg, c_contiguos=True, canonical=False):
    passs
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
    return INroughData * scl_slope
