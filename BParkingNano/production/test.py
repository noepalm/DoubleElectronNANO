from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

options = VarParsing('python')

options.register('year', 2023,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Year to process between 2022 or 2023 (default)")

options.register('isMC', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on real data"
)

options.register('isSignal', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on signal MC (else J/psi)")

options.register("isMinBias", False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on inclusive dilepton MinBias MC")

options.register("isPromptJpsi", False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on prompt J/psi MC (else J/psi)")

options.register("isPromptUpsilon", False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on prompt Upsilon MC (else J/psi)")

options.register('globalTag', 'NOTSET',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Set global tag"
)
options.register('wantSummary', True,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Request summary"
)
options.register('wantFullRECO', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Save full RECO event"
)
options.register('saveAllNanoContent', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Store the standard NanoAOD collections"
)
options.register('reportEvery', 10,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Report every N events"
)
options.register('skip', 0,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Skip first N events"
)

options.register('lhcRun', 3,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "LHC Run 2 or 3 (default)"
)

options.register('mode', "reco",
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Run standard reco ('reco'), efficiency study ('eff'), or trigger matching study ('trg')"
)

options.setDefault('maxEvents', 1000)
options.setDefault('tag', '130X')
options.parseArguments()

#!TEST
options.isMC = 0
options.reportEvery = 1000
options.tag = '2025Jun10'
options.globalTag = '140X_dataRun3_v20'
options.lhcRun = 3
options.year = 2024
options.mode = 'vbf'
options.saveAllNanoContent = 1
options.inputFiles = ["file:/afs/cern.ch/work/p/pviscone/CMSSW/CMSSW_14_0_18/src/test.root"]

print(options)

globaltag = None

if options.year == 2022:
    globaltag = '124X_mcRun3_2022_realistic_postEE_v3' if options.isMC else '124X_dataRun3_PromptAnalysis_v1'
    # NB for DATA: use 124X_dataRun3_PromptAnalysis_v1 for PromptReco, 124X_dataRun3_v15 for ReReco
elif options.year == 2023:
    globaltag = "130X_mcRun3_2023_realistic_postBPix_v2" if options.isMC else "130X_dataRun3_PromptAnalysis_v1"
    if options.isPromptJpsi:
        globaltag = "130X_mcRun3_2023_realistic_v14"
elif options.year == 2024:
    pass
else:
    raise ValueError("Year must be 2022 or 2023")

globaltag = options.globalTag

print("Using global tag ", globaltag)

ext1 = {False:'data', True:'mc'}
ext2 = {3 : 'Run3', 2 : 'Run2'}
ext3 = {"eff" : "noskim", "reco" : "", "trg" : ""}
ext4 = {True: 'allNano', False: ''}

output_flags = ["DoubleElectronNANO", ext2[options.lhcRun], str(options.year), ext1[options.isMC]]
if options.mode == "eff":
    output_flags.append(ext3[options.mode])
if options.saveAllNanoContent:
    output_flags.append(ext4[options.saveAllNanoContent])
output_flags.append(options.tag)

outputFileNANO = cms.untracked.string('_'.join(output_flags)+'.root')

outputFileFEVT = cms.untracked.string('_'.join(['BParkingFullEvt',
                                                str(options.year),
                                                ext1[options.isMC],
                                                options.tag])+'.root')
if not options.inputFiles:
    if options.year == 2022:
        options.inputFiles = [
            # # original
            # 'root://cms-xrd-global.cern.ch//store/user/jodedra/BuTOjpsiKEE20221103FIFTYMminiaod/BuTOjpsiKEE20221103FIFTYM/SUMMER22_MINIAOD/221106_001759/0000/step1_inMINIAODSIM_1.root', #4481 events

            # DARK PHOTON SAMPLES
            'root://cmsxrootd.fnal.gov///store/user/marlow/EtaToGammaTM_TMToEE_2022/EtaToGammaTM_TMToEE_2022_MINIAOD_388.root', #1000 events
            'root://cmsxrootd.fnal.gov///store/user/marlow/EtaToGammaTM_TMToEE_2022/EtaToGammaTM_TMToEE_2022_MINIAOD_828.root',
            'root://cmsxrootd.fnal.gov///store/user/marlow/EtaToGammaTM_TMToEE_2022/EtaToGammaTM_TMToEE_2022_MINIAOD_60.root',
            'root://cmsxrootd.fnal.gov///store/user/marlow/EtaToGammaTM_TMToEE_2022/EtaToGammaTM_TMToEE_2022_MINIAOD_19.root',
        ] if options.isMC and options.isSignal else [
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/3b3036b2-c738-4b32-b2f2-b3ba86ad0026.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/06120290-a3a0-44ea-bd8e-d45d9b8a4306.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/98cb2d23-4e66-4afa-baac-ea186cee8c0a.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/50097c68-e4cf-4bea-a2c9-3b0b741dc1de.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/c44ad042-7fbb-48e1-be51-c9370b962ecb.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/7cce6998-4154-4f35-be76-91ffa863a57b.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/ae736234-0f08-416d-8d5c-60664ab29440.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/25696625-f81d-45b3-a6d0-42d5efc09be6.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/38fcb833-c4b1-4c31-9044-3867054bdd62.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22MiniAODv4/InclusiveDileptonMinBias_TuneCP5Plus_13p6TeV_pythia8/MINIAODSIM/validDigi_130X_mcRun3_2022_realistic_v5-v4/2540000/95b2a773-125c-4b1e-8f3f-188a25a96bee.root',
        ] if options.isMC and options.isMinBias else [
            # central BuToKJpsi_JPsiToEE (should be similar), mini v1 bc of CMSSW compatibility reasons
            # 'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv3/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/124X_mcRun3_2022_realistic_postEE_v1-v2/2550000/0cc74dad-0a95-430d-82f1-113feb060680.root',
            # 'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv3/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/124X_mcRun3_2022_realistic_postEE_v1-v2/2550000/79ca5368-3191-42f6-877d-28760fbae9d8.root',
            # 'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv3/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/124X_mcRun3_2022_realistic_postEE_v1-v2/2550000/904980f9-5a94-493d-8e6c-3673b289ca30.root',
            # 'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv3/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/124X_mcRun3_2022_realistic_postEE_v1-v2/2550000/adc7d31b-a38b-41a1-8df9-e71e0a7e1d40.root',
            # 'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv3/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/124X_mcRun3_2022_realistic_postEE_v1-v2/2550000/04603ab0-8eff-4d59-bccb-bb3e9c64e4a5.root',
            # 'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv3/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/124X_mcRun3_2022_realistic_postEE_v1-v2/2550000/358618a8-9aad-4283-8249-e1fb48354c73.root',
            # 'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv3/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/124X_mcRun3_2022_realistic_postEE_v1-v2/2550000/9eafc8d8-d627-486d-a137-9931cd54f7f8.root',

            # central BuToKJpsi_JPsiToEE (should be similar), mini v4 2022
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/aeb83042-4174-49e8-8d7e-3f4acfff0a13.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/f6f9d6d6-ecff-47a6-9d9c-f0be003d99b8.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/0c772889-596b-4358-aeef-8cef53dfe216.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/1223aeb1-1145-4a07-93ae-8ce5d5dd77dd.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/4419ecf7-7341-4ad6-93f4-b81836d720bc.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/51c6d170-57f6-43d7-b02e-90a7e4588c40.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/96034a2c-5973-4f12-bedc-9321b5d98922.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/3ec09a45-2061-4a0a-8487-55c54b5bbdb0.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/ed7056bc-537a-47ed-a742-4055fef38e94.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/8dfdf330-83f9-475a-b057-c405baf43d3d.root',
            'root://cmsxrootd.fnal.gov///store/mc/Run3Summer22EEMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_postEE_v6-v2/60000/6db4a541-5fc9-4dbc-a799-d69a1be12d1f.root',
        ] if options.isMC else [
            # # 2022C - split 0
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass0/MINIAOD/PromptReco-v1/000/356/170/00000/45c0f2ed-eb5b-4292-abc8-3117424d9432.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass0/MINIAOD/PromptReco-v1/000/356/371/00000/b160219b-02dd-4858-a408-a3b1828ea504.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass0/MINIAOD/PromptReco-v1/000/356/375/00000/0487e761-50b3-4816-9b50-214915af2a6d.root',
            # # 2022C - split 1
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass1/MINIAOD/PromptReco-v1/000/356/170/00000/07cf47be-67de-4b52-8956-261221ac18a9.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass1/MINIAOD/PromptReco-v1/000/356/323/00000/4667ef56-54e3-4152-a6da-1100c492cd74.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass1/MINIAOD/PromptReco-v1/000/356/321/00000/18c138a4-8ddc-4d82-a033-fd610386063c.root',
            # # 2022C - split 2
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass2/MINIAOD/PromptReco-v1/000/356/170/00000/57130a2d-1e3e-4013-9236-e38cdfd81181.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass2/MINIAOD/PromptReco-v1/000/356/321/00000/da302835-c83d-4017-aa97-95f033ed118f.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass2/MINIAOD/PromptReco-v1/000/356/323/00000/3072ba5a-b5a6-45ed-b90c-9e489f75be80.root',
            # # 2022C - split 3
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass3/MINIAOD/PromptReco-v1/000/356/170/00000/2f693ac8-1454-4889-954c-9a77e07c82a8.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass3/MINIAOD/PromptReco-v1/000/356/371/00000/f474031f-6531-4ff6-b96f-c7d1961a7333.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass3/MINIAOD/PromptReco-v1/000/356/375/00000/d17eb325-c272-4823-b410-c132613d1602.root',
            # # 2022C - split 4
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass4/MINIAOD/PromptReco-v1/000/356/170/00000/8e4588b3-e391-4e2b-8507-a72dad99a244.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass4/MINIAOD/PromptReco-v1/000/356/316/00000/56545734-9a23-40dd-87d8-64534cddfdd8.root',
            # 'root://xrootds-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass4/MINIAOD/PromptReco-v1/000/356/321/00000/1000916f-8fd0-4e11-9550-43232984cae2.root',
            # # 2022C - split 5
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass5/MINIAOD/PromptReco-v1/000/356/170/00000/e247937b-47c5-4088-b39d-e0e631882072.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass5/MINIAOD/PromptReco-v1/000/356/309/00000/b84ab1ae-f20b-4ed9-89a2-301212d7adf5.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022C/ParkingDoubleElectronLowMass5/MINIAOD/PromptReco-v1/000/356/309/00000/cc1a5ecb-683b-4fd2-8ce3-81706a68d634.root',
            # # 2022G - split 0
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/70000/9100e1f2-e6fb-4ad3-9201-c421c75031b8.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/4f3add8f-0e5d-4912-a551-1190126880d0.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/72ae4983-b3a9-415d-a0fe-8255914514f0.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/c2305f06-0a01-4ae4-bc3b-e56a83c8fc05.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/c53ba0e4-ca63-416b-8e3d-f4054994146d.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/1a5c9680-b43e-499a-9ce8-942b58ed205a.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/bd11a2df-4042-4b1f-848b-53d0e3dd4b6a.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/f98d00a9-9fae-4b43-a493-8d2c6570edae.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/1bcce943-0b63-4d77-b42e-e229fdbd9d88.root',
            'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass0/MINIAOD/22Sep2023-v1/60000/b8ea45a7-0b5e-4ee4-b8bb-5b20d7c8b2a0.root',
            # # 2022G - split 1
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass1/MINIAOD/22Sep2023-v1/2560000/5380218e-9582-4fe6-8e79-c85ac7cc4394.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass1/MINIAOD/22Sep2023-v1/2560000/be9acaeb-0508-43bf-aa72-c0cbf7c7efb2.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass1/MINIAOD/22Sep2023-v1/2560000/d150d646-c63f-4593-91a1-f8895c06cf73.root',
            # # 2022G - split 2
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass2/MINIAOD/22Sep2023-v1/2560000/a4c2d9bb-1551-402b-8d60-fe303bf578c6.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass2/MINIAOD/22Sep2023-v1/2560000/835a7801-9cc5-4779-a90b-69cae583b7a9.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass2/MINIAOD/22Sep2023-v1/2560000/d1f0dc66-24f1-4745-bb61-6d240625d9f9.root',
            # # 2022G - split 3
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass3/MINIAOD/22Sep2023-v1/60000/2957ba96-cea0-4e95-a2db-e3f6b438e4d3.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass3/MINIAOD/22Sep2023-v1/60000/3d7a5ade-1ec6-4e91-b473-bffd75073301.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass3/MINIAOD/22Sep2023-v1/2560000/8afb3455-9168-467c-9c2b-b155c6e1a8a9.root',
            # # 2022G - split 4
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass4/MINIAOD/22Sep2023-v1/70000/64d1b128-5603-4e97-9689-4506823c8c93.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass4/MINIAOD/22Sep2023-v1/70000/7cd48ff8-c656-4ab1-9352-af3dd9661364.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass4/MINIAOD/22Sep2023-v1/70000/16de8e0d-6a9d-4085-b556-1ee379dc7a7f.root',
            # # 2022G - split 5
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass5/MINIAOD/22Sep2023-v1/2560000/7e5b3c93-a615-4d64-abde-0226dfeadfae.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass5/MINIAOD/22Sep2023-v1/2560000/490d9a00-380b-4bfd-8ec6-4c6970e8c611.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2022G/ParkingDoubleElectronLowMass5/MINIAOD/22Sep2023-v1/2560000/aa4c5c0b-3498-412c-a1f8-81ca67f75f17.root',
        ]
    elif options.year == 2023:
        options.inputFiles = [
            # # Z' SAMPLES
            f'file:/eos/cms/store/cmst3/group/xee/signalSamples/HAHM_DarkPhoton_13p6TeV_Nov2024/HAHM_ZpToEE_012jets_VBF_INCLUSIVE_noVBFcuts_Leta1p22_LpT5_M5_k2e_4_eps0p05_13p6TeV_MINIAOD.root'
            # f'file:/eos/cms/store/group/phys_susy/SOS/DarkPhoton_130X_Run3/MINIAOD/HAHM_ZdToEE_M15/HAHM_ZdToEE_M15.job{i}.root' for i in range(30)
        ] if options.isMC and options.isSignal else [
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/4e7a0372-833c-42b9-9b12-b66323d58da7.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/d17b2e6c-57b1-4847-a9b1-c4b499035a34.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/a9ff0f8a-a896-47b2-bd6b-c01a4778166c.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/ae1fbe5b-aed2-4eb3-bcb2-b36b748872fe.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/09ad3d9d-c180-4be7-8fa3-8367f06ff0fc.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/3487564d-db3e-4737-9e8d-e7233ebb3239.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/1c55667a-c1d0-441e-8067-66537cfbe765.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/128fcafa-d605-44d7-8553-cbdea27218e0.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/b4ffc90f-79bd-4c5e-99be-1a29b4f4f980.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v15-v2/140000/bd99c6d8-f670-489d-b14e-c3ed2aa8cef3.root',
        ] if options.isMC and options.isPromptJpsi else [
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/c269e0a6-3b8c-40de-a1bb-b922341b8475.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/0b263174-e6e1-4697-9b48-399165df2b0a.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/e1a5407d-cabf-4a6c-a416-b268701aa758.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/5d574d53-dd86-4833-a4dd-fb38afef8428.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/7c2c77e6-c5ec-4e9c-a5e9-7cb8071b2abd.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/9ad0c981-7067-43dd-839c-2f3119db16ce.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/8e0d20b5-08d0-4aa7-a208-d70a64145761.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/a38802fc-4e47-45a6-9622-c931ffbc42e8.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/c2f71616-b3f1-4c25-84d5-6da16e7785a5.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v6-v2/140000/28bc6e29-271c-4958-931f-ec0df8024210.root',
        ] if options.isMC and options.isPromptUpsilon else [
            # # central BuToKJpsi_JPsiToEE (should be similar), mini v4 2023, 2023 pre-BPix
            # 'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v3/40000/bc890edb-7cd8-4416-8938-42710506e833.root',
            # 'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v3/30000/0b8d58b6-fed7-4b68-9391-962bf73de310.root',
            # 'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v3/2820000/621b77eb-3b4c-4360-a056-4838d45f3e6c.root',
            # 'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v3/2820000/f71f3d75-cecb-4418-b04f-c7c0cab95334.root',
            # 'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v3/2820000/d5abfef3-f02c-4e89-bbe1-66ca3961eabe.root',
            # 'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v3/2820000/98b9286c-bf31-4678-86c1-739c249d3339.root',
            # 'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v3/2820000/7c043b6f-4d22-4022-8a0b-445bcb9ca444.root',
            # 'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v3/2820000/d955f561-8613-4600-896d-5d05feb499ad.root',
            # 'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v3/2820000/074180a5-76f9-4e1b-a1ed-c58dd85a6d55.root',
            # 'root://xrootd-cms.infn.it///store/mc/Run3Summer23MiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v3/2820000/a48687cb-7819-4e17-ad8b-e239729c7a40.root',
            # central BuToKJpsi_JPsiToEE (should be similar), mini v4 2023, 2023 POST-BPix
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/9bba4db3-9e00-4e97-b918-b4eda3059c15.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/a4551d66-6e54-47de-94d1-72cbeee6ea4e.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/4d776a87-a092-4c50-868b-34c54f040aa0.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/a73d0ecd-1f89-4d62-b08b-d46362f6f2fb.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/477dabc6-6a4b-46f2-935e-c902b68e2cf4.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/1b24c2db-675b-40ec-8d4d-3cd265db6f6a.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/104f45f4-3468-4f2d-8fe6-031f1e6af303.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/50478a74-da13-410a-a681-70fc6397db4b.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/011a365c-8ce2-4945-9b64-9fba5b2c79ed.root',
            'root://xrootd-cms.infn.it///store/mc/Run3Summer23BPixMiniAODv4/BuToKJPsi_JPsiToEE_SoftQCD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2023_realistic_postBPix_v2-v3/2820000/384a64cc-db68-4f50-a7e2-2da6ba9bfd70.root',
        ] if options.isMC else [
            # # 2023C files
            # 'root://xrootd-cms.infn.it///store/data/Run2023C/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v4-v1/2550000/5050267e-e959-4aec-a51c-8725965c8598.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2023C/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v4-v1/2550001/fd2e547d-6ec2-46ff-b4dd-c9e8bc4f3a11.root',
            # 'root://xrootd-cms.infn.it///store/data/Run2023C/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v4-v1/2550000/cc7a5cda-ba6e-4269-aa3f-4b73002b64c5.root',
            # 2023D
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/95e1791e-7dec-499f-8a11-3ee133300eb5.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/12117d01-dc26-496c-9dcd-0c8310a008e3.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/c46bf23a-9284-4f7e-8d6b-7305fe7a9a70.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/f305f435-af66-4db3-ba8e-91ce02e6b431.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/981369cd-255b-40f4-bc0d-84b0d41216a8.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/a984038b-a2c1-4b1d-b793-64a0f47b6738.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/fb49ceb2-8472-4801-9f7b-66e9a51b4953.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/a524cd8c-c707-4318-917c-c1de5c08101a.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/98134754-f152-4ff5-8020-e60188f42d70.root',
            'root://xrootd-cms.infn.it///store/data/Run2023D/ParkingDoubleElectronLowMass/MINIAOD/22Sep2023_v2-v1/2560000/cdd08e76-70dc-4ee1-bc2e-9f531cd1d1ab.root',
        ]

annotation = '%s nevts:%d' % (outputFileNANO, options.maxEvents)

# Process
from Configuration.StandardSequences.Eras import eras
from PhysicsTools.BParkingNano.modifiers_cff import *

# Attaching modifiers
modifiers = []

if options.mode not in ["reco", "eff", "trg", "vbf"]:
    raise ValueError("Mode must be reco (standard reconstruction), eff (efficiency study mode) or trg (trigger matching study mode)")

if options.mode == "eff":
    # Efficiency study:
    #     removes all selections among:
    #      - trigger selection (hltHighLevel filter)
    #      - electron selection (all selections inside electronsForAnalysis filter)
    #      - dielectron fit (both pre- and post-fit selections)
    #     Electron and dielectron-level selections are replaced by flags in the output,
    #     so that efficiency can be studied differentially separately.
    #     Trigger selection efficiency is evaluated using trgTable values.
    modifiers.append(efficiencyStudy)
elif options.mode == "trg":
    # Trigger matching study:
    #   removes all trigger selections and opens up deltaR max value for trigger-matching
    #   ambiguities not resolved -- looking at best match for each electron.
    modifiers.append(triggerMatchingStudy)
elif options.mode == "vbf":
    if options.year == 2022:
        raise ValueError("VBF mode is not supported for 2022 data")
    elif options.year == 2023:
        raise NotImplementedError("VBF mode is not implemented for 2023 data yet")
    elif options.year == 2024:
        modifiers.append(vbfSkimming2024)


process = cms.Process('BParkNANO', eras.Run3, *modifiers)

# import of standard configurations
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('PhysicsTools.BParkingNano.nanoBPark_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.MessageLogger.cerr.FwkReport.reportEvery = options.reportEvery
# process.MessageLogger.cerr.threshold = "DEBUG"
# process.MessageLogger.debugModules = ["*"]

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

# Input source
process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring(options.inputFiles),
    secondaryFileNames = cms.untracked.vstring(),
    skipEvents=cms.untracked.uint32(options.skip),
)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(options.wantSummary),
)

process.nanoMetadata.strings.tag = annotation
# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string(annotation),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition
process.FEVTDEBUGHLToutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM-RECO'),
        filterName = cms.untracked.string('')
    ),
    fileName = outputFileFEVT,
    outputCommands = (cms.untracked.vstring('keep *',
                                            'drop *_*_SelectedTransient*_*',
                     )),
    splitLevel = cms.untracked.int32(0)
)

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    fileName = outputFileNANO,
    outputCommands = cms.untracked.vstring(
      # 'drop *',
      "keep nanoaodFlatTable_*Table_*_*",     # event data
      "keep nanoaodUniqueString_nanoMetadata_*_*",   # basic metadata
      "keep nanoaodMergeableCounterTable_*Table_*_*", # run data
    )

)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, globaltag, '')

