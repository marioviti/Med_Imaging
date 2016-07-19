import os
import simplejson as json

#Dir Ops
def getExtension(filepathname):
    filename, fileExtension = os.path.splitext(filepathname)
    return fileExtension

def joinpath(dirname, filename):
    return os.path.join(dirname, filename)

def getdirlist(dirname, exts):
    if dirname=="" or exts == []:
        return []
    if not os.path.isdir(dirname):
        return []
    pre_listofdir = os.listdir(dirname)
    listofdir = [ filname for filname in os.listdir(dirname) if ''+getExtension(filname) in exts ]
    mtime = lambda f: - os.stat(os.path.join(dirname, f)).st_mtime
    return list(sorted(listofdir, key=mtime))

#Dictionaries
def saveDict(dirname, filename, data):
    name = joinpath(dirname,filename)
    with open(name, 'w') as fp:
        json.dump(data, fp)

def loadDict(dirname, filename):
    name = joinpath(dirname,filename)
    try:
        fp = open(name, 'r')
        data = json.load(fp)
    except (IOError, json.JSONDecodeError), e:
        data = None
    return data

#Pickles
def savePick(dirname, filename, data):
    name = joinpath(dirname,filename)
    with open(name, 'wb') as fp:
        pic.dump(data,fp)

def loadPick(dirname, filename):
    name = joinpath(dirname,filename)
    try:
        fp = open(filename, 'rb')
        data = pic.load(fp)
    except IOError, e:
        if e.errno == 2:
            data = None
        else:
            raise IOError(e.errno)
    return data
