import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.lowPtElectrons_cff import modifiedLowPtElectrons, updatedLowPtElectrons

# Electron ID MVA raw values
mvaConfigsForEleProducer = cms.VPSet()
from PhysicsTools.BParkingNano.mvaElectronID_BParkRetrain_cff \
    import mvaEleID_BParkRetrain_producer_config

mvaConfigsForEleProducer.append( mvaEleID_BParkRetrain_producer_config )

from PhysicsTools.BParkingNano.mvaElectronID_RunIII_custom_JPsitoEE_cff \
    import mvaEleID_RunIII_custom_JPsitoEE_V1_producer_config
mvaConfigsForEleProducer.append( mvaEleID_RunIII_custom_JPsitoEE_V1_producer_config )

# evaluate MVA IDs for PF electrons
# (Note:  custom IDs computed here instead of using PostRecoTools)
myelectronMVAValueMapProducer = cms.EDProducer(
    'ElectronMVAValueMapProducer',
    src = cms.InputTag('mySlimmedPFElectronsWithEmbeddedTrigger'),#,processName=cms.InputTag.skipCurrentProcess()),
    mvaConfigurations = mvaConfigsForEleProducer,
)

# change modifiedLowPtElectrons input to use embedded trigger matching
customModifiedLowPtElectrons = modifiedLowPtElectrons.clone(
                                    src = cms.InputTag("mySlimmedLPElectronsWithEmbeddedTrigger")
                                )
customUpdatedLowPtElectrons = updatedLowPtElectrons.clone(
                                src = cms.InputTag("customModifiedLowPtElectrons")
                                )

# compute electron seed gain
seedGainElePF = cms.EDProducer("ElectronSeedGainProducer", src = cms.InputTag("mySlimmedPFElectronsWithEmbeddedTrigger"))
seedGainEleLowPt = cms.EDProducer("ElectronSeedGainProducer", src = cms.InputTag("customUpdatedLowPtElectrons"))

# embed IDs and additional variables in slimmedElectrons collection
slimmedPFElectronsWithUserData = cms.EDProducer("PATElectronUserDataEmbedder",
    src = cms.InputTag("mySlimmedPFElectronsWithEmbeddedTrigger"), #includes trigger matching
    userFloats = cms.PSet(
        ElectronMVAEstimatorRun2BParkRetrainRawValues = cms.InputTag("myelectronMVAValueMapProducer:ElectronMVAEstimatorRun2BParkRetrainRawValues"),
    
    ElectronMVAEstimatorRun2RunIIICustomJPsitoEERawValues = cms.InputTag("myelectronMVAValueMapProducer:ElectronMVAEstimatorRun2RunIIICustomJPsitoEERawValues") 
    ),
    userInts = cms.PSet(
        seedGain = cms.InputTag("seedGainElePF"),
    )
)

slimmedLowPtElectronsWithUserData = cms.EDProducer("PATElectronUserDataEmbedder",
    src = cms.InputTag("customUpdatedLowPtElectrons"),
    userInts = cms.PSet(
        seedGain = cms.InputTag("seedGainEleLowPt"),
    ),
)

#Everything can be done here, in one loop and save time :)
electronsForAnalysis = cms.EDProducer(
  'ElectronMerger',
  trgLepton = cms.InputTag('electronTrgSelector:trgElectrons'),
  trgBits = cms.InputTag("TriggerResults","","HLT"),
  # lowptSrc = cms.InputTag('slimmedLowPtElectrons'), # Only used if saveLowPtE == True
  lowptSrc = cms.InputTag('slimmedLowPtElectronsWithUserData'), # Only used if saveLowPtE == True
  # pfSrc    = cms.InputTag('slimmedElectrons'),
  pfSrc    = cms.InputTag('slimmedPFElectronsWithUserData'),
  rho_PFIso = cms.InputTag("fixedGridRhoFastjetAll"),
  EAFile_PFIso = cms.FileInPath("RecoEgamma/ElectronIdentification/data/Run3_Winter22/effAreaElectrons_cone03_pfNeuHadronsAndPhotons_122X.txt"),
  # pfmvaId = cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2BParkRetrainValues"),
  # pfmvaId_Run2 = cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17NoIsoV2Values"),
  # pfmvaId_Run3 = cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2RunIIIWinter22NoIsoV1Values"),
  pfmvaId = cms.InputTag(""),
  pfmvaIdcustom = cms.InputTag(""),#use embedded values
  pfmvaId_Run2 = cms.InputTag(""), #use embedded values
  pfmvaId_Run3 = cms.InputTag(""), #use embedded values
  vertexCollection = cms.InputTag("offlineSlimmedPrimaryVertices"),
  ## cleaning wrt trigger lepton [-1 == no cut]
  ## NB: even if cuts are turned off, electron will be skipped if trigger lepton collection is empty. DISABLE filterEle TO AVOID.
  filterEle = cms.bool(False), # If True, skip electrons too close to trigger electron OR from different PV (see flags below)
  drForCleaning_wrtTrgLepton = cms.double(-1.), # do not check for dR matching to trg objs
  dzForCleaning_wrtTrgLepton = cms.double(-1.), # do not check for dZ matching to trg objs
  ## cleaning between pfEle and lowPtGsf
  drForCleaning = cms.double(0.05),
  dzForCleaning = cms.double(0.5), ##keep tighter dZ to check overlap of pfEle with lowPt (?)
  ## true = flag and clean; false = only flag
  flagAndclean = cms.bool(False),
  pf_ptMin = cms.double(1.),
  ptMin = cms.double(0.5),
  etaMax = cms.double(2.5),
  bdtMin = cms.double(-200.), # Open this up and rely on L/M/T WPs. was -2.5, this cut can be used to deactivate low pT e if set to >12
  useRegressionModeForP4 = cms.bool(False), # If True, use REGRESSED energy and eta and phi from track; else...
  useGsfModeForP4 = cms.bool(False), # If True, use TRACK energy and GSF phi/eta for both PF and LowPt eles.
  # If both are false, use regressed energy
  sortOutputCollections = cms.bool(True),
  saveLowPtE = cms.bool(True), # Use low-pT eles
  # conversions
  conversions = cms.InputTag('gsfTracksOpenConversions:gsfTracksOpenConversions'),
  beamSpot = cms.InputTag("offlineBeamSpot"),
  # module flags
  addUserVarsExtra = cms.bool(False),
  efficiencyStudy = cms.bool(False), # If True, flag electron selections instead of cutting; saves extra variables
  saveRegressionVars = cms.bool(False), # If True, save regression variables
  recHitCollectionEB = cms.InputTag("reducedEgamma:reducedEBRecHits"),
  recHitCollectionEE = cms.InputTag("reducedEgamma:reducedEERecHits"),
)