from PhysicsTools.BParkingNano.nanoBPark_cff import *
from PhysicsTools.BParkingNano.electronsTrigger_cff import *

process = nanoAOD_customizeEgammaPostRecoTools(process)
process = nanoAOD_customizeEle(process)
process = nanoAOD_customizeElectronFilteredBPark(process)
if options.saveAllNanoContent:
    process = nanoAOD_customizeNanoContent(process)
    process = nanoAOD_customizeCommon(process)
process = nanoAOD_customizeTriggerBitsBPark(process)
process = nanoAOD_customizeElectronTriggerSelectionBPark(process)
process = nanoAOD_customizeDiElectron(process)

process.nanoAOD_DiEle_step = cms.Path(process.egammaPostRecoSeq
                                    + process.nanoSequence
                                    + process.nanoEleSequence
                                    + process.nanoDiEleSequence)

# customisation of the process.
if options.isMC:
    from PhysicsTools.BParkingNano.nanoBPark_cff import nanoAOD_customizeMC
    nanoAOD_customizeMC(process, options.saveAllNanoContent)

process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGHLToutput_step = cms.EndPath(process.FEVTDEBUGHLToutput)
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_DiEle_step,
                                process.endjob_step,
                                process.NANOAODoutput_step)

if options.wantFullRECO:
    process.schedule = cms.Schedule(process.nanoAOD_DiEle_step,
                                    process.endjob_step,
                                    process.FEVTDEBUGHLToutput_step,
                                    process.NANOAODoutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
process.NANOAODoutput.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring('nanoAOD_DiEle_step')
)

### from https://hypernews.cern.ch/HyperNews/CMS/get/physics-validation/3287/1/1/1/1/1.html
process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab=cms.untracked.bool(True)

process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
