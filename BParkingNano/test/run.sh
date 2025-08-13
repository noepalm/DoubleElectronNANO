cmsRun run_nano_cfg.py isMC=1 maxEvents=1000 reportEvery=50 lhcRun=2 # MC with Run 2 (BParking 2018)
cmsRun run_nano_cfg.py isMC=0 maxEvents=1000 reportEvery=50 lhcRun=2 # Data with Run 2 (BParking 2018)
cmsRun run_nano_cfg.py isMC=1 maxEvents=1000 reportEvery=100 lhcRun=3 # MC with Run 3
cmsRun run_nano_cfg.py isMC=0 maxEvents=5000 reportEvery=100 lhcRun=3 year=2023 # Data with Run 3
cmsRun run_nano_cfg.py isMC=1 maxEvents=5000 reportEvery=100 lhcRun=3 year=2023 isSignal=0 # Data with Run 3
cmsRun run_nano_cfg.py isMC=0 maxEvents=3000 reportEvery=100 lhcRun=3 year=2022 # Data with Run 3 2022
cmsRun run_nano_cfg.py isMC=1 maxEvents=3000 reportEvery=100 lhcRun=3 year=2022 isSignal=0 # Data with Run 3 2022