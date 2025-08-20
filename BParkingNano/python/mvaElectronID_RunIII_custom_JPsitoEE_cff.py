import FWCore.ParameterSet.Config as cms
from RecoEgamma.ElectronIdentification.Identification.mvaElectronID_tools import mvaClassName
from os import path

#Egamma presentation on this ID for Run3:
#https://indico.cern.ch/event/1220628/contributions/5134878/attachments/2546114/4384580/Run%203%20Electron%20MVA%20based%20ID%20training.pdf

mvaTag = "RunIIICustomJPsitoEE"
mvaVariablesFileRun3custom = "PhysicsTools/BParkingNano/data/ElectronIDVariables.txt"
weightFileDir = "PhysicsTools/BParkingNano/data/PFRetrainWeightFiles/"


mvaWeightFiles = cms.vstring(
     path.join(weightFileDir, "electron_id_EB.root"), # EB1_5
     path.join(weightFileDir, "electron_id_EB.root"), # EB2_5
     path.join(weightFileDir, "electron_id_EE.root"), # EE_5
     path.join(weightFileDir, "electron_id_EB.root"), # EB1_10
     path.join(weightFileDir, "electron_id_EB.root"), # EB2_10
     path.join(weightFileDir, "electron_id_EE.root"), # EE_10
     )

EleMVA_6CategoriesCuts = [
    "pt < 5. && abs(superCluster.eta) < 0.800",
    "pt < 5. && abs(superCluster.eta) >= 0.800 && abs(superCluster.eta) < 1.479",
    "pt < 5. && abs(superCluster.eta) >= 1.479",
    "pt >= 5. && abs(superCluster.eta) < 0.800",
    "pt >= 5. && abs(superCluster.eta) >= 0.800 && abs(superCluster.eta) < 1.479",
    "pt >= 5. && abs(superCluster.eta) >= 1.479",
    ]

# mvaEleID_RunIII_custom_JPsitoEE_V1_wp80_container = EleMVA_WP(
#     idName = "mvaEleID-RunIII-custom-JPsitoEE-V1-wp80", mvaTag = mvaTag,
#     cutCategory0 = "-0.18", # EB1_5
#     cutCategory1 = "-0.42", # EB2_5
#     cutCategory2 = "-0.47", # EE_5
#     cutCategory3 = "1.68", # EB1_10
#     cutCategory4 = "1.50", # EB2_10
#     cutCategory5 = "1.29", # EE_10
#     )



# mvaEleID_RunIII_custom_JPsitoEE_V1_wp90_container = EleMVA_WP(
#     idName = "mvaEleID-RunIII-custom-JPsitoEE-V1-wp90", mvaTag = mvaTag,
#     cutCategory0 = "-0.89", # EB1_5
#     cutCategory1 = "-1.13", # EB2_5
#     cutCategory2 = "-1.35", # EE_5
#     cutCategory3 = "0.91", # EB1_10
#     cutCategory4 = "0.74", # EB2_10
#     cutCategory5 = "0.33", # EE_10
    #)

# workingPoints = dict(
#     wp80 = mvaEleID_RunIII_custom_JPsitoEE_V1_wp80_container,
#     wp90 = mvaEleID_RunIII_custom_JPsitoEE_V1_wp90_container
# )

mvaEleID_RunIII_custom_JPsitoEE_V1_producer_config = cms.PSet(
    mvaName             = cms.string(mvaClassName),
    mvaTag              = cms.string(mvaTag),
    nCategories         = cms.int32(6),
    categoryCuts        = cms.vstring(*EleMVA_6CategoriesCuts),
    weightFileNames     = mvaWeightFiles,
    variableDefinition  = cms.string(mvaVariablesFileRun3custom)
    )

# mvaEleID_RunIII_custom_JPsitoEE_V1_wp80 = configureVIDMVAEleID( mvaEleID_RunIII_custom_JPsitoEE_V1_wp80_container )
# mvaEleID_RunIII_custom_JPsitoEE_V1_wp90 = configureVIDMVAEleID( mvaEleID_RunIII_custom_JPsitoEE_V1_wp90_container )

# mvaEleID_RunIII_custom_JpsitoEE_V1_wp80.isPOGApproved = cms.untracked.bool(True)
# mvaEleID_RunIII_custom_JpsitoEE_V1_wp90.isPOGApproved = cms.untracked.bool(True)
