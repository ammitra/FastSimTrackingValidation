import subprocess, os
from common import fastsimTrackingHelpers as helper
from optparse import OptionParser

parser = OptionParser()
# Require input
parser.add_option('--tag', metavar='F', type='string', action='store',
                default =   '',
                dest    =   'tag',
                help    =   'Tag to organize this comparison (outputs will be saved in directory with this name)')
parser.add_option('-d', metavar='F', type='string', action='store',
                default =   '',
                dest    =   'dirs',
                help    =   'Directories (include CMSSW dir) to validate (comma separated) with colon to provide name if desired.')
parser.add_option('-n', metavar='F', type='string', action='store',
                default =   '',
                dest    =   'names',
                help    =   'Comma separated list of dir names in same order as dirs option.')                
parser.add_option('-s',"--steps", type='string', action="store", 
                default =   '',
                dest    =   "steps",
                help    =   "Comma separated list of steps. Possible are TRACKVAL,BTAGVAL,ANALYSIS,ALL.")

def BtagValPlotting(valdirs,names):
    if len(valdirs) > 2:
        print 'WARNING: BTAGVAL can only compare two sets at a time. Only the first two listed will be considered.'

    plotFactory_cmd = 'python Validation-Tools/plotProducer/scripts/plotFactory.py -f %s/FastSimValWorkspace/BTAGVAL/harvest.root -F %s/FastSimValWorkspace/BTAGVAL/harvest.root -r %s -R %s -s TTbar_13TeV_TuneCUETP8M1 -S TTbar_13TeV_TuneCUETP8M1_cfi'%(valdirs[0],valdirs[1],names[0],names[1])
    header.executeCmd(plotFactory_cmd,bkg=True)

def TrackValPlotting(valdirs):
    trackval_cmd = 'makeTrackValidationPlots.py -o tracking_plots'
    for d in valdirs:
        trackval_cmd+=' %s/FastSimValWorkspace/TRACKVAL/harvestTracks.root'%(d)
    header.executeCmd(plotFactory_cmd,bkg=True)

def AnalysisPlotting():
    pass

(options, args) = parser.parse_args()

#------------------------------------------------------------#
if __name__ == '__main__':
    # Grab comparison info
    valdirs = options.dirs.split(',')
    if options.names == '':
        names = []
        for n in range(len(valdirs)):
            names.append('Set '+str(n))
    else:
        names = options.names.split(',')

    # Setup storage of comparisons
    if not os.path.isdir(options.tag):
        print('mkdir '+options.tag)
        os.mkdir(options.tag)
    # Change dir and do each step
    with header.cd(options.tag):
        if 'ALL' in options.steps or 'BTAGVAL' in options.steps:
            BtagValPlotting(valdirs,names)
        if 'ALL' in options.steps or 'TRACKVAL' in options.steps:
            TrackValPlotting(valdirs)
        if 'ALL' in options.steps or 'ANALYSIS' in options.steps:
            AnalysisPlotting()