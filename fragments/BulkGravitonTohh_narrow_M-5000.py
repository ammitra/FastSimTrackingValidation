import FWCore.ParameterSet.Config as cms
externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
 args = cms.vstring('/cvmfs/cms.cern.ch/phys_generator/gridpacks/2017/13TeV/madgraph/V5_2.4.2/BulkGravitonTohhTohbbhbb/widthNarrow/BulkGravitonTohh_widthNarrow_M-5000_MG5.2.4.2_NNPDF31_lo_as_0130_CMSSW_7_1_30_tarball.tar.xz'),
 nEvents = cms.untracked.uint32(5000),
 numberOfParameters = cms.uint32(1),
 outputFile = cms.string('cmsgrid_final.lhe'),
 scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)
#Link to datacards:https://github.com/cms-sw/genproductions/tree/mg242legacy/bin/MadGraph5_aMCatNLO/cards/production/2017/13TeV/b2g_dihiggs
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP2Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *
generator = cms.EDFilter("Pythia8HadronizerFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13000.),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP2SettingsBlock,
        pythia8PSweightsSettingsBlock,
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP2Settings',
                                    'pythia8PSweightsSettings',
                                    )
    )
)