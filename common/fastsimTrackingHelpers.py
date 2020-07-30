import CRABClient, subprocess
from CRABClient.UserUtilities import config
import cmsDriverAPI, pickle, os, json

from contextlib import contextmanager
from collections import OrderedDict
from fastsimTrackingValidation import *

#--------------------Helpers-----------------------------------------#
def ParseSteps(allBool,steps):
    step_list = steps.split(',')
    all_steps = ['AOD','TRACKVAL','BTAGVAL','MINIAOD','NANOAOD','ANALYSIS']
    out = OrderedDict()

    if allBool:
        for s in all_steps:
            out[s] = True

    else:
        for step in all_steps:
            if step in step_list:
                out[step] = True
            else:
                out[step] = False
    print ('Will process %s'%[s for s in out.keys() if out[s] == True])
    return out

def GetWorkingArea(cmssw,testdir):
    working_location = testdir+'/'+cmssw+'/src'

    if os.path.isdir(working_location):
        working_location+='/FastSimValWorkspace'
        if not os.path.isdir(working_location):
            print('mkdir '+working_location)
            os.mkdir(working_location)
        for f in ['AOD','TRACKVAL','BTAGVAL','MINIAOD','NANOAOD','ANALYSIS']:
            if not os.path.isdir(working_location+'/'+f):
                print ('mkdir '+working_location+'/'+f)
                os.mkdir(working_location+'/'+f)
    else:
        raise NameError('%s does not exist'%working_location)
    
    return working_location

def GetMakers(step_bools,options):
    makers = OrderedDict()
    
    for step_name in step_bools.keys():
        if step_bools[step_name]:
            if step_name == 'AOD': # AOD - no reliance
                makers[step_name] = MakeAOD(options)
            elif step_name == 'TRACKVAL': # TRACKVAL - relies on AOD/DQM
                makers[step_name] = MakeTrackVal(makers['AOD'],options)
            elif step_name == 'BTAGVAL': # BTAGVAL - relies on AOD/DQM
                makers[step_name] = MakeBtagVal(makers['AOD'],options)
            elif step_name == 'MINIAOD': # MINIAOD - relies on AOD
                makers[step_name] = MakeMiniAOD(makers['AOD'],options)
            elif step_name == 'NANOAOD': # NANOAOD - relies on MINIAOD
                makers[step_name] = MakeNanoAOD(makers['MINIAOD'],options)
            elif step_name == 'ANALYSIS': # ANALYSIS - relies on NANOAOD
                makers[step_name] = MakeAnalysis(makers['NANOAOD'],options)
        else:
            # Returns None and warning message if it doesn't exist
            makers[step_name] = LoadMaker('{0}/{0}.p'.format(step_name))
 
    return makers

def LoadMaker(name):
    if os.path.exists(name):
        return pickle.load(open(name, "rb"))
    else:
        print ('WARNING: Cannot find %s. Further steps may not run.'%name)
        return None

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
        subprocess.call([cmd],shell=True,executable='/bin/bash')


#------------CMS interfacing-----------------------------------------#
def MakeCrabConfig(stepname, tag, files=[],storageSite='T3_US_FNALLPC',outLFNdir='/store/user/%s/FastSimValidation/'%os.environ['USER'],nevents=None,dataset=''):
    # As of now, only first statement will run (but keeping functionality)
    if stepname in ['AOD']:#,'BTAGVAL','MINIAOD','NANOAOD']:
        gen = True
        ana = False
    else:
        gen = False
        ana = True

    if files[0] == '' and gen and stepname != 'AOD':
        raise ValueError("You are trying to generate but the inputFiles list is non-empty. Perhaps you meant to run an analysis script?")
    if files == [] and ana:
        raise ValueError("You are trying to analyze but the inputFiles list is empty.")

    crab_config = config()
    crab_config.General.requestName = 'FastSimValidation_%s'%stepname
    crab_config.General.workArea = stepname
    crab_config.General.transferOutputs = True
    crab_config.JobType.psetName = '%s/FastSimValidation_%s.py'%(stepname,stepname)
    crab_config.Data.publication = False
    if stepname == 'AOD':
        crab_config.Data.totalUnits = int(nevents)
        # crab_config.Data.inputDataset = dataset
    crab_config.Site.storageSite = storageSite
    crab_config.Data.outLFNDirBase = outLFNdir
    crab_config.Data.outputPrimaryDataset = dataset.replace('_cfi','')
    crab_config.Data.outputDatasetTag = tag
    if files != ['']:
        crab_config.Data.inputFiles = files

    # Again, first statement will always be the one to execute
    if gen:
        crab_config.JobType.pluginName = 'PrivateMC'
        crab_config.Data.splitting = 'EventBased'
        crab_config.Data.unitsPerJob = 1000
    elif ana:
        crab_config.JobType.pluginName = 'Analysis'
        crab_config.Data.splitting = 'FileBased'
        crab_config.Data.unitsPerJob = 1

    return crab_config

def MakeRunConfig(inputArgs):
    final_string = ''
    for a in inputArgs:
        final_string += a+' '
    final_string += '--no_exec'
    print final_string.split()
    cmsDriverAPI.run(final_string.split())
    # remove_spaces = []
    # for a in inputArgs:
    #     s = a.split(' ')
    #     for p in s:
    #         if p != '': remove_spaces.append(p)
    # driver_args = remove_spaces
    # driver_args.append('--no_exec')
    # print (driver_args)
    # cmsDriverAPI.run(driver_args)