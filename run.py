#!/usr/bin/env python3
import time, os
from optparse import OptionParser
from common import fastsimTrackingHelpers as helper
from collections import OrderedDict

parser = OptionParser()
# Require input
parser.add_option('-d', metavar='F', type='string', action='store',
                default =   '',
                dest    =   'dir',
                help    =   'Directory to validate')
parser.add_option("--steps", type='string', action="store", 
                default =   '',
                dest    =   "steps",
                help    =   "Comma separated list of steps. Possible are AOD,TRACKVAL,MINIAOD,BTAGVAL,NANOAOD,ANALYSIS,ALL.")
# Provided defaults
parser.add_option("--bypassChecks", action="store_true", 
                default =   False,
                dest    =   "bypassChecks",
                help    =   "Bypass check to see previous version finished (useful if most crab jobs are finished)")
parser.add_option("--SCRAM", action="store_true", 
                default =   False,
                dest    =   "scram",
                help    =   "Scram the area before processing")
parser.add_option("--CRAB", action="store_true", 
                default =   False,
                dest    =   "crab",
                help    =   "Run steps with crab when applicable")
parser.add_option('-t','--tag', metavar='F', type='string', action='store',
                default =   '',
                dest    =   'tag',
                help    =   'Name for identifying CRAB run')
parser.add_option('--nevents', metavar='F', type='string', action='store',
                default =   '1000',
                dest    =   'nevents',
                help    =   'Number of events to run')
parser.add_option('--cmsDriver', metavar='F', type='string', action='store',
                default =   '',
                dest    =   'cmsDriver',
                help    =   'Additional cmsDriver.py arguments that are not included in the definitions in fastsimTrackingValidation.py')
parser.add_option('--cmssw', metavar='F', type='string', action='store',
                default =   'CMSSW_10_6_12',
                dest    =   'cmssw',
                help    =   'CMSSW release to use')
parser.add_option('--storageSite', metavar='F', type='string', action='store',
                default =   'T3_US_FNALLPC',
                dest    =   'storageSite',
                help    =   'CRAB storage site')
# Config to use as base options
parser.add_option('-c', '--config', metavar='F', type='string', action='store',
                default =   '',
                dest    =   'config',
                help    =   'JSON config with options set')
# parser.add_option('--eosPath', metavar='F', type='string', action='store',
#                 default =   '',
#                 dest    =   'eosPath',
#                 help    =   'EOS path')

options = helper.handleOptions(parser)

#------------------------------------------------------------#
if __name__ == '__main__':
    start = time.time()
    step_bools = helper.ParseSteps(options.steps)
    working_dir = helper.GetWorkingArea(options.cmssw,options.dir,step_bools)  

    timers = OrderedDict()
    with helper.cd(working_dir):
        os.environ = helper.cmsenv()

        if options.scram:
            helper.executeCmd('scram b clean; scram b -j 10')
            os.environ = helper.cmsenv()

        makers = helper.GetMakers(step_bools,options)

        for m in makers.keys():
            maker = makers[m]
            if maker == None or step_bools[m] == False: continue
            maker.run()
            maker.save()
            timers[maker.stepname] = time.time()

    # Print time
    end = time.time()
    prevtime = start
    for step in timers.keys():
        t = time.strftime("%H:%M:%S", time.gmtime(timers[step]-prevtime))
        print ('%s time: %s'%(step,t))
        prevtime = timers[step]
    print ('Total time: %s'%time.strftime("%H:%M:%S", time.gmtime(end-start)))
