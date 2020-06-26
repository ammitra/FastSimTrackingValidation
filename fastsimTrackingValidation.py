import CRABClient
from CRABAPI.RawCommand import crabCommand
from CRABClient.UserUtilities import config

import cmsDriverAPI, pickle, os, time, subprocess
import fastsimTrackingHelpers as helper

from collections import OrderedDict

from optparse import OptionParser

parser = OptionParser()

parser.add_option('-d', metavar='F', type='string', action='store',
                default =   '',
                dest    =   'dir',
                help    =   'Directory to validate')
parser.add_option('--cmssw', metavar='F', type='string', action='store',
                default =   'CMSSW_10_6_11',
                dest    =   'cmssw',
                help    =   'CMSSW release to use')
parser.add_option("--ALL", action="store_true", 
                default =   False,
                dest    =   "all",
                help    =   "Run full workflow")
parser.add_option("--steps", type='string', action="store", 
                default =   '',
                dest    =   "steps",
                help    =   "Comma separated list of steps. Possible are AOD,TRACKVAL,MINIAOD,BTAGVAL,NANOAOD,HAMMER.")


(options, args) = parser.parse_args()

eos_path = 'root://cmseos.fnal.gov//store/user/lcorcodi/'

#----------------------Maker Classes----------------------------------#
# Parent class of processing objects
class Maker(object):
    """docstring for Maker"""
    def __init__(self, stepname, prev): # name is either AOD, MINIAOD, NANOAOD, TRACKVAL, BTAGVAL, HAMMER
        super(Maker, self).__init__()

        # Store reference to maker this is reliant on ("True" for AOD which is the top level)
        self.stepname = stepname
        self.prev = prev
        if self.prev == None:
            raise TypeError('The previous object needs to be made before running this step. If the current step already exists, please load it.')

        # Basic initializing
        if self.stepname in ['AOD','MINIAOD','NANOAOD']:
            self.crab = True
        else:
            self.crab = False

        # THINGS GET HAIRY HERE SO THIS IS WHERE TO PICK BACK UP
        self.localsavedir = '%s/'%stepname
        self.savename = '%s%s.p'%(self.localsavedir,stepname) # pickle name
        self.exists = self.checkExists() # check if pickle already exists
        if self.crab:
            self.crab_config = helper.MakeCrabConfig(stepname, tag) # make crab config
            self.crabDir = stepname+'/crab_'+self.crab_config.General.requestName # record crab task dir name
            self.cmsRun_file = 'fastsim_%s.py'%stepname
            self.submit_out = None
        else:
            self.cmsRun_file = ''

    # Save out obj to pickle
    def save(self):
        pickle.dump(self, open(self.savename, "wb"))
        if self.crab:
            helper.SaveToJson('%scrab_submit.json'%self.localsavedir, self.submit_out)
            helper.SaveToJson('%scrab_status.json'%self.localsavedir, crabCommand('status',dir = self.crabDir))

    # Check if pickled obj already exists
    def checkExists(self):
        if self.savename == '':
            raise ValueError('Savename is empty. Cannot check for existence.')

        exists = os.exists(self.savename)
        if exists:
            print('WARNING: %s has already been made.'%self.savename)

        return exists
    # Check if self crab job finished
    def checkDone(self):
        status = crabCommand('status',dir = self.crabDir)
        if status['status'] == 'COMPLETED':
            print ('Job %s COMPLETED'%self.crabDir)
            done = True
        else:
            done = False
        
        return done
    # Wait for crab job that self relies on to finish
    def wait(self):
        if self.prev != True:
            while not self.prev.checkDone():
                time.sleep(60)

    def run_gen(self):
        self.wait()
        helper.MakeRunConfig(self.cmsDriver_args)
        self.submit_out = crabCommand('submit',config=self.cmsRun_file)

    def setDir(self,valdir): # id for what is being validated
        self.valdir = valdir

    def setCmsRunFile(self,file):
        self.cmsRun_file = file

