import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *
from  PhysicsTools.NanoAOD.triggerObjects_cff import unpackedPatTrigger

### Muons

triggerObjectBParkTable = cms.EDProducer("TriggerObjectTableBParkProducer",
    name= cms.string("TrigObj"),
    src = cms.InputTag("unpackedPatTrigger"),
    # src = cms.InputTag("slimmedPatTrigger"),
    l1Muon = cms.InputTag("gmtStage2Digis","Muon"), #TODO: find equivalent for electrons
    selections = cms.VPSet(
        cms.PSet(
            name = cms.string("Muon"),
            id = cms.int32(13),
            sel = cms.string("type(83) && pt > 5 && coll('hltIterL3MuonCandidates')"), 
            l1seed = cms.string("type(-81)"), l1deltaR = cms.double(0.5),
            l2seed = cms.string("type(83) && coll('hltL2MuonCandidates')"),  l2deltaR = cms.double(0.3),
            qualityBits = cms.string("filter('hltL3fL1s*Park*')"), qualityBitsDoc = cms.string("1 = Muon filters for BPH parking"),
        ),
    ),
)

triggerObjectBParkTables = cms.Sequence( unpackedPatTrigger + triggerObjectBParkTable )

### Electrons

# see https://github.com/cms-sw/cmssw/blob/master/DataFormats/HLTReco/interface/TriggerTypeDefs.h for filter definitions
# used this config as reference: https://github.com/cms-sw/cmssw/blob/2a53ad993325fe72593bd588fbc7750927b434fb/PhysicsTools/NanoAOD/python/egamma_custom_cff.py
# also inspired by https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/triggerObjects_cff.py

electronTriggerObjectBParkTable = cms.EDProducer("ElectronTriggerObjectTableBParkProducer",
    name= cms.string("EGTrigObj"),
    src = cms.InputTag("unpackedPatTrigger"),
    l1EGamma = cms.InputTag("caloStage2Digis","EGamma"),
    selections = cms.VPSet(
        cms.PSet(
            name = cms.string("Electron"),
            id = cms.int32(11),
            sel = cms.string("(type(82) || type(92)) && pt > 3 && coll('hltEgammaCandidates')"), #type 82 (TriggerElectron) or 92 (TriggerCluster)
            l1seed = cms.string("type(-82)"), # here is stage 1, before was type(-98) i.e. stage 2 TriggerL1EG
            l1deltaR = cms.double(0.3),
            #l2 seed not needed for electrons
            skipObjectsNotPassingQualityBits = cms.bool(True),
            qualityBits = cms.string("filter('hltDoubleEle*')"), qualityBitsDoc = cms.string("1 = Electron filters for BPH parking"),
        ),
    ),
)

myl1EGTable = cms.EDProducer("SimpleTriggerL1EGFlatTableProducer",
    src = cms.InputTag("caloStage2Digis","EGamma"),
    minBX = cms.int32(-2),
    maxBX = cms.int32(2),
    cut = cms.string(""),
    name= cms.string("L1EG"),
    doc = cms.string(""),
    extension = cms.bool(False),
    variables = cms.PSet(
        pt = Var("pt()", float, precision=12),
        phi = Var("phi()", float, precision=12),
        eta = Var("eta()", float, precision=12),
    ),
)

electronTriggerObjectBParkTables = cms.Sequence( unpackedPatTrigger + electronTriggerObjectBParkTable + myl1EGTable)