import cmsDriverAPI, pickle, os, json

from contextlib import contextmanager
from collections import OrderedDict

#------------CMS interfacing-----------------------------------------#
def MakeCrabConfig(stepname, tag, files=[]):
    if stepname in ['AOD','MINIAOD','NANOAOD']:
        gen = True
        ana = False
    else:
        gen = False
        ana = True

    if files != [] and gen:
        raise ValueError("You are trying to generate but the inputFiles list is non-empty. Perhaps you meant to run an analysis script?")
    if files == [] and ana:
        raise ValueError("You are trying to analyze but the inputFiles list is empty.")

    config = config()
    config.General.requestName = 'FastSimValidation_%s'%stepname
    config.General.workArea = stepname
    config.General.transferOutputs = True
    config.JobType.psetName = 'FastSimValidation_%s.py'%stepname
    config.Data.publication = False
    config.Site.storageSite = 'T3_US_FNALLPC'
    config.Data.outLFNDirBase = '/store/user/lcorcodi/FastSimValidation/'
    config.Data.outputDatasetTag = tag

    if gen:
        config.JobType.pluginName = 'PrivateMC'
        config.Data.splitting = 'EventBased'
        config.Data.unitsPerJob = 1000
    elif ana:
        config.JobType.pluginName = 'Analysis'
        config.Data.inputFiles = files
        config.Data.splitting = 'FileBased'
        config.Data.unitsPerJob = 1

    return config

def MakeRunConfig(inputArgs):
    remove_spaces = []
    for a in inputArgs:
        s = a.split(' ')
        for p in s:
            if p != '': remove_spaces.append(p)

    driver_args = ['--noexec'].extend(remove_spaces)
    cmsDriverAPI.run(driver_args)

#--------------------Helpers-----------------------------------------#
def ParseSteps(allBool,steps):
    step_list = steps.split(',')
    all_steps = ['AOD','TRACKVAL','MINIAOD','BTAGVAL','NANOAOD','HAMMER']
    out = {}

    if allBool:
        for s in all_steps:
            out[s] = True

    else:
        for step in all_steps:
            if step in step_list:
                out[step] = True
            else:
                out[step] = False

    return out

def GetWorkingArea(cmssw,testdir):
    working_location = testdir+'/'+cmssw+'/src'

    if os.path.isdir(working_location):
        working_location+='/FastSimValidation'
        if not os.path.isdir(working_location):
            print('mkdir '+working_location)
            os.mkdir(working_location)
    else:
        raise NameError('%s does not exist'%working_location)
    
    return working_location

def LoadMaker(name):
    if os.exists(name):
        return pickle.load(open(name, "rb"))
    else:
        raise ValueError('Attempt to load `%s` which does not exist.'%name)

def SaveToJson(path,outdict):
    out = open(path,'w')
    out.write(json.dumps(outdict))
    out.close()

@contextmanager
def cd(newdir):
    print ('cd '+newdir)
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