# finer trigger skim -- only select events that have >= 2 reco trigger-matched electrons
# (here considers both PF and lowPt electrons, after overlap removal)

uniqueTriggerElectrons = cms.EDFilter("PATElectronSelector",
    src = cms.InputTag("electronsForAnalysis:SelectedElectrons"),
    cut = cms.string("userInt('isPFoverlap') == 0 && userInt('isTriggering') == 1"),
)

countTrgElectrons = cms.EDFilter(
    "PATCandViewCountFilter",
    minNumber = cms.uint32(2),
    maxNumber = cms.uint32(999999),
    src = cms.InputTag("uniqueTriggerElectrons"),
)

# # Previous implementation: only checks for PF trigger-matched electrons
# countTrgElectrons = cms.EDFilter(
#     "PATCandViewCountFilter",
#     minNumber = cms.uint32(2),
#     maxNumber = cms.uint32(999999),
#     src = cms.InputTag("electronTrgSelector", "trgElectrons"),
# )

# Saving analysis electrons
electronBParkTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
 src = cms.InputTag("electronsForAnalysis:SelectedElectrons"),
 cut = cms.string(""),
    name= cms.string("Electron"),
    doc = cms.string("slimmedElectrons for BPark after basic selection"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(P4Vars,
        pdgId  = Var("pdgId", int, doc="PDG code assigned by the event reconstruction (not by MC truth)"),
        charge = Var("userFloat('chargeMode')", int, doc="electric charge from pfEle or chargeMode for lowPtGsf"),
        dz = Var("dB('PVDZ')",float,doc="dz (with sign) wrt first PV, in cm",precision=10),
        dzErr = Var("abs(edB('PVDZ'))",float,doc="dz uncertainty, in cm",precision=6),
        dxy = Var("dB('PV2D')",float,doc="dxy (with sign) wrt first PV, in cm",precision=10),
        dxyErr = Var("edB('PV2D')",float,doc="dxy uncertainty, in cm",precision=6),
        vx = Var("vx()",float,doc="x coordinate of vertex position, in cm",precision=6),
        vy = Var("vy()",float,doc="y coordinate of vertex position, in cm",precision=6),
        vz = Var("vz()",float,doc="z coordinate of vertex position, in cm",precision=6),
        dzTrg = Var("userFloat('dzTrg')",float,doc="dz from the corresponding triggered lepton, in cm",precision=10),
        ip3d = Var("abs(dB('PV3D'))",float,doc="3D impact parameter wrt first PV, in cm",precision=10),
        sip3d = Var("abs(dB('PV3D')/edB('PV3D'))",float,doc="3D impact parameter significance wrt first PV, in cm",precision=10),
        preRegEnergy = Var("superCluster().rawEnergy()",float,doc="energy before correction",precision=10),
        trackPt = Var("gsfTrack().ptMode()",float,doc="pt of the gsf track", precision=10),
        correctedEnergy = Var("correctedEcalEnergy()",float,doc="energy after correction",precision=10),
        trackRegressedEnergy = Var("ecalTrackRegressionEnergy()",float,doc="energy after regression",precision=10),

        # START MVA ID input variabiles (from RecoEgamma/ElectronIdentification/data/ElectronIDVariablesRun3.txt)
        deltaEtaSC = Var("superCluster().eta()-eta()",float,doc="delta eta (SC,ele) with sign",precision=10),
        sigmaietaieta = Var("full5x5_sigmaIetaIeta()",float,doc="sigma_IetaIeta of the supercluster, calculated with full 5x5 region",precision=10),
        sigmaiphiiphi = Var("full5x5_sigmaIphiIphi()",float,doc="sigma_IphiIphi of the supercluster, calculated with full 5x5 region",precision=10),
        circularity = Var("1.-full5x5_e1x5()/full5x5_e5x5()",float,doc="circularity of the supercluster",precision=10),
        r9 = Var("full5x5_r9()",float,doc="R9 of the supercluster, calculated with full 5x5 region",precision=10),
        scletawidth = Var("superCluster().etaWidth()",float,doc="width of the supercluster in eta",precision=10),
        sclphiwidth = Var("superCluster().phiWidth()",float,doc="width of the supercluster in phi",precision=10),
        hoe = Var("full5x5_hcalOverEcal()",float,doc="H/E of the supercluster, calculated with full 5x5 region",precision=10),
        kfhits = Var("closestCtfTrackNLayers()",int,doc="number of missing hits in the inner tracker"),
        kfchi2 = Var("closestCtfTrackNormChi2()",float,doc="normalized chi2 of the closest CTF track"),
        gsfchi2 = Var("gsfTrack().normalizedChi2()",int,doc="number of missing hits in the inner tracker"),
        fBrem = Var("fbrem()",float,doc="brem fraction from the gsf fit",precision=12),
        gsfhits = Var("gsfTrack().hitPattern().trackerLayersWithMeasurement()",int,doc="number of missing hits in the inner tracker"),
        expected_inner_hits = Var("gsfTrack().hitPattern().numberOfLostHits('MISSING_INNER_HITS')",int,doc="number of missing hits in the inner tracker"),
        conversionVertexFitProbability = Var("convVtxFitProb()",float,doc="conversion vertex fit probability"),
        eoverp = Var("eSuperClusterOverP()",float,doc="E/P of the electron",precision=10),
        eeleoverpout = Var("eEleClusterOverPout()",float,doc="E/E_{SC} of the electron",precision=10),
        IoEmIop = Var("1.0/ecalEnergy()-1.0/trackMomentumAtVtx().R()",float,doc="1/E - 1/P of the electron",precision=10),
        deltaetain = Var("abs(deltaEtaSuperClusterTrackAtVtx())",float,doc="delta eta (SC,track) with sign",precision=10),
        deltaphiin = Var("abs(deltaPhiSuperClusterTrackAtVtx())",float,doc="delta phi (SC,track) with sign",precision=10),
        deltaetaseed = Var("abs(deltaEtaSeedClusterTrackAtCalo())",float,doc="delta eta (seed,track) with sign",precision=10),
        psOverEraw = Var("superCluster().preshowerEnergy()/superCluster().rawEnergy()",float,doc="preshower energy over raw ECAL energy",precision=10),

        pfIso03_chg = Var("pfIsolationVariables().sumChargedHadronPt()",float,doc="PF absolute isolation dR=0.3, charged component",precision=10),
        pfIso03_chg_corr = Var("userFloat('PFIsoChg03_corr')",float,doc="corrected PF absolute isolation dR=0.3, charged component",precision=10),
        pfIso03_neu = Var("pfIsolationVariables().sumNeutralHadronEt()",float,doc="PF absolute isolation dR=0.3, neutral component",precision=10),
        pfIso03_all = Var("userFloat('PFIsoAll03')",float,doc="PF absolute isolation dR=0.3, total (with rho*EA PU Winter22V1 corrections)"),
        pfIso03_all_corr = Var("userFloat('PFIsoAll03_corr')",float,doc="corrected PF absolute isolation dR=0.3, total (with rho*EA PU Winter22V1 corrections)"),
        pfIso04_chg = Var("chargedHadronIso()",float,doc="PF absolute isolation dR=0.4, charged component"),
        pfIso04_chg_corr = Var("userFloat('PFIsoChg04_corr')",float,doc="corrected PF absolute isolation dR=0.4, charged component",precision=10),
        pfIso04_neu = Var("neutralHadronIso()",float,doc="PF absolute isolation dR=0.4, neutral component"),
        pfIso04_all = Var("userFloat('PFIsoAll04')",float,doc="PF absolute isolation dR=0.4, total (with rho*EA PU Winter22V1 corrections)"),
        pfIso04_all_corr = Var("userFloat('PFIsoAll04_corr')",float,doc="corrected PF absolute isolation dR=0.4, total (with rho*EA PU Winter22V1 corrections)"),
        ctfTrackPt = Var("?closestCtfTrackRef().isNonnull()?closestCtfTrackRef().pt():0",float,doc=""),
        ctfTrackEta = Var("?closestCtfTrackRef().isNonnull()?closestCtfTrackRef().eta():0",float,doc=""),
        ctfTrackPhi = Var("?closestCtfTrackRef().isNonnull()?closestCtfTrackRef().phi():0",float,doc=""),

        ecalPFclusterIso = Var("ecalPFClusterIso()",float,doc="sum of PF clusters in isolation cone",precision=10),
        hcalPFclusterIso = Var("hcalPFClusterIso()",float,doc="sum of PF clusters in isolation cone",precision=10),
        dr03TkSumPt = Var("dr03TkSumPt()",float,doc="sum of tracks in isolation cone",precision=10),
        # END MVA input variables

        # START Scale and smearing inputs
        seedGain = Var("userInt('seedGain')", int, doc="Gain of the seed crystal"),
        # END Scale and smearing inputs

        tightCharge = Var("isGsfCtfScPixChargeConsistent() + isGsfScPixChargeConsistent()",int,doc="Tight charge criteria (0:none, 1:isGsfScPixChargeConsistent, 2:isGsfCtfScPixChargeConsistent)"),
        convVeto = Var("passConversionVeto()",bool,doc="pass conversion veto"),
        # lostHits = Var("gsfTrack.hitPattern.numberOfLostHits('MISSING_INNER_HITS')","uint8",doc="number of missing inner hits"),
        trkRelIso = Var("trackIso/pt",float,doc="PF relative isolation dR=0.3, total (deltaBeta corrections)"),
        isPF = Var("userInt('isPF')",bool,doc="electron is PF candidate"),
        isLowPt = Var("userInt('isLowPt')",bool,doc="electron is LowPt candidate"),
        LPEleSeed_Fall17PtBiasedV1Value = Var("userFloat('LPEleSeed_Fall17PtBiasedV1Value')",float,doc="Seed BDT for low-pT electrons, Fall17 ptBiased model"), #@@ was called "ptBiased"
        LPEleSeed_Fall17UnBiasedV1Value = Var("userFloat('LPEleSeed_Fall17UnBiasedV1Value')",float,doc="Seed BDT for low-pT electrons, Fall17 unBiased model"), #@@ was called "unBiased"
        LPEleMvaID_2020Sept15Value = Var("userFloat('LPEleMvaID_2020Sept15Value')",float,doc="MVA ID for low-pT electrons, 2020Sept15 model"), #@@ was called "mvaId"
        PFEleMvaID_RetrainedValue = Var("userFloat('PFEleMvaID_RetrainedValue')",float,doc="MVA ID for PF electrons, BParkRetrainValues"), #@@ was called "pfmvaId"
        PFEleMvaID_Run3CustomJpsitoEEValue = Var("userFloat('PFEleMvaID_Run3CustomJpsitoEEValue')",float,doc="Custom MVA ID for PF electrons, RunIIICustomJPsitoEERawValues"),                 

        PFEleMvaID_Fall17NoIsoV2Value   = Var("userFloat('PFEleMvaID_Fall17NoIsoV2Value')",float,doc="MVA ID for PF electrons, mvaEleID-Fall17-noIso-V2"),
        PFEleMvaID_Fall17NoIsoV2wpLoose = Var("userInt('PFEleMvaID_Fall17NoIsoV2wpLoose')",bool,doc="MVA ID for PF electrons, mvaEleID-Fall17-noIso-V2-wpLoose"),
        PFEleMvaID_Fall17NoIsoV2wp90    = Var("userInt('PFEleMvaID_Fall17NoIsoV2wp90')",bool,doc="MVA ID for PF electrons, mvaEleID-Fall17-noIso-V2-wp90"),
        PFEleMvaID_Fall17NoIsoV2wp80    = Var("userInt('PFEleMvaID_Fall17NoIsoV2wp80')",bool,doc="MVA ID for PF electrons, mvaEleID-Fall17-noIso-V2-wp80"),

        PFEleMvaID_Fall17IsoV2Value     = Var("userFloat('PFEleMvaID_Fall17IsoV2Value')",float,doc="MVA ID for PF electrons, mvaEleID-Fall17-iso-V2"),
        PFEleMvaID_Fall17IsoV2wpLoose   = Var("userInt('PFEleMvaID_Fall17IsoV2wpLoose')",bool,doc="MVA ID for PF electrons, mvaEleID-Fall17-iso-V2-wpLoose"),
        PFEleMvaID_Fall17IsoV2wp90      = Var("userInt('PFEleMvaID_Fall17IsoV2wp90')",bool,doc="MVA ID for PF electrons, mvaEleID-Fall17-iso-V2-wp90"),
        PFEleMvaID_Fall17IsoV2wp80      = Var("userInt('PFEleMvaID_Fall17IsoV2wp80')",bool,doc="MVA ID for PF electrons, mvaEleID-Fall17-iso-V2-wp80"),

        PFEleCutID_Fall17V2wpLoose      = Var("userInt('PFEleCutID_Fall17V2wpLoose')",bool,doc="Cut ID for PF electrons, Fall17V2wpLoose"),
        PFEleCutID_Fall17V2wpMedium     = Var("userInt('PFEleCutID_Fall17V2wpMedium')",bool,doc="Cut ID for PF electrons, Fall17V2wpMedium"),
        PFEleCutID_Fall17V2wpTight      = Var("userInt('PFEleCutID_Fall17V2wpTight')",bool,doc="Cut ID for PF electrons, Fall17V2wpTight"),

        PFEleMvaID_Winter22NoIsoV1Value = Var("userFloat('PFEleMvaID_Winter22NoIsoV1Value')",float,doc="MVA ID for PF electrons: RunIIIWinter22NoIsoV1Values"),
        PFEleMvaID_Winter22NoIsoV1wp90  = Var("userInt('PFEleMvaID_Winter22NoIsoV1wp90')",bool,doc="MVA ID for PF electrons, mvaEleID-RunIIIWinter22-noIso-V1-wp90"),
        PFEleMvaID_Winter22NoIsoV1wp80  = Var("userInt('PFEleMvaID_Winter22NoIsoV1wp80')",bool,doc="MVA ID for PF electrons, mvaEleID-RunIIIWinter22-noIso-V1-wp80"),

        PFEleMvaID_Winter22IsoV1Value = Var("userFloat('PFEleMvaID_Winter22IsoV1Value')",float,doc="MVA ID for PF electrons: RunIIIWinter22IsoV1Values",),
        PFEleMvaID_Winter22IsoV1wp90  = Var("userInt('PFEleMvaID_Winter22IsoV1wp90')",bool,doc="MVA ID for PF electrons, mvaEleID-RunIIIWinter22-iso-V1-wp90"),
        PFEleMvaID_Winter22IsoV1wp80  = Var("userInt('PFEleMvaID_Winter22IsoV1wp80')",bool,doc="MVA ID for PF electrons, mvaEleID-RunIIIWinter22-iso-V1-wp80"),

        PFEleCutID_Winter22V1wpLoose  = Var("userInt('PFEleCutID_Winter22V1wpLoose')",bool,doc="Cut ID for PF electrons, Winter22V1wpLoose"),
        PFEleCutID_Winter22V1wpMedium = Var("userInt('PFEleCutID_Winter22V1wpMedium')",bool,doc="Cut ID for PF electrons, Winter22V1wpMedium"),
        PFEleCutID_Winter22V1wpTight  = Var("userInt('PFEleCutID_Winter22V1wpTight')",bool,doc="Cut ID for PF electrons, Winter22V1wpTight"),

        isTriggering = Var("userInt('isTriggering')",int,doc="Is ele trigger-matched?"),
        drTrg = Var("userFloat('drTrg')",float,doc="dR to the triggering lepton"),
        dPtOverPtTrg = Var("userFloat('dPtOverPtTrg')",float,doc="dPt/Pt to the triggering lepton"),

        isPFoverlap = Var("userInt('isPFoverlap')",bool,doc="flag lowPt ele overlapping with pf in selected_pf_collection", precision=8),
        convOpen = Var("userInt('convOpen')",bool,doc="Matched to a conversion in gsfTracksOpenConversions collection"),
        convLoose = Var("userInt('convLoose')",bool,doc="Matched to a conversion satisfying Loose WP (see code)"),
        convTight = Var("userInt('convTight')",bool,doc="Matched to a conversion satisfying Tight WP (see code)"),
        convLead = Var("userInt('convLead')",bool,doc="Matched to leading track from conversion"),
        convTrail = Var("userInt('convTrail')",bool,doc="Matched to trailing track from conversion"),
        convExtra = Var("userInt('convExtra')",bool,doc="Flag to indicate if all conversion variables are stored"),
        skipEle = Var("userInt('skipEle')",bool,doc="Is ele skipped (due to small dR or large dZ w.r.t. trigger)?"),
        )
)

