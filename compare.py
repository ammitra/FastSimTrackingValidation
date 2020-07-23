import subprocess, os
from optparse import OptionParser

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

def BtagValPlotting(projDir1,projDir2,name1,name2):
    # plotFactory_cmd = 'python %s/Validation-Tools/plotProducer/scripts/plotFactory.py -f '
    # subprocess.Popen()
    pass
def TrackValPlotting():
    # subprocess.Popen('makeTrackValidationPlots.py %s -o tracking_plots'%(options.eosPath+self.prev.crabDir))
    pass
def AnalysisPlotting():
    pass

(options, args) = parser.parse_args()

#------------------------------------------------------------#
if __name__ == '__main__':
    BtagValPlotting()
    TrackValPlotting()
    AnalysisPlotting()