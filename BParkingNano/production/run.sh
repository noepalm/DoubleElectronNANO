source /cvmfs/cms.cern.ch/common/crab-setup.sh #needed to make CRABClient work

# Uncommented as required ...

## 2022
#python3 submit_on_crab.py --filter=Run2022E_part0 --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022
#python3 submit_on_crab.py --filter=Run2022C_part* --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022
#python3 submit_on_crab.py --filter=Run2022Dv1_part* --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022
#python3 submit_on_crab.py --filter=Run2022Dv2_part* --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022
#python3 submit_on_crab.py --filter=Run2022E_part* --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022
#python3 submit_on_crab.py --filter=Run2022F_part* --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022
#python3 submit_on_crab.py --filter=Run2022G_part* --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022

# python3 submit_on_crab.py --filter=BuToKJpsi_Toee_2022preEE --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022
#python3 submit_on_crab.py --filter=BuToKJpsi_Toee_2022postEE --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022

## BACKGROUND SAMPLES
# python3 submit_on_crab.py --filter=JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2022preEE  --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022 --mode=eff --saveAllNanoContent=True
# python3 submit_on_crab.py --filter=JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2022postEE  --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022 --mode=eff --saveAllNanoContent=True
# python3 submit_on_crab.py --filter=JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2022preEE  --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022 --mode=eff --saveAllNanoContent=True
# python3 submit_on_crab.py --filter=JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2022postEE  --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022 --mode=eff --saveAllNanoContent=True
# python3 submit_on_crab.py --filter=UpsilonToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2022preEE  --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022 --mode=eff --saveAllNanoContent=True
# python3 submit_on_crab.py --filter=UpsilonToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2022postEE  --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022 --mode=eff --saveAllNanoContent=True
# python3 submit_on_crab.py --filter=UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2022preEE  --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022 --mode=eff --saveAllNanoContent=True
# python3 submit_on_crab.py --filter=UpsilonToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2022postEE  --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022 --mode=eff --saveAllNanoContent=True

python3 submit_on_crab.py --filter=InclusiveDileptonMinBias  --yaml=samples_Run3_2022.yml --lhcRun=3 --year=2022 --saveAllNanoContent=True

### 2023
## DATA
# python3 submit_on_crab.py --filter=Run2023Cv* --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023
# python3 submit_on_crab.py --filter=Run2023Dv* --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023
# python3 submit_on_crab.py --filter=Run2023Dv1 --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023 --saveAllNanoContent=True

## BACKGROUND SAMPLES
# python3 submit_on_crab.py --filter=BuToKJpsi_Toee_2023preBPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023
# python3 submit_on_crab.py --filter=BuToKJpsi_Toee_2023BPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023
# python3 submit_on_crab.py --filter=JPsiToEE_pth0to10_*_2023preBPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023
# python3 submit_on_crab.py --filter=JPsiToEE_pth0to10_*_2023BPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023
# python3 submit_on_crab.py --filter=JPsiToEE_pth10toInf_*_2023preBPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023
# python3 submit_on_crab.py --filter=JPsiToEE_pth10toInf_*_2023BPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023
# python3 submit_on_crab.py --filter=UpsilonToEE_pth0to10_*_2023preBPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023
# python3 submit_on_crab.py --filter=UpsilonToEE_pth0to10_*_2023BPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023
# python3 submit_on_crab.py --filter=UpsilonToEE_pth10toInf_*_2023preBPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023
# python3 submit_on_crab.py --filter=UpsilonToEE_pth10toInf_*_2023BPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023

# python3 submit_on_crab.py --filter=JPsiToEE_pth10toInf_*_2023BPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023 --mode=eff --saveAllNanoContent=True
# python3 submit_on_crab.py --filter=JPsiToEE_pth10toInf_*_2023preBPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023 --mode=eff --saveAllNanoContent=True
# python3 submit_on_crab.py --filter=JPsiToEE_pth0to10_*_2023preBPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023 --mode=eff --saveAllNanoContent=True
# python3 submit_on_crab.py --filter=JPsiToEE_pth0to10_*_2023BPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023 --mode=eff --saveAllNanoContent=True
# python3 submit_on_crab.py --filter=UpsilonToEE_pth0to10_*_2023preBPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023 
# python3 submit_on_crab.py --filter=UpsilonToEE_pth0to10_*_2023BPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023 
# python3 submit_on_crab.py --filter=UpsilonToEE_pth10toInf_*_2023preBPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023 
# python3 submit_on_crab.py --filter=UpsilonToEE_pth10toInf_*_2023BPix --yaml=samples_Run3_2023.yml --lhcRun=3 --year=2023 
