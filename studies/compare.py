import subprocess, os, ROOT
from argparse import ArgumentParser
from common import fastsimTrackingHelpers as helper
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

parser = ArgumentParser()
parser.add_argument('-t', '--tag', dest='tag', default='',
		    help='Name of the directory containing DQM output from runTheMatrix',
		    required=True)

options = parser.parse_args()


def doBTag(plotDir, histos, title, xlabel, ylabel, norm=False):
    '''
    plotDir [str] = TDirectoryFile name containing relevant Btag histos
    histos [list] = list of b-tagging histogram names [bJet, cJet, DUSGjet]
    title [str]   = title for plot
    xlabel [str]  = x label for THStack
    ylabel [str]
    norm [bool]   = normalize histograms
    '''
    assert(len(histos)==3)
    # do b-tagging vars, across all years
    refBTag = ref.Get(plotDir)
    valBTag = val.Get(plotDir)
    # b jets
    refB = refBTag.Get(histos[0])
    valB = valBTag.Get(histos[0])
    formatHist(refB, ROOT.kRed, ROOT.kFullCircle)
    formatHist(valB, ROOT.kRed, ROOT.kOpenCircle)
    # c Jets
    refC = refBTag.Get(histos[1])
    valC = valBTag.Get(histos[1])
    formatHist(refC, ROOT.kGreen, ROOT.kFullCircle)
    formatHist(valC, ROOT.kGreen, ROOT.kOpenCircle)
    # DUSG jets
    refD = refBTag.Get(histos[2])
    valD = valBTag.Get(histos[2])
    formatHist(refD, ROOT.kBlue, ROOT.kFullCircle)
    formatHist(valD, ROOT.kBlue, ROOT.kOpenCircle)
    # normalize if required
    if norm:
        refB.Scale(1./refB.Integral())
        valB.Scale(1./valB.Integral())
        refC.Scale(1./refC.Integral())
        valC.Scale(1./valC.Integral())
        refD.Scale(1./refD.Integral())
        valD.Scale(1./valD.Integral())
    # now actually plot
    if not norm:
        c.SetLogy(1)
    stack = ROOT.THStack(title,'{};{};{}'.format(title,xlabel,ylabel))
    stack.Add(refB)
    stack.Add(valB)
    stack.Add(refC)
    stack.Add(valC)
    stack.Add(refD)
    stack.Add(valD)
    stack.Draw('nostack LP')
    if not norm:
	l = ROOT.TLegend(0.12,0.12,0.35,0.35)
    else:
	l = ROOT.TLegend(0.5,0.65,0.7,0.85)
    l.SetHeader()
    l.SetBorderSize(0)
    # create dummy histos for the legends
    dummyRef = ROOT.TH1F("dummy_ref", "", 1, 0, 1)
    dummyVal = ROOT.TH1F("dummy_val", "", 1, 0, 1)
    dummyRef.SetMarkerStyle(ROOT.kFullSquare)
    dummyVal.SetMarkerStyle(ROOT.kOpenSquare)
    l.AddEntry(dummyRef,'base','p')
    l.AddEntry(dummyVal, tag, 'p')
    l.AddEntry(refB, 'B jets', 'p')
    l.AddEntry(refC, 'C jets', 'p')
    l.AddEntry(refD, 'DUSG jets', 'p')
    l.Draw()
    c.Print('base_vs_{}.pdf'.format(tag))
    c.SetLogy(0)
    c.Clear()

def generateLegend(ratioPlot):
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
    p = ratioPlot.GetUpperPad()
    p.BuildLegend()
    p.Modified()
    p.Update()

def formatHist(hist, color, style):
    hist.SetMarkerColor(color)
    hist.SetMarkerStyle(style)

