from CRABAPI.RawCommand import crabCommand

import cmsDriverAPI, pickle, os, time
import fastsimTrackingHelpers as helper

from collections import OrderedDict

#----------------------Maker Classes----------------------------------#
class Maker(object):
    """Parent class of processing objects"""
    def __init__(self, stepname, prev,options): # name is either AOD, MINIAOD, NANOAOD, TRACKVAL, BTAGVAL, ANALYSIS
        super(Maker, self).__init__()

        # Store reference to maker this is reliant on ("False" for AOD which is the top level)
        self.stepname = stepname
        self.prev = prev
        if self.prev == None:
            raise TypeError('The previous object needs to be made before running this step. If the current step already exists, please make sure it is loading properly.')

        # Basic initializing
        if self.stepname in ['AOD','BTAGVAL','MINIAOD','NANOAOD']:
            self.crab = True
        else:
            self.crab = False
        self.localsavedir = '%s/'%self.stepname
        self.picklename = '%s%s.p'%(self.localsavedir, stepname)
        self.exists = self.checkExists() # check if pickle already exists

        # Crab configuration if needed
        if self.crab:
            # Get input files
            if self.prev != False:
                if self.prev.crab:
                    input_file = '%sFastSim_%s*.root'%(self.prev.eosDir,self.prev.stepname if self.stepname != 'BTAGVAL' else 'AOD_inDQM')
        else:
                    input_file = '%sFastSim_%s.root'%(self.prev.localsavedir,self.prev.stepname if self.stepname != 'BTAGVAL' else 'AOD_inDQM')
            else:
                input_file = ''
            # Get crab setup to track
            self.crab_config = helper.MakeCrabConfig(stepname, options.tag, files=[input_file], storageSite=options.storageSite) # make crab config
            self.crabDir = self.localsavedir+'crab_'+self.crab_config.General.requestName # record crab task dir name
            self.cmsRun_file = self.crab_config.JobType.psetName

            # Set after submit
            self.submit_out = None
            self.eosPath = None

    # Save out obj to pickle
    def save(self):
        pickle.dump(self, open(self.picklename, "wb"))
        if self.crab:
            helper.SaveToJson('%scrab_submit.json'%self.localsavedir, self.submit_out)
            # helper.SaveToJson('%scrab_status.json'%self.localsavedir, crabCommand('status',dir = self.crabDir))

    # Check if pickled obj already exists
    def checkExists(self):
        if self.picklename == '':
            raise ValueError('Pickle name is empty. Cannot check for existence.')
        exists = os.path.exists(self.picklename)
        if exists:
            print('WARNING: %s has already been made. Will overwrite.'%self.picklename)
        
        return exists

    # Check if self crab job finished
    def checkDone(self):
        status = crabCommand('status',dir = self.crabDir)
        if status['status'] == 'COMPLETED':
            print ('Job %s COMPLETED'%self.crabDir)
            done = True
        elif status['status'] == 'FAILED':
            raise Exception('Job %s has FAILED. Please attempt to fix the issue manually before attempting to rerun.'%self.crabDir)
        else:
            done = False
        return done

    # Wait for crab job that self relies on to finish
    def wait(self):
        if self.prev != False:
            while not self.prev.checkDone():
                time.sleep(60)

    def run_gen(self):
        self.wait()
        helper.MakeRunConfig(self.cmsDriver_args)
        if not os.path.exists(self.cmsRun_file):
            raise Exception('%s was not created.'%self.cmsRun_file)
        self.submit_out = crabCommand('submit',config=self.crab_config)
        self.setEOSdir()

    def setEOSdir(self):
        full_request = self.submit_out['uniquerequestname']
        first_underscore = full_request.find('_')+1
        request_time_data = full_request[:full_request.find('_',first_underscore)]
        self.eosPath = 'root://cmsxrootd.fnal.gov//%s/%s/%s/%s/*/%s.root'%(self.crab_config.Data.outLFNDirBase, self.crab_config.General.requestName, self.crab_config.Data.outputDatasetTag, request_time_data, self.crab_config.JobType.psetName)
        return self.eosPath

