from CRABClient.UserUtilities import config
import yaml
import datetime
import copy
from fnmatch import fnmatch
from argparse import ArgumentParser

production_tag = datetime.date.today().strftime('%Y%b%d')

config = config()
config.section_('General')
config.General.transferOutputs = True
config.General.transferLogs = True
config.General.workArea = 'DoubleElectronNANO_{:s}'.format(production_tag)

config.section_('Data')
config.Data.publication = False
config.Data.outLFNDirBase = '/store/group/cmst3/group/xee'

config.Data.inputDBS = 'global'

config.section_('JobType')
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '../test/run_nano_cfg.py'
config.JobType.maxJobRuntimeMin = 3000
config.JobType.maxMemoryMB = 3500
config.JobType.allowUndistributedCMSSW = True

config.section_('User')
config.section_('Site')
config.Site.storageSite = 'T2_CH_CERN'

if __name__ == '__main__':

  from CRABAPI.RawCommand import crabCommand
  from CRABClient.ClientExceptions import ClientException
  from http.client import HTTPException
  from multiprocessing import Process

  def submit(config):
      try:
          crabCommand('submit', config = config)
      except HTTPException as hte:
          print("Failed submitting task:",hte.headers)
      except ClientException as cle:
          print("Failed submitting task:",cle)

  parser = ArgumentParser()
  parser.add_argument('-y', '--yaml', default = 'samples_Run3.yml', help = 'File with dataset descriptions')
  parser.add_argument('-f', '--filter', default='*', help = 'filter samples, POSIX regular expressions allowed')
  parser.add_argument('-r', '--lhcRun', type=int, default=3, help = 'Run 2 or 3 (default)')
  parser.add_argument('-yy', '--year', type=int, default=2023, help = 'Year of the dataset')
  parser.add_argument('-m', '--mode', type=str, default="reco", help= 'Reconstruction mode (reco = apply skim, eff = disable all selections)')
  parser.add_argument('-s', '--saveAllNanoContent', type=bool, default=False, help= 'Save all nano content (default = False)')
  parser.add_argument('-sr', '--saveRegressionVars', type=bool, default=False, help='Save regression variables (default = False)')
  args = parser.parse_args()

  configs = []
  with open(args.yaml) as f:
    doc = yaml.load(f,Loader=yaml.FullLoader) # Parse YAML file
    common = doc['common'] if 'common' in doc else {'data' : {}, 'mc' : {}}

    # loop over samples
    for sample, info in doc['samples'].items():
      # Input DBS
      input_dbs = info['dbs'] if 'dbs' in info else None
      # Given we have repeated datasets check for different parts
      parts = info['parts'] if 'parts' in info else [None]
      for part in parts:
        name = sample.replace('%d',str(part)) if part is not None else sample

        # filter names according to what we need
        if not fnmatch(name, args.filter): continue
        print('submitting', name)

        isMC = info['isMC']

        config.Data.inputDBS = input_dbs if input_dbs is not None else 'global'

        config.Data.inputDataset = info['dataset'].replace('%d',str(part)) \
                                   if part is not None else \
                                      info['dataset']

        config.General.requestName = name
        common_branch = 'mc' if isMC else 'data'
        config.Data.splitting = 'FileBased' if isMC else 'LumiBased'
        if not isMC:
            config.Data.lumiMask = info.get(
                'lumimask',
                common[common_branch].get('lumimask', None)
            )
        else:
            config.Data.lumiMask = ''

        config.Data.unitsPerJob = info.get(
            'splitting',
            common[common_branch].get('splitting', None)
        )
        globaltag = info.get(
            'globaltag',
            common[common_branch].get('globaltag', None)
        )

        config.JobType.pyCfgParams = [
            'isMC={:.0f}'.format(int(isMC)),
            'reportEvery=1000',
            'tag={:s}'.format(production_tag),
            'globalTag={:s}'.format(globaltag),
            'lhcRun={:.0f}'.format(args.lhcRun),
            'year={:.0f}'.format(args.year),
            'mode={:s}'.format(args.mode),
            'saveAllNanoContent={:.0f}'.format(int(args.saveAllNanoContent)),
            'saveRegressionVars={:.0f}'.format(int(args.saveRegressionVars)),
        ]

        ext1 = {False:'data', True:'mc'}
        ext2 = {3 : 'Run3', 2 : 'Run2'}
        ext3 = {"eff" : "noskim", "reco" : "", "trg" : ""}
        ext4 = {True: 'allNano', False: ''}
        ext5 = {True: 'withRegVars', False: ''}

        output_flags = ["DoubleElectronNANO", ext2[args.lhcRun], str(args.year), ext1[isMC]]
        if args.mode == "eff":
            output_flags.append(ext3[args.mode])
        if args.saveAllNanoContent:
            output_flags.append(ext4[args.saveAllNanoContent])
        if args.saveRegressionVars:
            output_flags.append(ext5[args.saveRegressionVars])
        output_flags.append(production_tag)

        config.JobType.outputFiles = ['_'.join(output_flags)+'.root']
        config.Data.outLFNDirBase = '/store/group/cmst3/group/xee'

        if "HAHM" in name:
            config.Data.outLFNDirBase += '/signalSamples/HAHM_DarkPhoton_13p6TeV_Nov2024'
        elif "Run20" in name:
            config.Data.outLFNDirBase += '/data'
        else:
            config.Data.outLFNDirBase += '/backgroundSamples'

        last_subfolder_pieces = []

        if args.mode == "eff":
            last_subfolder_pieces.append('noskim')
        if args.saveAllNanoContent:
            last_subfolder_pieces.append('allnanoColl')
        if args.saveRegressionVars:
            last_subfolder_pieces.append('withRegVars')

        if len(last_subfolder_pieces) > 0:
            config.Data.outLFNDirBase += '/' + '_'.join(last_subfolder_pieces)

        print()
        print(config)
        config_copy = copy.deepcopy(config)
        configs.append(config_copy)
    print("Do you want to submit all task? (y/n)")
    if input().strip().lower() == 'y':
        for c in configs:
            submit(c)