if __name__=='__main__':
    tag = options.tag
    
    base = '../../BaseFastSim/CMSSW_10_6_4/src/5.1_TTbar+TTbarFS+HARVESTFS'
    comp = '../../BaseFastSim_LucasChanges/CMSSW_10_6_4/src/5.1_TTbar+TTbarFS+HARVESTFS_{}'.format(tag)
    
    # first set up the ROOT files
    refFile = ROOT.TFile.Open('{}/DQM_V0001_R000000001__Global__CMSSW_X_Y_Z__RECO.root'.format(base),'READ')
    valFile = ROOT.TFile.Open('{}/DQM_V0001_R000000001__Global__CMSSW_X_Y_Z__RECO.root'.format(comp),'READ')
    ref = refFile.Get('DQMData/Run 1')
    val = valFile.Get('DQMData/Run 1')

    # now set up the plotting 
    c = ROOT.TCanvas('canvas')
    c.Print('base_vs_{}.pdf['.format(tag))
    c.Clear()

    # do pulls and residuals
    pullRes = [
	'dxypull_vs_eta',
	'dxyres_vs_eta',
	'dzpull_vs_eta',
	'dzres_vs_eta',
	'dzres_vs_pt'
    ]
    for pr in pullRes:
        refVar = ref.Get('Tracking/Run summary/Track/general_trackingParticleRecoAsssociation/{}'.format(pr))
	refVar.SetTitle('{}_BASE'.format(pr))
	valVar = val.Get('Tracking/Run summary/Track/general_trackingParticleRecoAsssociation/{}'.format(pr))
	valVar.SetTitle('{}_{}'.format(pr, tag))
	c.Divide(2,1)
	c.cd(1)
	refVar.Draw('colz')
	c.cd(2)
	valVar.Draw('colz')
	c.Print('base_vs_{}.pdf'.format(tag))
	c.Clear()

    # do b tagging 
    doBTag(
        plotDir = 'Btag/Run summary/deepCSV_BvsAll_GLOBAL',
        histos = ['effVsDiscrCut_discr_deepCSV_BvsAll_GLOBALB','effVsDiscrCut_discr_deepCSV_BvsAll_GLOBALC','effVsDiscrCut_discr_deepCSV_BvsAll_GLOBALDUSG'],
        title='deepCSV_BvsAll',
        xlabel='Cut on Discriminant',
        ylabel='Efficiency'
    )
    doBTag(
        plotDir = 'Btag/Run summary/deepCSV_BvsAll_GLOBAL',
        histos = ['discr_deepCSV_BvsAll_GLOBALB','discr_deepCSV_BvsAll_GLOBALC','discr_deepCSV_BvsAll_GLOBALDUSG'],
        title='deepCSV_BvsAll',
        xlabel='Discriminant',
        ylabel='Normalized entries',
        norm=True
    )
    doBTag(
        plotDir = 'Btag/Run summary/CSVv2_GLOBAL',
        histos = ['effVsDiscrCut_discr_CSVv2_GLOBALB','effVsDiscrCut_discr_CSVv2_GLOBALC','effVsDiscrCut_discr_CSVv2_GLOBALDUSG'],
        title='CSVv2',
        xlabel='Cut on Discriminant',
        ylabel='Efficiency'
    )
    doBTag(
        plotDir = 'Btag/Run summary/CSVv2_GLOBAL',
        histos = ['discr_CSVv2_GLOBALB','discr_CSVv2_GLOBALC','discr_CSVv2_GLOBALDUSG'],
        title='CSVv2',
        xlabel='Discriminant',
        ylabel='Normalized entries',
        norm=True
    )
    # now do other tracking vars
    trackVars = ['effic',   		# efficiency vs eta
		 'efficPt',		# efficiency vs pT
		 'effic_vs_phi'		# efficiency vs phi
    ]
    for var in trackVars:
	refVar = ref.Get('Tracking/Run summary/Track/general_trackingParticleRecoAsssociation/{}'.format(var))
        valVar = val.Get('Tracking/Run summary/Track/general_trackingParticleRecoAsssociation/{}'.format(var))
	plot = ROOT.TRatioPlot(refVar, valVar, 'diffsig')
	plot.Draw()
	generateLegend(plot)
	c.Print('base_vs_{}.pdf'.format(tag))
	c.Clear()

    # then do pseudorapidity
    refEta = ref.Get("Tracking/Run summary/Track/simulation/etaSIM")
    valEta = val.Get("Tracking/Run summary/Track/simulation/etaSIM")
    eta = ROOT.TRatioPlot(refEta, valEta, 'diffsig')
    eta.Draw()
    generateLegend(eta)
    c.Print('base_vs_{}.pdf'.format(tag))
    c.Clear()

    # finish and close the pdf
    c.Print('base_vs_{}.pdf]'.format(tag))
