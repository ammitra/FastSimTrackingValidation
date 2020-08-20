import subprocess, os, ROOT
from common import fastsimTrackingHelpers as helper
from optparse import OptionParser
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

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
                default =   'ALL',
                dest    =   "steps",
                help    =   "Comma separated list of steps. Possible are TRACKVAL,BTAGVAL,ANALYSIS,ALL.")
(options, args) = parser.parse_args()

cwd = os.getcwd()

def BtagValPlotting(valdirs,names):
    if len(valdirs) > 2:
        print ('WARNING: BTAGVAL can only compare two sets at a time. Only the first two listed will be considered.')

    first = valdirs[0] if '.root' in valdirs[0] else valdirs[0]+'/FastSimValWorkspace/BTAGVAL/harvest.root'
    second = valdirs[1] if '.root' in valdirs[1] else valdirs[1]+'/FastSimValWorkspace/BTAGVAL/harvest.root'

    with helper.cd('btag_plots/'):
        plotFactory_cmd = 'python %s/Validation-Tools/plotProducer/scripts/plotFactory.py -f ../../%s -F ../../%s -r %s -R %s -s TTbar_13TeV_TuneCUETP8M1 -S TTbar_13TeV_TuneCUETP8M1'%(cwd,first,second,names[0],names[1])
        helper.executeCmd(plotFactory_cmd,bkg=False)

def TrackValPlotting(valdirs):
    trackval_cmd = 'makeTrackValidationPlots.py -o tracking_plots'
    for d in valdirs:
        if '.root' in d:
            trackval_cmd+=' ../%s'%(d)
        else:
            trackval_cmd+=' ../%s/FastSimValWorkspace/TRACKVAL/harvestTracks.root'%(d)
    helper.executeCmd(trackval_cmd,bkg=False)

def AnalysisPlotting(valdirs,names):
    if len(valdirs) > 2:
        print ('WARNING: ANALYSIS can only compare up to four sets at a time. Only the first four listed will be considered.')

    canvases = {}
    legends = {}
    colors = [ROOT.kRed,ROOT.kBlue,ROOT.kGreen,ROOT.kOrange]
    for i,d in enumerate(valdirs):
        if '.root' in d:
            f = ROOT.TFile.Open(d)
        else:
            f = ROOT.TFile.Open('../%s/FastSimValWorkspace/ANALYSIS/FastSim_ANALYSIS.root'%d)
        for key in f.GetListOfKeys():
            hname = key.GetName()
            if hname not in canvases.keys():
                canvases[hname] = ROOT.TCanvas(hname,hname,800,700)
                legends[hname] = ROOT.TLegend(0.65,0.75,0.95,0.9)
            
            h = f.Get(key.GetName())
            canvases[hname].cd()
            h.SetDirectory(0)
            h.SetLineColor(colors[i])
            h.Scale(1-i*0.1)
            # if i == 0:
            #     h.SetFillColor(ROOT.kYellow)
            legends[hname].AddEntry(h,names[i],'l')
            h.Draw('same hist e')
            legends[hname].Draw()
    
    for ckey in canvases.keys():
        canvases[ckey].Print('AnalysisVars/%s.pdf'%ckey,'pdf')

def optionsCheck(options):
    if options.tag =='':
        raise ValueError('Option `tag` must be specified. This determines directory where plots will be saved.')

#------------------------------------------------------------#
if __name__ == '__main__':
    optionsCheck(options)

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
    with helper.cd(options.tag):
        if 'ALL' in options.steps or 'BTAGVAL' in options.steps:
            BtagValPlotting(valdirs,names)
        if 'ALL' in options.steps or 'TRACKVAL' in options.steps:
            TrackValPlotting(valdirs)
        if 'ALL' in options.steps or 'ANALYSIS' in options.steps:
            if not os.path.exists('AnalysisVars/'):
                os.mkdir('AnalysisVars')
            AnalysisPlotting(valdirs,names)
