import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

trgTable = cms.EDProducer( "TrgBitTableProducer",
                          hltresults = cms.InputTag("TriggerResults::HLT"),
                          l1results  = cms.InputTag("gtStage2Digis::RECO"),
                          #add interesting paths
                          paths = cms.vstring(
                                  'HLT_DoubleEle10_eta1p22_mMax6',
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
                                  'HLT_DoubleEle4_eta1p22_mMax6',
                                  #VBF 2023
                                  'HLT_VBF_DiPFJet105_40_Mjj1000_Detajj3p5',
                                  'HLT_VBF_DiPFJet110_40_Mjj1000_Detajj3p5',
                                  'HLT_VBF_DiPFJet125_45_Mjj1000_Detajj3p5',
                                  'HLT_VBF_DiPFJet125_45_Mjj720_Detajj3p0',
                                  'HLT_VBF_DiPFJet45_Mjj500_Detajj2p5_Photon12',
                                  'HLT_VBF_DiPFJet50_Mjj500_Detajj2p5_Photon22',
                                  'HLT_VBF_DiPFJet45_Mjj500_Detajj2p5_Ele12_eta2p1_WPTight_Gsf',
                                  'HLT_VBF_DiPFJet50_Mjj500_Detajj2p5_Ele22_eta2p1_WPTight_Gsf',
                                  #VBF 2024
                                  'HLT_VBF_DiPFJet125_45_Mjj1050',
                                  'HLT_VBF_DiPFJet125_45_Mjj1200',
                                  'HLT_VBF_DiPFJet50_Mjj600_Ele22_eta2p1_WPTight_Gsf',
                                  'HLT_VBF_DiPFJet50_Mjj650_Ele22_eta2p1_WPTight_Gsf',
                                  'HLT_VBF_DiPFJet50_Mjj650_Photon22',
                                  'HLT_VBF_DiPFJet50_Mjj750_Photon22'
                                  ),
                          seeds = cms.vstring('L1_DoubleEG11_er1p2_dR_Max0p6',
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
                                  'L1_DoubleJet_90_30_DoubleJet30_Mass_Min620',
                                  'L1_DoubleJet_90_30_DoubleJet30_Mass_Min800',
                                  'L1_DoubleJet_100_30_DoubleJet30_Mass_Min620',
                                  'L1_DoubleJet_100_30_DoubleJet30_Mass_Min800',
                                  'L1_DoubleJet_110_35_DoubleJet35_Mass_Min620',
                                  'L1_DoubleJet_110_35_DoubleJet35_Mass_Min800',
                                  'L1_DoubleJet_110_35_DoubleJet35_Mass_Min850',
                                  'L1_DoubleJet45_Mass_Min550_LooseIsoEG20er2p1_RmOvlp_dR0p2',
                                  'L1_DoubleJet45_Mass_Min600_LooseIsoEG20er2p1_RmOvlp_dR0p2',
                                  'L1_DoubleJet40_Mass_Min450_IsoEG10er2p1_RmOvlp_dR0p2',
                                  ),
)

trgTables = cms.Sequence(trgTable)

###########
# Modifiers
###########

# from PhysicsTools.BParkingNano.modifiers_cff import *

# old modifier:
# DiEle.toModify(trgTable, paths = [], seeds = [])

# # 2024 paths/seeds only
# BToKEE_DiEle.toModify(trgTable,
#                       paths = ['HLT_DoubleEle6p5_eta1p22_mMax6',
#                                'HLT_DoubleEle8_eta1p22_mMax6',
#                                'HLT_DoubleEle10_eta1p22_mMax6'],
#                       seeds = ['L1_DoubleEG11_er1p2_dR_Max0p6'],
# )

# BToKMuMu_DiMuon.toModify(trgTable,
#                          paths = ["HLT_DoubleMu4_JpsiTrk_Displaced"],
#                          seeds = ["L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4",
#                                   "L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4",
#                                   "L1_DoubleMu4p5_SQ_OS_dR_Max1p2",
#                                   "L1_DoubleMu4_SQ_OS_dR_Max1p2",],
# )