if electronsForAnalysis.addUserVarsExtra :
    electronBParkTable.variables = cms.PSet(
        electronBParkTable.variables,
        convValid = Var("userInt('convValid')",bool,doc="Valid conversion"),
        convChi2Prob = Var("userFloat('convChi2Prob')",float,doc="Reduced chi2 for conversion vertex fit"),
        convQualityHighPurity = Var("userInt('convQualityHighPurity')",bool,doc="'High purity' quality flag for conversion"),
        convQualityHighEff = Var("userInt('convQualityHighEff')",bool,doc="'High efficiency' quality flag for conversion"),
        convTracksN = Var("userInt('convTracksN')",int,doc="Number of tracks associated with conversion"),
        convMinTrkPt = Var("userFloat('convMinTrkPt')",float,doc="Minimum pT found for tracks associated with conversion"),
        convLeadIdx = Var("userInt('convLeadIdx')",int,doc="Index of leading track"),
        convTrailIdx = Var("userInt('convTrailIdx')",int,doc="Index of trailing track"),
        convLxy = Var("userFloat('convLxy')",float,doc="Transverse position of conversion vertex"),
        convVtxRadius = Var("userFloat('convVtxRadius')",float,doc="Radius of conversion vertex"),
        convMass = Var("userFloat('convMass')",float,doc="Invariant mass from conversion pair"),
        convMassFromPin = Var("userFloat('convMassFromPin')",float,doc="Invariant mass from inner momeuntum of conversion pair"),
        convMassBeforeFit = Var("userFloat('convMassBeforeFit')",float,doc="Invariant mass from conversion pair before fit"),
        convMassAfterFit = Var("userFloat('convMassAfterFit')",float,doc="Invariant mass from conversion pair after fit"),
        convLeadNHitsBeforeVtx = Var("userInt('convLeadNHitsBeforeVtx')",int,doc="Number of hits before vertex for lead track"),
        convTrailNHitsBeforeVtx = Var("userInt('convTrailNHitsBeforeVtx')",int,doc="Number of hits before vertex for trail track"),
        convMaxNHitsBeforeVtx = Var("userInt('convMaxNHitsBeforeVtx')",int,doc="Maximum number of hits per track before vertex"),
        convSumNHitsBeforeVtx = Var("userInt('convSumNHitsBeforeVtx')",int,doc="Summed number of hits over tracks before vertex"),
        convDeltaExpectedNHitsInner = Var("userInt('convDeltaExpectedNHitsInner')",int,doc="Delta number of expected hits before vertex"),
        convDeltaCotFromPin = Var("userFloat('convDeltaCotFromPin')",float,doc="Delta cotangent theta from inner momenta"),
    )

