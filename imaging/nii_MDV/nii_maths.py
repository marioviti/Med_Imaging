import math
import bisect as bsc

def mergedicts(a,b):
    c = {}
    if a == {}:
        return b
    if b == {}:
        return a
    keys = set().union(*[a.keys(), b.keys()])
    for key in keys:
        try:
            c[key] = a[key]
        except KeyError, e:
            c[key] = 0
        try:
            c[key] += b[key]
        except KeyError, e:
            c[key] = c[key]
    return c

class precisionError:
    def __init__(self,val):
        self.val = val

    def __str__(self):
        return repr(self.val)

def makeFreqHistogram(samples, precision=1, fun=lambda x:x):
    overall = sum(samples.values())
    if overall == 0:
        raise ZeroDivisionError("there must be non empty sample")
    freqHistogram = {}
    for patt,count in samples.items():
        smoothed = smooth(fun(count/float(overall)),precision)
        if smoothed in freqHistogram:
            freqHistogram[smoothed] += [patt]
        else:
            freqHistogram[smoothed] = [patt]
    return freqHistogram

def smooth(n, precision):
    if precision > 1:
        raise precisionError("precision must be percentage.")
    return math.trunc(n/precision)*precision if precision < 1 else n

class binnedHistogram:
    """
    produce a binned histogram, mapkv is a keyvalue map structured as
    { observation : occurrences , ... , }. Parameter float array X is the sorted
    list of frequencies, float array Y is the count of patterns with respect to X
    dictionary MAP is the mapping from X to a list of samples.
    """
    def __init__(self, precision=1, fun=lambda x:x, mapkv={}):
        self.__precision = precision
        self.__fun = fun
        self.makebin(mapkv, self.__precision, self.__fun)

    @property
    def fun(self):
        return self.__fun

    @property
    def precision(self):
        return self.__precision

    @property
    def X(self):
        """
        frequencies binned based on precision
        """
        return self.__X

    @property
    def Y(self):
        """
        counts per bin
        """
        return self.__Y

    @property
    def MAP(self):
         """
         mapping between frequencies and elements lists
         """
         return self.__map

    def makebin(self, sample, precision, fun):
        self.__map = makeFreqHistogram(sample, precision, fun)
        mapp = sorted(self.__map.items(), key=lambda x:x[0])
        self.__X = [i for (i,j) in mapp]
        self.__Y = [len(j) for (i,j) in mapp]

def makefilter(thrss):
    def myfilter(x):
        return bsc.bisect_left(thrss,x)
    return myfilter

def thressholding(arr, thrss):
    assert arr.flags["C_CONTIGUOUS"], "must be c contiguous array."
    thrss.sort()
    myfilter = makefilter(thrss)
    return map(myfilter,arr)

def patternKey(bitDepth, pattern):
    """
        Given a pattern returns a key in the specified bitDepth
    """
    flatdim = reduce(lambda x,y: x*y, pattern.shape)
    flatpatt = pattern.flatten()
    acc = 0
    for i in range(0,flatdim):
        acc += (1 << ((i) * bitDepth)) * int(flatpatt[i])
    return acc

def keyPattern(pattshape, bitDepth, key):
    """
        Given a key number returns a pattern in the specified pattshape, bitDepth
    """
    flatdim = reduce(lambda x,y: x*y, pattshape)
    pattern = np.array( range(0, flatdim) ) * 0
    if key == int((2**bitDepth)**flatdim) - 1:
        pattern.shape = pattshape
        return pattern + (int(2**bitDepth) - 1)
    if key == 0:
        pattern.shape = pattshape
        return  pattern * 0
    for i in range(0, len(pattern)):
        pattern[i] = key % int(2**bitDepth)
        key >>= bitDepth
    pattern.shape = pattshape
    return pattern
