import nii_MDV as mdv
import nii_io
import nii_utils as utils
import numpy as np
proj_dir = "."
nii_dir = "./brainNii"
nii_settings_name = "settings.json"
nii_data_name = "patterns.json"
nii_histogram_name = "histogram.json"

extensions = ['.nii']
patch_side = 3 # considering square pathces

def main():
    data = utils.loadDict(proj_dir,nii_data_name) # load data
    bnnh = mdv.nii_maths.binnedHistogram(precision = 0.001, fun=np.log,mapkv=data)
    utils.saveDict(proj_dir,nii_histogram_name,bnnh.MAP)

if __name__ == '__main__':
    main()
