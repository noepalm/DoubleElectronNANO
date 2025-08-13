from __future__ import print_function
import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.nano_cff import *
from PhysicsTools.NanoAOD.vertices_cff import *
from PhysicsTools.NanoAOD.NanoAODEDMEventContent_cff import *
from PhysicsTools.BParkingNano.trgbits_cff import *

##for gen and trigger muon
from PhysicsTools.BParkingNano.genparticlesBPark_cff import *
from PhysicsTools.BParkingNano.particlelevelBPark_cff import *
from PhysicsTools.BParkingNano.triggerObjectsBPark_cff import *
# from PhysicsTools.BParkingNano.muonsBPark_cff import * 

## filtered input collections
from PhysicsTools.BParkingNano.electronsBPark_cff import * 
from PhysicsTools.BParkingNano.tracksBPark_cff import *

## Dielectron collection
from PhysicsTools.BParkingNano.dielectron_cff import *

# nanoSequenceOnlyFullSim = cms.Sequence(triggerObjectBParkTables + l1bits)
nanoSequenceOnlyFullSim = cms.Sequence(electronTriggerObjectBParkTables + l1bits)

nanoSequence = cms.Sequence(nanoMetadata + 
                            cms.Sequence(vertexTask) +
                            cms.Sequence(globalTablesTask) + cms.Sequence(vertexTablesTask) +
                            # triggerObjectBParkTables + l1bits)
                            electronTriggerObjectBParkTables + l1bits)

nanoSequenceMC = cms.Sequence(particleLevelBParkSequence + genParticleBParkSequence + 
                              cms.Sequence(globalTablesMCTask) + cms.Sequence(genWeightsTableTask) + genParticleBParkTables + lheInfoTable)

nanoSequenceMC_extra = cms.Sequence(cms.Sequence(genParticleTask)
                            + cms.Sequence(particleLevelTask)
                            + cms.Sequence(jetMCTask)
                            + cms.Sequence(muonMCTask)
                            # + cms.Sequence(electronMCTask) # gen-matching for (lowpt/ged) electrons already done
                            # + cms.Sequence(lowPtElectronMCTask)
                            + cms.Sequence(photonMCTask)
                            + cms.Sequence(metMCTable)
                            + cms.Sequence(genVertexTablesTask)
    )

from EgammaUser.EgammaPostRecoTools.EgammaPostRecoTools import setupEgammaPostRecoSeq

def nanoAOD_customizeEgammaPostRecoTools(process):
    setupEgammaPostRecoSeq(process,
                            runEnergyCorrections=False,
                            runVID=True,
                            era='2022-Prompt',
                            eleIDModules=[
                                # Run 3
                                'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_RunIIIWinter22_iso_V1_cff',
                                'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_RunIIIWinter22_noIso_V1_cff',
                                'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Winter22_122X_V1_cff',
                                # Run 2
                                'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V2_cff',
                                'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V2_cff',
                                'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V2_cff',
                                # # Run 2 BPark retrain
                                # 'PhysicsTools.BParkingNano.mvaElectronID_BParkRetrain_cff',
'PhysicsTools.BParkingNano.mvaElectronID_RunIII_custom_JPsitoEE_cff',
                            ],
                            isMiniAOD=True,
                        )
    return process

from PhysicsTools.BParkingNano.electronsTrigger_cff import *

def nanoAOD_customizeEle(process):
    process.nanoEleSequence = cms.Sequence(
        myUnpackedPatTrigger
        +myPFTriggerMatches
        +myLPTriggerMatches
        +mySlimmedPFElectronsWithEmbeddedTrigger
        +mySlimmedLPElectronsWithEmbeddedTrigger
        +electronTrgSelector
        +hltHighLevel)
    return process

# def nanoAOD_customizeMuonTriggerBPark(process):
#     process.nanoSequence = cms.Sequence( process.nanoSequence + muonBParkSequence + muonBParkTables)#+ muonTriggerMatchedTables)   ###comment in this extra table in case you want to create the TriggerMuon collection again.
#     return process

# def nanoAOD_customizeTrackFilteredBPark(process):
#     process.nanoTracksSequence = cms.Sequence( tracksBParkSequence + tracksBParkTables)
#     return process

def nanoAOD_customizeElectronFilteredBPark(process):
    process.nanoDiEleSequence     = cms.Sequence(electronsBParkSequence + electronBParkTables)
    return process

def nanoAOD_customizeElectronTriggerSelectionBPark(process):
    process.nanoDiEleSequence = cms.Sequence( process.nanoDiEleSequence + electronBParkTriggerSelection)
    return process

def nanoAOD_customizeTriggerBitsBPark(process):
    process.nanoSequence = cms.Sequence( process.nanoSequence + trgTables)
    return process

def nanoAOD_customizeDiElectron(process):
    process.nanoDiEleSequence = cms.Sequence( process.nanoDiEleSequence + DiElectronSequence)
    return process

def nanoAOD_customizeNanoContent(process):
    process.nanoSequence = cms.Sequence( PhysicsTools.NanoAOD.nano_cff.nanoSequence + electronTriggerObjectBParkTables + l1bits )
    return process

from FWCore.ParameterSet.MassReplace import massSearchReplaceAnyInputTag
def nanoAOD_customizeMC(process, saveAllNanoContent=False):
    for name, path in process.paths.iteritems():
        # replace all the non-match embedded inputs with the matched ones
        massSearchReplaceAnyInputTag(path, 'muonTrgSelector:SelectedMuons', 'selectedMuonsMCMatchEmbedded')
        #massSearchReplaceAnyInputTag(path, 'electronTrgSelector:SelectedElectrons', 'selectedElectronsMCMatchEmbedded') # Is this needed if the trigger is emulated ???
        massSearchReplaceAnyInputTag(path, 'electronsForAnalysis:SelectedElectrons', 'selectedElectronsMCMatchEmbedded')
        massSearchReplaceAnyInputTag(path, 'tracksBPark:SelectedTracks', 'tracksBParkMCMatchEmbedded')

        # modify the path to include mc-specific info
        path.insert(0, nanoSequenceMC)
        if saveAllNanoContent: path.insert(0, nanoSequenceMC_extra)
        # path.replace(process.muonBParkSequence, process.muonBParkMC)
        path.replace(process.electronsBParkSequence, process.electronBParkMC)
        path.replace(process.tracksBParkSequence, process.tracksBParkMC)