electronsBParkMCMatchForTable = cms.EDProducer("MCMatcher",  # cut on deltaR, deltaPt/Pt; pick best by deltaR
    src         = electronBParkTable.src,                 # final reco collection
    matched     = cms.InputTag("finalGenParticlesBPark"), # final mc-truth particle collection
    mcPdgId     = cms.vint32(11),                 # one or more PDG ID (11 = el, 22 = pho); absolute values (see below)
    checkCharge = cms.bool(False),              # True = require RECO and MC objects to have the same charge
    mcStatus    = cms.vint32(1),                # PYTHIA status code (1 = stable, 2 = shower, 3 = hard scattering)
    maxDeltaR   = cms.double(0.03),             # Maximum deltaR for the match
    maxDPtRel   = cms.double(0.5),              # Maximum deltaPt/Pt for the match
    # maxDeltaR   = cms.double(0.05),             # Maximum deltaR for the match
    # maxDPtRel   = cms.double(0.5),              # Maximum deltaPt/Pt for the match
    # TODO: check changes
    resolveAmbiguities    = cms.bool(True),    # Forbid two RECO objects to match to the same GEN object
    # NB: resolveAmbiguities = False before. Why?
    resolveByMatchQuality = cms.bool(True),     # False = just match input in order; True = pick lowest deltaR pair first
)

