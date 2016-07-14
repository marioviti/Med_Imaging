import nii_MDV as mdv
import nii_io
import nii_utils as utils
import numpy as np
import sys
from settings import *

def main():
    if len(sys.argv)<2:
        print 'no precision provided, setting to default 0.001'
        precision_ = 0.001
    else:
        precision_ = float(sys.argv[1])
    data = utils.loadDict(proj_dir,nii_data_name) # load data
    bnnh = mdv.nii_maths.binnedHistogram(precision=precision_,
     fun=np.log,mapkv=data)
    utils.saveDict(proj_dir,nii_histogram_name,bnnh.MAP)

if __name__ == '__main__':
    main()
