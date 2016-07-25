from __future__ import print_function
import os
if  os.environ['PWD'] not in os.environ['PATH']:
    os.environ['OLD_PATH'] = os.environ['PATH']
    os.environ['PATH'] += ":" + os.environ['PWD']

import math
import operator
import bisect
import numpy as np
import nii_maths
import nii_utils as utils
import copy

class Maximizator:

    def __init__(self,W,N):
        self.__W = W
        self.__N = N
        self.patternBank = None

    @property
    def patternBank(self):
        return self.__patternbank

    def maxim(self, bh, W=None, N=None):
        """
        Applies a feature reduction filter based on a entropy maximization
        with linear constratint of W weighet frequency, and N spatial constratint
        """
        if not W == None:
            self.__W = W
        if not N == None:
            self.__N = N
        patternBank = {}
        assert isinstance(bh,nii_maths.binnedHistogram), "must pass a BinnedHistogram."
        offset = bh.precision
        X = copy.deepcopy(bh.X)
        Y = copy.deepcopy(bh.Y)
        exL, exR = (X[0] , X[len(X)-1])
        Il = Ir = cusp = math.log(self.__W/float(self.__N))
        selL = selR = count = 0
        while count < self.__N and not (Il<exL and Ir>exR):
            Il = Il - offset
            Ir = Ir + offset
            i, j = selL, selR = (bisect.bisect_right(X,Il), bisect.bisect_right(X,Ir))
            while i < selR and count < self.__N:
                count += Y[i]
                patternBank[X[i]] = bh.MAP[X[i]]
                i += 1
            del X[selL:i+1]
            del Y[selL:i+1]
        del X
        del Y
        self.__patternbank = patternBank
        return self.__patternbank

class Compressor:

    def __init__(self, sampler, patternBank):
        assert isinstance(sampler,Sampler), "must pass a Sampler."
        cond0 = all(isinstance(n, int) for n in patternBank)
        cond1 = all(isinstance(n, long) for n in patternBank)
        assert cond0 or cond1, "patternBank must be <list> of <int> or <long>"
        self.__sampler = sampler
        self.__patternbank = patternBank

    @property
    def sampler(self):
        return self.__sampler

    def compress3D(self, image, encode_extremes=False, verbose=False, shape=None):
        if not len(image.shape) == 3:
            raise ValueError("Must provide 3D image")
        if verbose:
            print('start')
        patchside = self.__sampler.patchside
        bitDepth = self.__sampler.bitDepth
        thrss = self.__sampler.thrss
        patternbank = self.__patternbank
        shape_ = image.shape
        if not shape == None:
            shape_ = shape
        x,y,z = shape_
        if x < patchside or y < patchside or z <patchside:
            raise ValueError("Must provide shape with at least the same size of patchside**3")
        imageCopy = np.reshape(nii_maths.thressholding(image.ravel(), thrss),(x,y,z))
        ########################################################################
        if encode_extremes:
            for i in range(x):
                for j in range(y):
                    for k in range(z):
                        if imageCopy[i,j,k] == len(thrss):
                            imageCopy[i,j,k]=0
            if 2**bitDepth == len(thrss):
                bitDepth -= 1
        ########################################################################
        blankimageCopy = np.zeros(shape_)
        for i in range(x - patchside + 1):
            for j in range(y - patchside + 1):
                for k in range(z - patchside + 1):
                    key = nii_maths.patternKey(bitDepth, imageCopy[i:i + patchside, j:j + patchside, k:k + patchside])
                    if key in patternbank:
                        blankimageCopy[i:i + patchside, j:j + patchside, k:k + patchside] = imageCopy[i:i + patchside, j:j + patchside, k:k + patchside]
            if verbose:
                print ("\rprogress: ", int(((i+1)/float(x-patchside+1))*100), "%" , end="")
        if verbose:
            print ('\nended')
        return blankimageCopy

