import nii_io as nio
import nii_utils as utils
import nii_settings as nst
import nii_MDV as mdv
import numpy as np

import datetime as dtme
################################################################################
proj_dir = "."
nii_dir = "./brainNii"
nii_settings_name = "settings.json"
nii_data_name = "patterns.json"

extensions = ['.nii']
patch_side = 3 # sample side either 2D or 3D
################################################################################

def main():
    print "proj_dir: " + proj_dir +'\n'+ "nii_dir: " + nii_dir +'\n'+ "nii_settings_name: " + nii_settings_name +'\n'
    settings = utils.loadDict(proj_dir,nii_settings_name)
    if settings == None:
        settings = nst.createSettings(nii_dir,extensions)
    utils.saveDict(proj_dir,nii_settings_name,settings)

    data = utils.loadDict(proj_dir,nii_data_name) # load data
    data = {} if data == None else data
    imgs_data = np.array(nio.loadNii(utils.joinpath(nii_dir,settings['todo_dirlist'][0])))
    mean = np.mean(imgs_data)
    std = np.std(imgs_data)
    thrss = np.array([ mean-std, mean+std, np.amax(imgs_data) ])
    settings['thrss'] = []
    for t in thrss:
        settings['thrss'] += [`t`]
    sampler = mdv.sampler(patch_side, thrss)
    utils.saveDict(proj_dir,nii_data_name,data)
    utils.saveDict(proj_dir,nii_settings_name,settings)
    print settings
    for img_name in settings['todo_dirlist']:
        t_0 = dtme.datetime.now()
        img_data = nio.loadNii(utils.joinpath(nii_dir,img_name))
        res = sampler.sample3D(img_data,True)
        data = mdv.nii_maths.mergedicts(data,res)
        utils.saveDict(proj_dir,nii_data_name,data)
        settings['todo_dirlist'].remove(img_name)
        settings['done_dirlist'] += [img_name]
        utils.saveDict(proj_dir,nii_settings_name,settings)
        t_1 = dtme.datetime.now()
        print t_1 - t_0

if __name__ == '__main__':
    main()
