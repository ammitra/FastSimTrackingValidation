import subprocess
from optparse import OptionParser
from common import fastsimTrackingHelpers as helper

parser = OptionParser()
# Require input

parser.add_option('-d', metavar='F', type='string', action='store',
                default =   '',
                dest    =   'dir',
                help    =   'Directory to validate')
parser.add_option("--steps", type='string', action="store", 
                default =   '',
                dest    =   "steps",
                help    =   "Comma separated list of steps. Possible are AOD,TRACKVAL,MINIAOD,BTAGVAL,NANOAOD,ANALYSIS.")
# Provided defaults
parser.add_option("--ALL", action="store_true", 
                default =   False,
                dest    =   "all",
                help    =   "Run full workflow")
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
                help    =   'Name for identifying the run')
parser.add_option('--cfi', metavar='F', type='string', action='store',
                default =   'TTbar_13TeV_TuneCUETP8M1_cfi',
                dest    =   'cfi',
                help    =   'Set cfi')
parser.add_option('--nevents', metavar='F', type='string', action='store',
                default =   '1000',
                dest    =   'nevents',
                help    =   'Number of events to run')
parser.add_option('--cmssw', metavar='F', type='string', action='store',
                default =   'CMSSW_10_6_12',
                dest    =   'cmssw',
                help    =   'CMSSW release to use')
parser.add_option('--storageSite', metavar='F', type='string', action='store',
                default =   'T3_US_FNALLPC',
                dest    =   'storageSite',
                help    =   'CRAB storage site')
# parser.add_option('--eosPath', metavar='F', type='string', action='store',
#                 default =   '',
#                 dest    =   'eosPath',
#                 help    =   'EOS path')

(options, args) = parser.parse_args()

#------------------------------------------------------------#
if __name__ == '__main__':
    step_bools = helper.ParseSteps(options.all,options.steps)
    working_dir = helper.GetWorkingArea(options.cmssw,options.dir,step_bools)

    with helper.cd(working_dir):
        helper.executeCmd("eval `scramv1 runtime -sh`")
        if options.scram:
            helper.executeCmd('scram b -j 10')
            helper.executeCmd("eval `scramv1 runtime -sh`")

        makers = helper.GetMakers(step_bools,options)

        for m in makers.keys():
            maker = makers[m]
            if maker == None or step_bools[m] == False: continue
            maker.run()
            maker.save()