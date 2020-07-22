import CRABClient
from CRABClient.UserUtilities import config
import cmsDriverAPI, pickle, os, json

from contextlib import contextmanager
from collections import OrderedDict
from fastsimTrackingValidation import *

#--------------------Helpers-----------------------------------------#
def ParseSteps(allBool,steps):
    step_list = steps.split(',')
    all_steps = ['AOD','TRACKVAL','BTAGVAL','MINIAOD','NANOAOD','ANALYSIS']
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
    print ('Will process %s'%out)
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

def GetMakers(step_bools,options):
    makers = OrderedDict()
    # AOD - no reliance
    if step_bools['AOD']:
        makers['AOD'] = MakeAOD(options)
    else:
        makers['AOD'] = LoadMaker('AOD/AOD.p')
    # TRACKVAL - relies on AOD/DQM
    if step_bools['TRACKVAL']:
        makers['TRACKVAL'] = MakeTrackVal(makers['AOD'],options)
    else:
        makers['TRACKVAL'] = LoadMaker('TRACKVAL/TRACKVAL.p')
    # BTAGVAL - relies on AOD/DQM
    if step_bools['BTAGVAL']:
        makers['BTAGVAL'] = MakeBtagVal(makers['AOD'],options)
    else:
        makers['BTAGVAL'] = LoadMaker('BTAGVAL/BTAGVAL.p')
    # MINIAOD - relies on AOD
    if step_bools['MINIAOD']:
        makers['MINIAOD'] = MakeMiniAOD(makers['AOD'],options)
    else:
        makers['MINIAOD'] = LoadMaker('MINIAOD/MINIAOD.p')
    # NANOAOD - relies on MINIAOD
    if step_bools['NANOAOD']:
        makers['NANOAOD'] = MakeNanoAOD(makers['MINIAOD'],options)
    else:
        makers['NANOAOD'] = LoadMaker('NANOAOD/NANOAOD.p')
    # ANALYSIS - relies on NANOAOD
    if step_bools['ANALYSIS']:
        makers['ANALYSIS'] = MakeAnalysis(makers['NANOAOD'],options)
    else:
        makers['ANALYSIS'] = LoadMaker('ANALYSIS/ANALYSIS.p')
 
    return makers

def LoadMaker(name):
    if os.path.exists(name):
        return pickle.load(open(name, "rb"))
    else:
        print ('Attempt to load `%s` which does not exist.'%name)
        return False

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

def executeCmd(cmd,bkg=False):
    if bkg:
        subprocess.Popen(cmd.split(' '))
    else:
        subprocess.call([cmd],shell=True)


#------------CMS interfacing-----------------------------------------#
def MakeCrabConfig(stepname, tag, files=[],storageSite='T3_US_FNALLPC'):
    # if stepname in ['AOD','BTAGVAL','MINIAOD','NANOAOD']:
    gen = True
    ana = False
    # else:
    #     gen = False
    #     ana = True

    if files != [] and gen:
        raise ValueError("You are trying to generate but the inputFiles list is non-empty. Perhaps you meant to run an analysis script?")
    if files == [] and ana:
        raise ValueError("You are trying to analyze but the inputFiles list is empty.")

    crab_config = config()
    crab_config.General.requestName = 'FastSimValidation_%s'%stepname
    crab_config.General.workArea = stepname
    crab_config.General.transferOutputs = True
    crab_config.JobType.psetName = 'FastSimValidation_%s.py'%stepname
    crab_config.Data.publication = False
    crab_config.Site.storageSite = storageSite
    crab_config.Data.outLFNDirBase = '/store/user/lcorcodi/FastSimValidation/'
    crab_config.Data.outputDatasetTag = tag

    # if gen:
    crab_config.JobType.pluginName = 'PrivateMC'
    crab_config.Data.splitting = 'EventBased'
    crab_config.Data.unitsPerJob = 1000
    # elif ana:
    #     crab_config.JobType.pluginName = 'Analysis'
    #     crab_config.Data.inputFiles = files
    #     crab_config.Data.splitting = 'FileBased'
    #     crab_config.Data.unitsPerJob = 1

    return crab_config

def MakeRunConfig(inputArgs):
    remove_spaces = []
    for a in inputArgs:
        s = a.split(' ')
        for p in s:
            if p != '': remove_spaces.append(p)
    driver_args = ['--no_exec']
    driver_args.extend(remove_spaces)
    print (driver_args)
    cmsDriverAPI.run(driver_args)