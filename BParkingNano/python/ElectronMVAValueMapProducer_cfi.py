import FWCore.ParameterSet.Config as cms

mvaConfigsForEleProducer = cms.VPSet( )

# Import and add all desired MVAs
from RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring16_HZZ_V1_cff \
    import mvaEleID_Spring16_HZZ_V1_producer_config
mvaConfigsForEleProducer.append( mvaEleID_Spring16_HZZ_V1_producer_config )

from RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring16_GeneralPurpose_V1_cff \
    import mvaEleID_Spring16_GeneralPurpose_V1_producer_config
mvaConfigsForEleProducer.append( mvaEleID_Spring16_GeneralPurpose_V1_producer_config )

from RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V1_cff \
    import mvaEleID_Fall17_noIso_V1_producer_config
mvaConfigsForEleProducer.append( mvaEleID_Fall17_noIso_V1_producer_config )

from RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V1_cff \
    import mvaEleID_Fall17_iso_V1_producer_config
mvaConfigsForEleProducer.append( mvaEleID_Fall17_iso_V1_producer_config )

from RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V2_cff \
    import mvaEleID_Fall17_noIso_V2_producer_config
mvaConfigsForEleProducer.append( mvaEleID_Fall17_noIso_V2_producer_config )

from RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V2_cff \
    import mvaEleID_Fall17_iso_V2_producer_config
mvaConfigsForEleProducer.append( mvaEleID_Fall17_iso_V2_producer_config )

# from RecoEgamma.ElectronIdentification.Identification.mvaElectronID_RunIIIWinter22_noIso_V1_cff \
#     import mvaEleID_RunIIIWinter22_noIso_V1_producer_config
# mvaConfigsForEleProducer.append( mvaEleID_RunIIIWinter22_noIso_V1_producer_config )

from RecoEgamma.ElectronIdentification.Identification.mvaElectronID_BParkRetrain_cff \
    import mvaEleID_BParkRetrain_producer_config
mvaConfigsForEleProducer.append( mvaEleID_BParkRetrain_producer_config )

from RecoEgamma.ElectronIdentification.Identification.mvaElectronID_RunIII_custom_JPsitoEE_cff \
    import mvaEleID_RunIII_custom_JPsitoEE_V1_producer_config
mvaConfigsForEleProducer.append( mvaEleID_RunIII_custom_JPsitoEE_V1_producer_config )

print("mvaConfigsForEleProducer = ", mvaConfigsForEleProducer)

electronMVAValueMapProducer = cms.EDProducer('ElectronMVAValueMapProducer',
                                             # The module automatically detects AOD vs miniAOD, so we configure both
                                             #
                                             # AOD case
                                             #
                                             src = cms.InputTag('gedGsfElectrons'),
                                             #
                                             # miniAOD case
                                             #
                                             srcMiniAOD = cms.InputTag('customSlimmedElectrons', processName=cms.InputTag.skipCurrentProcess()),
                                             #
                                             # MVA configurations
                                             #
                                             mvaConfigurations = mvaConfigsForEleProducer
                                             )