selectedElectronsMCMatchEmbedded = cms.EDProducer(
    'ElectronMatchEmbedder',
    src = electronBParkTable.src,
    matching = cms.InputTag('electronsBParkMCMatchForTable')
)

electronBParkMCTable = cms.EDProducer("CandMCMatchTableProducerBPark",
    src     = electronBParkTable.src,
    mcMap   = cms.InputTag("electronsBParkMCMatchForTable"),
    objName = electronBParkTable.name,
    objType = electronBParkTable.name,
    branchName = cms.string("genPart"),
    docString = cms.string("MC matching to status==1 electrons or photons"),
)

electronsBParkSequence = cms.Sequence(
    customModifiedLowPtElectrons +
    customUpdatedLowPtElectrons +
    myelectronMVAValueMapProducer +
    seedGainElePF +
    seedGainEleLowPt +
    slimmedPFElectronsWithUserData +
    slimmedLowPtElectronsWithUserData +
    electronsForAnalysis
)

electronBParkMC = cms.Sequence(
    electronsBParkSequence +
    electronsBParkMCMatchForTable +
    selectedElectronsMCMatchEmbedded +
    electronBParkMCTable
)

# defining separate sequence to be correctly inserted at the end of nanoDiEleSequence
# (electronBParkMC must go BEFORE because of dependencies)
electronBParkTriggerSelection = cms.Sequence(
    uniqueTriggerElectrons +
    countTrgElectrons
)