# Fastsim AOD production
class MakeAOD(Maker):
    """docstring for MakeAOD"""
    def __init__(self,options):
        super(MakeAOD, self).__init__('AOD',True,options)
        
        self.cmsDriver_args = [
            'TTbar_13TeV_TuneCUETP8M1_cfi',
            '--conditions auto:phase1_2018_design', 
            '--fast', '-n 10000', '--nThreads 1',
            '--era Run2_2018_FastSim', '--beamspot Realistic50ns13TeVCollision',
            '--datatier AODSIM,DQMIO', '--eventcontent AODSIM,DQM',
            '-s GEN,SIM,RECOBEFMIX,DIGI:pdigi_valid,RECO,VALIDATION:tracksValidationTrackingOnly',
            '--python_filename '+self.cmsRun_file, '--fileout fastsim_AOD.root'
        ]

    def run(self):
        self.run_gen()

#### Btag validation
class MakeBtagVal(Maker):
    """docstring for MakeBtagVal"""
    def __init__(self, MiniAODobj,options):
        super(MakeBtagVal, self).__init__('BTAGVAL',MiniAODobj)

    def run(self):
        self.wait()
        pass

#### Track validation 
class MakeTrackVal(Maker):
    """docstring for MakeTrackVal"""
    def __init__(self, AODobj,options):
        super(MakeTrackVal, self).__init__('TRACKVAL',AODobj,options)
        
    def run(self):
        self.wait()
        harvest_cmd = 'harvestTrackValidationPlots.py %s -o harvestTracks.root'%(options.eosPath+self.prev.crab_config.Data.outputDatasetTag)
        harvest = subprocess.Popen(harvest_cmd.split(' '))
        # harvest.wait()
        # subprocess.Popen('makeTrackValidationPlots.py %s -o tracking_plots'%(options.eosPath+self.prev.crabDir))

## MiniAOD production
class MakeMiniAOD(Maker):
    """docstring for MakeMiniAOD"""
    def __init__(self, AODobj,options):
        super(MakeMiniAOD, self).__init__('MINIAOD',AODobj,options)

        self.cmsDriver_args = [
            '--filein file:fastsim_AOD.root',
            '--conditions auto:phase1_2018_design',
            '--fast', '-n 10000', '--nThreads 1',
            '--era Run2_2018_FastSim', '--beamspot Realistic50ns13TeVCollision',
            '--datatier MINIAODSIM', '--eventcontent MINIAODSIM',
            '-s PAT', '--python_filename '+self.cmsRun_file,
            '--fileout fastsim_MINIAOD.root', '--runUnscheduled']

    def run(self):
        self.run_gen()

## NanoAOD production
class MakeNanoAOD(Maker):
    """docstring for MakeNanoAOD"""
    def __init__(self, MiniAODobj,options):
        super(MakeNanoAOD, self).__init__('NANOAOD',MiniAODobj,options)

        self.cmsDriver_args = [
            '--filein file:fastsim_MINIAOD.root',
            '--conditions auto:phase1_2018_design',
            '--fast', '-n 10000', '--nThreads 1',
            '--era Run2_2018,run2_nanoAOD_102Xv1', '--beamspot Realistic50ns13TeVCollision',
            '--datatier NANOAODSIM', '--eventcontent NANOAODSIM',
            '-s NANO', '--mc', '--python_filename '+self.cmsRun_file,
            '--fileout fastsim_NANOAOD.root', '''--customise_commands="process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))"'''
        ]

    def run(self):
        self.run_gen()


#### ANALYSIS
class MakeAnalysis(Maker):
    """docstring for MakeAnalysis"""
    def __init__(self, NanoAODobj,options):
        super(MakeAnalysis, self).__init__('ANALYSIS',NanoAODobj,options)
        self.savename = 'ANALYSIS/ANALYSIS.p'
        self.checkExists()
        self.crab_config = helper.MakeCrabConfig('ANALYSIS')
        self.crabDir = 'ANALYSIS/crab_'+self.crab_config.General.requestName

    def run(self):
        self.wait()
        pass



    
