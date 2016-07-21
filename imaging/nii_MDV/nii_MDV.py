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

class filter:

    def __init__(self):
        self.__W = None
        self.__N = None
        self.patternBank = None

    @property
    def patternBank(self):
        return self.__patternbank

    def apply(self, bh, W, N):
        """
        apply a feature reduction filter based on a entropy maximization with linear constratint of W weighet frequency, and N spatial constratint
        """
        self.__W = W
        self.__N = N
        patternBank = {}
        assert isinstance(bh,nii_maths.binnedHistogram), "must pass a BinnedHistogram."
        offset = bh.precision
        X = bh.X
        Y = bh.Y
        exL, exR = (X[0] , X[len(X)-1])
        Il = Ir = cusp = math.log(W/float(N))
        selL = selR = count = 0
        while count < N and not (Il<exL and Ir>exR):
            Il = Il - offset
            Ir = Ir + offset
            i, j = selL, selR = (bisect.bisect_right(X,Il), bisect.bisect_right(X,Ir))
            while i < selR and count < N:
                count += Y[i]
                patternBank[X[i]] = bh.MAP[X[i]]
                i += 1
            del X[selL:i+1]
            del Y[selL:i+1]
        self.__patternbank = nii_maths.binnedHistogram(bh.precision,bh.fun,patternBank)
        return self.__patternbank

class sampler:

    def __init__(self, patchside, thrss):
        self.__patchside = patchside
        self.__thrss = thrss
        self.__bitDepth = int(math.log(len(self.__thrss)+1,2))

    def sample3Din2Dslices(self, image, direction=0, verbose=False):
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
        if not int(math.log(len(self.__thrss)+1,2)) == self.__bitDepth :
            raise ValueError("incompatible thresholds and bitDepth")
        x, y = image.shape
        imageCopy = np.reshape(nii_maths.thressholding(image.ravel(), self.__thrss),(x,y))
        i=j=0
        freqHistogram = {}
        if verbose:
            print('start')
        for i in range(0, x - self.__patchside + 1):
            for j in range(0, y - self.__patchside + 1):
                key = nii_maths.patternKey(self.__bitDepth,
                    imageCopy[i:i + self.__patchside, j:j + self.__patchside] )
                if key in freqHistogram:
                    freqHistogram[key] += 1
                else:
                    freqHistogram.update({key: 1})
            if verbose:
                print ("\rprogress: ", int((i/float(x - self.__patchside))*100), "%" , end="")

        ret = { k : float(v) for k,v in freqHistogram.items() }
        if verbose:
            print ('\nended')
        return ret

    def sample3D(self, image, verbose=False):
        """
            Sample 3D array of data
        """
        if not len(image.shape) == 3:
            raise ValueError("must provide 3D images")
        if not int(math.log(len(self.__thrss)+1,2)) == self.__bitDepth :
            raise ValueError("incompatible thresholds and bitDepth")
        x, y, z = image.shape
        imageCopy = np.reshape(nii_maths.thressholding(image.ravel(), self.__thrss),(x,y,z))
        i=j=k=0
        freqHistogram = {}
        if verbose:
            print('start')
        for i in range(0, x - self.__patchside + 1):
            for j in range(0, y - self.__patchside + 1):
                for k in range(0, z - self.__patchside + 1):
                    key = nii_maths.patternKey(self.__bitDepth,
                        imageCopy[i:i + self.__patchside, j:j + self.__patchside, k:k + self.__patchside] )
                    if key in freqHistogram:
                        freqHistogram[key] += 1
                    else:
                        freqHistogram.update({key: 1})
            if verbose:
                print ("\rprogress: ", int((i/float(x - self.__patchside))*100), "%" , end="")

        ret = { k : float(v) for k,v in freqHistogram.items() }
        if verbose:
            print ('\nended')
        return ret