class Sampler:
    """
    Sampling is a 2 parts process:
    First data is downsampled according to thresholds,
    there are 2 possible way to down sample data.
        1 - thresholds are applied straightforward.
        an example can clarify:
        dwnsampl [0.9, 2.2, 5.1] using [1,2,3] = [0,2,3]
        2 - thresholds will encode extremes as zeroes:
        an example can clarify:
        dwnsampl [0.9, 2.2, 5.1] using [1,2,3] = [0,2,0]
        this method follows an entropy-like shape (nothing and everything are equally informative).
    Second each subspace [0-patchside]**n (n is either 2 or 3) samples the [0-x] x [0-y] x [0-z] downsampled space and it's ecoded in
    a single natural number.
    """
    def __init__(self, patchside, thrss):
        self.__patchside = patchside
        self.__thrss = thrss
        self.__bitDepth =int(math.ceil(math.log(len(self.__thrss)+1,2)))

    @property
    def patchside(self):
        return self.__patchside

    @property
    def thrss(self):
        return self.__thrss

    @property
    def bitDepth(self):
        return self.__bitDepth

    def sample3Din2Dslices(self, image, direction=0, verbose=False):
        """
            Sample 3D array of data as 2D slices, direction will tell the axis
            orthogonal to the 2D patches planes (independet).
        """
        x, y, z = image.shape
        sample = curr_sample = {}
        if direction == 0:
            for i in range(x):
                curr_sample = self.sample2D(image[i,:,:],verbose)
                sample = nii_maths.mergedicts(sample,curr_sample)
        elif direction == 1:
            for j in range(y):
                curr_sample = self.sample2D(image[:,j,:],verbose)
                sample = nii_maths.mergedicts(sample,curr_sample)
        elif direction == 2:
            for k in range(y):
                curr_sample =self.sample2D(image[:,:,k],verbose)
                sample = nii_maths.mergedicts(sample,curr_sample)
        return sample

    def sample2D(self, image, verbose=False):
        """
            Sample 2D array of data
        """
        if not len(image.shape) == 2:
            raise ValueError("must provide 2D images")
        if not math.ceil(math.log(len(self.__thrss)+1,2)) == self.__bitDepth:
            raise ValueError("incompatible thresholds and bitDepth")
        if verbose:
            print('start')
        patchside = self.__patchside
        thrss = self.__thrss
        bitDepth = self.__bitDepth
        x,y = image.shape
        imageCopy = np.reshape(nii_maths.thressholding(image.ravel(), thrss),(x,y))
        freqHistogram = {}
        for i in range(x - patchside + 1):
            for j in range(y - patchside + 1):
                key = nii_maths.patternKey(bitDepth, imageCopy[i:i + patchside, j:j + patchside] )
                if key in freqHistogram:
                    freqHistogram[key] += 1
                else:
                    freqHistogram.update({key: 1})
            if verbose:
                print ("\rprogress: ", int(((i+1)/float(x-patchside+1))*100), "%" , end="")
        ret = { k : float(v) for k,v in freqHistogram.items() }
        if verbose:
            print ('\nended')
        return ret

    def sample3D(self, image, encode_extremes=False, verbose=False):
        """
            Sample 3D array of data
        """
        if not len(image.shape) == 3:
            raise ValueError("must provide 3D images")
        if not math.ceil(math.log(len(self.__thrss)+1,2)) == self.__bitDepth:
            raise ValueError("incompatible thresholds and bitDepth")
        if verbose:
            print('start')
        patchside = self.__patchside
        thrss = self.__thrss
        bitDepth = self.__bitDepth
        x, y, z = image.shape
        imageCopy = np.reshape(nii_maths.thressholding(image.ravel(), thrss),(x,y,z))
        ########################################################################
        if encode_extremes:
            for i in range(x):
                for j in range(y):
                    for k in range(z):
                        if imageCopy[i,j,k] == len(thrss):
                            imageCopy[i,j,k]=0
            if 2**bitDepth == len(thrss):
                bitDepth -= 1
        ########################################################################
        freqHistogram = {}
        for i in range(x - patchside + 1):
            for j in range(y - patchside + 1):
                for k in range(z - patchside + 1):
                    key = nii_maths.patternKey(bitDepth, imageCopy[i:i + patchside, j:j + patchside, k:k + patchside] )
                    if key in freqHistogram:
                        freqHistogram[key] += 1
                    else:
                        freqHistogram.update({key: 1})
            if verbose:
                print ("\rprogress: ", int(((i+1)/float(x-patchside+1))*100), "%" , end="")
        ret = { k : float(v) for k,v in freqHistogram.items() }
        if verbose:
            print ('\nended')
        return ret
