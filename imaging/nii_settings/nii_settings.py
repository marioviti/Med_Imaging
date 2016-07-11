import os
if  os.environ['PWD'] not in os.environ['PATH']:
    os.environ['OLD_PATH'] = os.environ['PATH']
    os.environ['PATH'] += ":" + os.environ['PWD']
import nii_utils as utils

def createSettings(path, extensions):
    settingsData = {
        'todo_dirlist' : utils.getdirlist(path,extensions),
        'done_dirlist' : []
        }
    return settingsData

def loadSettings(path):
    return utils.loadDict(path, settingsfilename)

def savesamples(dirname, filename, samples):
    data = utils.loadPick(nii_dir,nii_data_name) # load data
    if data == None:
        data = []
    data += [samples]
    utils.savePick(dirname, filename, data)