electronBParkTables = cms.Sequence(electronBParkTable)

###########
# Modifiers
###########

from PhysicsTools.BParkingNano.modifiers_cff import *

# DiEle.toModify(electronsForAnalysis, ...)

# Trigger matching study
vbfSkimming2023.toModify(countTrgElectrons, minNumber = cms.uint32(0))
vbfSkimming2024.toModify(countTrgElectrons, minNumber = cms.uint32(0))
triggerMatchingStudy.toModify(countTrgElectrons, minNumber = cms.uint32(0))


# Selection efficiency study (-> disable all cuts, store them as flags)
efficiencyStudy.toModify(electronsForAnalysis, efficiencyStudy = cms.bool(True))

efficiencyStudy.toModify(electronBParkTable,
        variables = cms.PSet(
            electronBParkTable.variables,
            selection_ptCut = Var("userInt('selection_pTcut')",bool,doc="Passes pT cut"),
            selection_etaCut = Var("userInt('selection_etaCut')",bool,doc="Passes eta cut"),
            # convVeto var already saved
        )
)
efficiencyStudy.toModify(countTrgElectrons, minNumber = cms.uint32(0))

# Regression study (-> save extra variables needed for regression training and application)
regressionVars.toModify(electronsForAnalysis, saveRegressionVars = cms.bool(True))

