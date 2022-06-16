# This is the Frama-C-runner (fcr) package

import json
import os
from pathlib import Path
import shlex
import sys
import yaml

########################################################################
# Now deal with click commands

def cli() :

  ################################################################
  # start by extracting the command line arguments
  cliArguments = list(sys.argv)
  cliArguments.pop(0)

  if '-h' in cliArguments or '--help' in cliArguments :
    print("fcr [-h|--help] [-gui] [-no-config] [frama-c options]")
    print("")
    print("  -h, --help  print this help message")
    print("  -gui        run the frama-c-gui instead of the frama-c")
    print("  -no-config  do not load any local .fcrConfig files")
    print("")
    print("  any valid frama-c or frama-c-gui options ")
    print("")
    sys.exit(0)

  fcCmd = ['frama-c']
  if '-gui' in cliArguments :
    fcCmd = ['frama-c-gui']
    cliArguments.remove('-gui')

  ################################################################
  # now extract the src files and -I include arguments from the
  # compile_commands.json file

  jcdbPath = Path('compile_commands.json')
  if not jcdbPath.exists() :
    print("No JSON Compilation Database found in the current directory!")
    print("  nothing to do...")
    sys.exit(1)

  with open("compile_commands.json") as jFile :
    jCompileCommands = json.load(jFile)

  includesDict = {}
  srcDict      = {}

  for aCompCmd in jCompileCommands :
    srcDict[aCompCmd['file']] = True
    aCmd = shlex.split(aCompCmd['command'])
    for anArgument in aCmd :
      if anArgument.startswith('-I') :
        includesDict[anArgument.strip()] = True

  if not srcDict :
    print("No src files found")
    print("  nothing to do...")
    sys.exit(1)

  ################################################################
  # now load any local frama-c arguments

  if '-no-config' in cliArguments :
    fcArguments = []
    cliArguments.remove('-no-config')
  else :
    fcrParts = list(Path.cwd().parts)
    rootPart = fcrParts.pop(0)
    fcrParts[0] = rootPart + fcrParts[0]
    fcrConfigPath = None
    while fcrParts :
      aConfigPath = Path(os.path.join(*fcrParts, '.fcrConfig'))
      if aConfigPath.exists() :
        fcrConfigPath = aConfigPath
        break
      fcrParts.pop()

    fcArguments = []
    if fcrConfigPath :
      with open(fcrConfigPath) as fcrConfigFile :
        fcrConfigYaml = yaml.safe_load(fcrConfigFile.read())
      if fcrConfigYaml :
        fcArguments = fcrConfigYaml
    #print(yaml.dump(fcArguments))

  ################################################################
  # now build the frama-c command

  if includesDict :
    incStr = " ".join(includesDict.keys())
    fcCmd.append(f"-cpp-extra-args=\"{incStr}\"")
  for anArg in fcArguments :
    fcCmd.append(anArg)
  for anArg in cliArguments :
    fcCmd.append(anArg)
  for aSrcFile in srcDict.keys() :
    fcCmd.append(aSrcFile)

  fcCmd = " ".join(fcCmd)
  print("")
  print("---------------------------------------------------------------")
  print(fcCmd)
  print("---------------------------------------------------------------")
  os.system(fcCmd)
  print("---------------------------------------------------------------")
