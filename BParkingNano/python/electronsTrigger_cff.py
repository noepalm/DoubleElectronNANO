import FWCore.ParameterSet.Config as cms

paths = []
seeds = []

is_new = False #If True, 2024 triggers only

if is_new:
    paths = ['HLT_DoubleEle6p5_eta1p22_mMax6',
            'HLT_DoubleEle8_eta1p22_mMax6',
            'HLT_DoubleEle10_eta1p22_mMax6']
    seeds = ['L1_DoubleEG11_er1p2_dR_Max0p6']
else:
    paths=['HLT_DoubleEle10_eta1p22_mMax6',
        'HLT_DoubleEle9p5_eta1p22_mMax6',
        'HLT_DoubleEle9_eta1p22_mMax6',
        'HLT_DoubleEle8p5_eta1p22_mMax6',
        'HLT_DoubleEle8_eta1p22_mMax6',
        'HLT_DoubleEle7p5_eta1p22_mMax6',
        'HLT_DoubleEle7_eta1p22_mMax6',
        'HLT_DoubleEle6p5_eta1p22_mMax6',
        'HLT_DoubleEle6_eta1p22_mMax6',
        'HLT_DoubleEle5p5_eta1p22_mMax6',
        'HLT_DoubleEle5_eta1p22_mMax6',
        'HLT_DoubleEle4p5_eta1p22_mMax6',
        'HLT_DoubleEle4_eta1p22_mMax6'
    ]
    seeds = ['L1_DoubleEG11_er1p2_dR_Max0p6',
         'L1_DoubleEG10p5_er1p2_dR_Max0p6',
         'L1_DoubleEG10_er1p2_dR_Max0p6',
         'L1_DoubleEG9p5_er1p2_dR_Max0p6',
         'L1_DoubleEG9_er1p2_dR_Max0p7',
         'L1_DoubleEG8p5_er1p2_dR_Max0p7',
         'L1_DoubleEG8_er1p2_dR_Max0p7',
         'L1_DoubleEG7p5_er1p2_dR_Max0p7',
         'L1_DoubleEG7_er1p2_dR_Max0p8',
         'L1_DoubleEG6p5_er1p2_dR_Max0p8',
         'L1_DoubleEG6_er1p2_dR_Max0p8',
         'L1_DoubleEG5p5_er1p2_dR_Max0p8',
         'L1_DoubleEG5_er1p2_dR_Max0p9',
         'L1_DoubleEG4p5_er1p2_dR_Max0p9',
         'L1_DoubleEG4_er1p2_dR_Max0p9',
    ]

paths_OR = " || ".join([ 'path( "{:s}_v*" )'.format(path) for path in paths])

# https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/PatAlgos/plugins/PATTriggerObjectStandAloneUnpacker.cc
myUnpackedPatTrigger = cms.EDProducer(
    "PATTriggerObjectStandAloneUnpacker",
    patTriggerObjectsStandAlone = cms.InputTag("slimmedPatTrigger"),
    triggerResults = cms.InputTag("TriggerResults::HLT"),
    unpackFilterLabels = cms.bool(True),
)

# https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/PatAlgos/python/triggerLayer1/triggerMatcherExamples_cfi.py
# https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/PatAlgos/plugins/PATTriggerMatcher.cc
myPFTriggerMatches = cms.EDProducer(
    # "PATTriggerMatcherDEtaLessByDR", # match by DeltaEta only, best match by DeltaR
    #"PATTriggerMatcherDEtaLessByDEta", # match by DeltaEta only, best match by DeltaEta
    "PATTriggerMatcherDRDPtLessByR", # match by DeltaR only, best match by DeltaR
    src = cms.InputTag("customSlimmedElectrons"),
    matched = cms.InputTag("myUnpackedPatTrigger"),
    matchedCuts = cms.string(paths_OR), # e.g. 'path("HLT_DoubleEle6_eta1p22_mMax6_v*")'
    maxDeltaR = cms.double(0.3),
    maxDPtRel = cms.double(0.5),
    resolveAmbiguities    = cms.bool( True ), # only one match per trigger object
    resolveByMatchQuality = cms.bool( True ), # take best match found per reco object (e.g. by DeltaR)
)

myLPTriggerMatches = myPFTriggerMatches.clone(
    src = cms.InputTag("slimmedLowPtElectrons"),
    # NB: matching PF and LP collections separately;
    #     they can be matched to the same trigger object
)