# Fastsim AOD production
class MakeAOD(Maker):
    """docstring for MakeAOD"""
    def __init__(self):
        super(MakeAOD, self).__init__('AOD',True)
        
        self.cmsDriver_args = [
            'TTbar_13TeV_TuneCUETP8M1_cfi',
            '--conditions auto:phase1_2018_design', 
            '--fast', '-n 10000', '--nThreads 1',
            '--era Run2_2018_FastSim', '--beamspot Realistic50ns13TeVCollision',
            '--datatier AODSIM,DQMIO', '--eventcontent AODSIM,DQM',
            '-s GEN,SIM,RECOBEFMIX,DIGI:pdigi_valid,RECO,VALIDATION:tracksValidationTrackingOnly',
            '--python_filename '+self.cmsRun_file, '--fileout fastsim_AOD.root'
        ]

    def run():
        self.run_gen()

#### Track validation 
class MakeTrackVal(Maker):
    """docstring for MakeTrackVal"""
    def __init__(self, AODobj):
        super(MakeTrackVal, self).__init__('TRACKVAL',AODobj)
        
    def run():
        self.wait()
        harvest_cmd = 'harvestTrackValidationPlots.py %s -o harvestTracks.root'%(eos_path+self.prev.crab_config.Data.outputDatasetTag)
        harvest = subprocess.Popen(harvest_cmd.split(' '))
        # harvest.wait()
        # subprocess.Popen('makeTrackValidationPlots.py %s -o tracking_plots'%(eos_path+self.prev.crabDir))

## MiniAOD production
class MakeMiniAOD(Maker):
    """docstring for MakeMiniAOD"""
    def __init__(self, AODobj):
        super(MakeMiniAOD, self).__init__('MINIAOD',AODobj)

        self.cmsDriver_args = [
            '--filein file:fastsim_AOD.root',
            '--conditions auto:phase1_2018_design',
            '--fast', '-n 10000', '--nThreads 1',
            '--era Run2_2018_FastSim', '--beamspot Realistic50ns13TeVCollision',
            '--datatier MINIAODSIM', '--eventcontent MINIAODSIM',
            '-s PAT', '--python_filename '+self.cmsRun_file,
            '--fileout fastsim_MINIAOD.root', '--runUnscheduled']

    def run():
        self.run_gen()
        

#### Btag validation
class MakeBtagVal(Maker):
    """docstring for MakeBtagVal"""
    def __init__(self, MiniAODobj):
        super(MakeBtagVal, self).__init__('BTAGVAL',MiniAODobj)

    def run():
        self.wait()
        pass

## NanoAOD production
class MakeNanoAOD(Maker):
    """docstring for MakeNanoAOD"""
    def __init__(self, MiniAODobj):
        super(MakeNanoAOD, self).__init__('NANOAOD',MiniAODobj)

        self.cmsDriver_args = [
            '--filein file:fastsim_MINIAOD.root',
            '--conditions auto:phase1_2018_design',
            '--fast', '-n 10000', '--nThreads 1',
            '--era Run2_2018,run2_nanoAOD_102Xv1', '--beamspot Realistic50ns13TeVCollision',
            '--datatier NANOAODSIM', '--eventcontent NANOAODSIM',
            '-s NANO', '--mc', '--python_filename '+self.cmsRun_file,
            '--fileout fastsim_NANOAOD.root', '''--customise_commands="process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))"'''
        ]

    def run():
        self.run_gen()


#### HAMMER
class MakeHAMMER(Maker):
    """docstring for MakeHAMMER"""
    def __init__(self, NanoAODobj):
        super(MakeHAMMER, self).__init__('HAMMER',NanoAODobj)
        self.savename = 'HAMMER/HAMMER.p'
        self.checkExists()
        self.crab_config = helper.MakeCrabConfig('HAMMER')
        self.crabDir = 'HAMMER/crab_'+self.crab_config.General.requestName

    def run(self):
        self.wait()
        pass


#------------------------------------------------------------#

if __name__ == '__main__':
    step_bools = helper.ParseSteps(options.all,options.steps)
    working_dir = helper.GetWorkingArea(options.cmssw,options.dir)

    with helper.cd(working_dir):
        subprocess.call(["eval `scramv1 runtime -sh`"],shell=True)
        makers = helper.GetMakers(step_bools)

        for m in makers:
            m.setDir(options.dir)
            m.run()
            m.save()

    