regressionVars.toModify(electronBParkTable, 
    variables = cms.PSet(
        electronBParkTable.variables,
        # regression variables
        SCeta = Var("superCluster().eta()",float,doc="eta of the supercluster",precision=10),
        SCphi = Var("superCluster().phi()",float,doc="phi of the supercluster",precision=10),
        SCrawESenergy = Var("superCluster().preshowerEnergy()",float,doc="raw preshower energy of the supercluster",precision=10),
        SCclustersSize = Var("superCluster().clustersSize()",int,doc="number of clusters in the supercluster"),
        hadronicOverEm = Var("hadronicOverEm()",float,doc="H/E of the supercluster (rechits within cone)",precision=10),
        hadronicOverEmBc = Var("hcalOverEcalBc()",float,doc="H/E of the supercluster (rechits behind clusters)",precision=10),
        seedEta = Var("seed().eta()",float,doc="eta of the supercluster seed",precision=10),
        seedPhi = Var("seed().phi()",float,doc="phi of the supercluster seed",precision=10),
        seedEnergy = Var("seed().energy()",float,doc="energy of the supercluster seed",precision=10),
        e3x3 = Var("userFloat('e3x3')",float,doc="e3x3 of the supercluster, calculated with full 5x5 region",precision=10),
        e5x5 = Var("full5x5_e5x5()",float,doc="e5x5 of the supercluster, calculated with full 5x5 region",precision=10),
        sigmaietaiphi = Var("full5x5_showerShape().sigmaIetaIphi",float,doc="sigma_IetaIphi of the supercluster, calculated with full 5x5 region",precision=10),
        eMax = Var("full5x5_showerShape().eMax",float,doc="eMax of the supercluster, calculated with full 5x5 region",precision=10),
        e2nd = Var("full5x5_showerShape().e2nd",float,doc="e2nd of the supercluster, calculated with full 5x5 region",precision=10),
        eLeft = Var("full5x5_showerShape().eLeft",float,doc="eLeft of the supercluster, calculated with full 5x5 region",precision=10),
        eRight = Var("full5x5_showerShape().eRight",float,doc="eRight of the supercluster, calculated with full 5x5 region",precision=10),
        eTop = Var("full5x5_showerShape().eTop",float,doc="eTop of the supercluster, calculated with full 5x5 region",precision=10),
        eBottom = Var("full5x5_showerShape().eBottom",float,doc="eBottom of the supercluster, calculated with full 5x5 region",precision=10),
        e2x5Max = Var("full5x5_showerShape().e2x5Max",float,doc="e2x5Max of the supercluster, calculated with full 5x5 region",precision=10),
        e2x5Top = Var("full5x5_showerShape().e2x5Top",float,doc="e2x5Top of the supercluster, calculated with full 5x5 region",precision=10),
        e2x5Bottom = Var("full5x5_showerShape().e2x5Bottom",float,doc="e2x5Bottom of the supercluster, calculated with full 5x5 region",precision=10),
        e2x5Left = Var("full5x5_showerShape().e2x5Left",float,doc="e2x5Left of the supercluster, calculated with full 5x5 region",precision=10),
        e2x5Right = Var("full5x5_showerShape().e2x5Right",float,doc="e2x5Right of the supercluster, calculated with full 5x5 region",precision=10),

        trkEtaMode = Var("gsfTrack().etaMode()",float,doc="eta of the gsf track", precision=10),
        trkPhiMode = Var("gsfTrack().phiMode()",float,doc="phi of the gsf track", precision=10),
        trkPmode = Var("gsfTrack().pMode()",float,doc="p of the gsf track", precision=10),
        trkPVtx = Var("trackMomentumAtVtx().Mag2()",float,doc="momentum of the track at the vertex", precision=10),
        trkPOut = Var("trackMomentumOut().Mag2()",float,doc="momentum of the track at the outermost point", precision=10),

        nrSatCrys = Var("nSaturatedXtals()",int,doc="Number of saturated crystals in the supercluster"),

        ecalEnergy = Var("ecalEnergy()",float,doc="ECAL energy of the electron",precision=10),
        ecalEnergyErr = Var("ecalEnergyError()",float,doc="ECAL energy uncertainty of the electron",precision=10),

        dEtaSeedSC = Var("seed().eta() - superCluster().eta() ",float,doc="delta eta (seed,track) with sign",precision=10),
        dPhiSeedSC = Var("seed().phi() - superCluster().phi() ",float,doc="delta phi (seed,track) with sign",precision=10),

        iEtaOrX = Var("userInt('iEtaOrX')",int,doc="ieta of the supercluster seed"),
        iPhiOrY = Var("userInt('iPhiOrY')",int,doc="iphi of the supercluster seed"),
        iEtaMod5 = Var("userInt('iEtaMod5')",int,doc="ieta of the supercluster seed mod 5"),
        iPhiMod2 = Var("userInt('iPhiMod2')",int,doc="iphi of the supercluster seed mod 2"),
        iEtaMod20 = Var("userInt('iEtaMod20')",int,doc="ieta of the supercluster seed mod 20"),
        iPhiMod20 = Var("userInt('iPhiMod20')",int,doc="iphi of the supercluster seed mod 20"),

        etaCrySeed = Var("userInt('etaCrySeed')", int, doc="eta of seed in crystal indices"),
        phiCrySeed = Var("userInt('phiCrySeed')", int, doc="phi of seed in crystal indices"),

        eSubClusters = Var("userFloat('eSubClusters')",int,doc="number of subclusters in the supercluster"),
        subClusterEnergy1 = Var("userFloat('subClusterEnergy1')",float,doc="energy of the first subcluster (excluding seed)",precision=10),
        subClusterEta1 = Var("userFloat('subClusterEta1')",float,doc="eta of the first subcluster (excluding seed)",precision=10),
        subClusterPhi1 = Var("userFloat('subClusterPhi1')",float,doc="phi of the first subcluster (excluding seed)",precision=10),
        subClusterEmax1 = Var("userFloat('subClusterEmax1')",float,doc="Emax of the first subcluster (excluding seed)",precision=10),
        subClusterE3x3_1 = Var("userFloat('subClusterE3x31')",float,doc="E3x3 of the first subcluster (excluding seed)",precision=10),
        subClusterEnergy2 = Var("userFloat('subClusterEnergy2')",float,doc="energy of the second subcluster (excluding seed)",precision=10),
        subClusterEta2 = Var("userFloat('subClusterEta2')",float,doc="eta of the second subcluster (excluding seed)",precision=10),
        subClusterPhi2 = Var("userFloat('subClusterPhi2')",float,doc="phi of the second subcluster (excluding seed)",precision=10),
        subClusterEmax2 = Var("userFloat('subClusterEmax2')",float,doc="Emax of the second subcluster (excluding seed)",precision=10),
        subClusterE3x3_2 = Var("userFloat('subClusterE3x32')",float,doc="E3x3 of the second subcluster (excluding seed)",precision=10),
        subClusterEnergy3 = Var("userFloat('subClusterEnergy3')",float,doc="energy of the third subcluster (excluding seed)",precision=10),
        subClusterEta3 = Var("userFloat('subClusterEta3')",float,doc="eta of the third subcluster (excluding seed)",precision=10),
        subClusterPhi3 = Var("userFloat('subClusterPhi3')",float,doc="phi of the third subcluster (excluding seed)",precision=10),
        subClusterEmax3 = Var("userFloat('subClusterEmax3')",float,doc="Emax of the third subcluster (excluding seed)",precision=10),
        subClusterE3x3_3 = Var("userFloat('subClusterE3x33')",float,doc="E3x3 of the third subcluster (excluding seed)",precision=10),

        clusterMaxDR = Var("userFloat('clusterMaxDR')", float, doc = "maximum dR of subclusters wrt seed"),
        clusterMaxDRDPhi = Var("userFloat('clusterMaxDRDPhi')", float, doc = "dphi of subcluster with maximum dR wrt seed"),
        clusterMaxDRDEta = Var("userFloat('clusterMaxDRDEta')", float, doc = "deta of subcluster with maximum dR wrt seed"),
        clusterMaxDRRawEnergy = Var("userFloat('clusterMaxDRRawEnergy')", float, doc = "raw energy of subcluster with maximum dR wrt seed"),

        nPreshowerClusters = Var("userInt('nPreshowerClusters')",int,doc="number of preshower clusters in the supercluster"),
        eESClusters = Var("userFloat('eESClusters')",float,doc="energy of the first preshower cluster",precision=10),
        esClusterEnergy0 = Var("userFloat('esClusterEnergy0')",float,doc="energy of the first preshower cluster",precision=10),
        esClusterEta0 = Var("userFloat('esClusterEta0')",float,doc="eta of the first preshower cluster",precision=10),
        esClusterPhi0 = Var("userFloat('esClusterPhi0')",float,doc="phi of the first preshower cluster",precision=10),
        esClusterEnergy1 = Var("userFloat('esClusterEnergy1')",float,doc="energy of the second preshower cluster",precision=10),
        esClusterEta1 = Var("userFloat('esClusterEta1')",float,doc="eta of the second preshower cluster",precision=10),
        esClusterPhi1 = Var("userFloat('esClusterPhi1')",float,doc="phi of the second preshower cluster",precision=10),
        esClusterEnergy2 = Var("userFloat('esClusterEnergy2')",float,doc="energy of the third preshower cluster",precision=10),
        esClusterEta2 = Var("userFloat('esClusterEta2')",float,doc="eta of the third preshower cluster",precision=10),
        esClusterPhi2 = Var("userFloat('esClusterPhi2')",float,doc="phi of the third preshower cluster",precision=10),        

        isEB = Var("isEB()",bool,doc="is EB?"),
    )
)