# https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/PatAlgos/plugins/PATTriggerMatchEmbedder.cc
mySlimmedPFElectronsWithEmbeddedTrigger = cms.EDProducer(
    "PATTriggerMatchElectronEmbedder",
    src = cms.InputTag("customSlimmedElectrons"),
    matches = cms.VInputTag('myPFTriggerMatches'),
)

mySlimmedLPElectronsWithEmbeddedTrigger = cms.EDProducer(
    "PATTriggerMatchElectronEmbedder",
    src = cms.InputTag("slimmedLowPtElectrons"),
    matches = cms.VInputTag('myLPTriggerMatches'),
)

electronTrgSelector = cms.EDProducer(
    "ElectronTriggerSelector",
    electronCollection = cms.InputTag("mySlimmedPFElectronsWithEmbeddedTrigger"),
    bits = cms.InputTag("TriggerResults","","HLT"),
    prescales = cms.InputTag("patTrigger"),
    objects = cms.InputTag("slimmedPatTrigger"),
    vertexCollection = cms.InputTag("offlineSlimmedPrimaryVertices"),
    maxdR_matching = cms.double(10.), # not used
    dzForCleaning_wrtTrgElectron = cms.double(1.),
    filterElectron = cms.bool(True),
    ptMin = cms.double(2.),
    absEtaMax = cms.double(1.25),
    HLTPaths = cms.vstring(paths),
    L1seeds = cms.vstring(seeds),
)

# first skim based on trigger -- discard events that don't fire any of the paths
hltHighLevel = cms.EDFilter("HLTHighLevel",
                            TriggerResultsTag = cms.InputTag("TriggerResults", "", "HLT"),
                            HLTPaths = cms.vstring(              # provide list of HLT paths (or patterns) you want
                                [path + "_v*" for path in paths]
                            ),       
                            eventSetupPathsKey = cms.string(''), # not empty => use read paths from AlCaRecoTriggerBitsRcd via this key
                            andOr = cms.bool(True),              # how to deal with multiple triggers: True (OR) accept if ANY is true, False (AND) accept if ALL are true
                            throw = cms.bool(True),             # throw exception on unknown path names
)

#electronsTriggerSequence = cms.Sequence(
#unpackedPatTrigger
#    #myTriggerMatches
#    #+mySlimmedElectronsWithEmbeddedTrigger
#    electronTrgSelector
#    +countTrgElectrons
#)

#electronsTriggerTask = cms.Task(
#    #myTriggerMatches,
#    mySlimmedElectronsWithEmbeddedTrigger,
#    electronTrgSelector,
#    countTrgElectrons,
#)

# ---------------------------------------
# MODIFIERS FOR TRIGGER MATCHING STUDIES

from PhysicsTools.BParkingNano.modifiers_cff import *

triggerMatchingStudy.toModify(myPFTriggerMatches,
    maxDeltaR = cms.double(2.0),
    maxDPtRel = cms.double(1.0),
    resolveAmbiguities    = cms.bool( False ),
    resolveByMatchQuality = cms.bool( False ),
)

triggerMatchingStudy.toModify(myLPTriggerMatches,
    maxDeltaR = cms.double(2.0),
    maxDPtRel = cms.double(1.0),
    resolveAmbiguities    = cms.bool( False ),
    resolveByMatchQuality = cms.bool( False ),
)

triggerMatchingStudy.toModify(hltHighLevel,
    HLTPaths = cms.vstring([]) # disable HLT selection
)

vbfSkimming2024.toModify(hltHighLevel,
    HLTPaths = cms.vstring(
        [ f"{p}_v*" for p in [
        'HLT_VBF_DiPFJet125_45_Mjj1050',
        'HLT_VBF_DiPFJet125_45_Mjj1200',
        'HLT_VBF_DiPFJet50_Mjj600_Ele22_eta2p1_WPTight_Gsf',
        'HLT_VBF_DiPFJet50_Mjj650_Ele22_eta2p1_WPTight_Gsf',
        'HLT_VBF_DiPFJet50_Mjj650_Photon22',
        'HLT_VBF_DiPFJet50_Mjj750_Photon22'
        ]]
    )
)


efficiencyStudy.toModify(hltHighLevel,
    HLTPaths = cms.vstring([]) # disable HLT selection
)