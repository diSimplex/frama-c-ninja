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
    print("  -h, --help         print this help message")
    print("  -gui               run the frama-c-gui instead of the frama-c")
    print("  -fcr <configName>  load the specified Frama-C-runner configuration")
    print("                     file (no configuration is loaded if no file is")
    print("                     found corresponding to `configName`)")
    print("                     (default `configName`: 'default')")
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

  if not srcDict :
    print("No src files found")
    print("  nothing to do...")
    sys.exit(1)

  ################################################################
  # now load any local frama-c arguments

  # compute the fcrConfig file name
  fcrConfigName = 'default'
  if cliArguments.count('-fcr') :
    fcrConfigIndex = cliArguments.index('-fcr')
    cliArguments.remove('-fcr')
    fcrConfigName = cliArguments.pop(fcrConfigIndex)

  fcrParts = list(Path.cwd().parts)
  rootPart = fcrParts.pop(0)
  fcrParts[0] = rootPart + fcrParts[0]
  fcrConfigPath = None
  while fcrParts :
    aConfigPath = Path(os.path.join(*fcrParts, '.fcrConfig', fcrConfigName))
    if aConfigPath.exists() :
      fcrConfigPath = aConfigPath
      break
    fcrParts.pop()

  fcrConfig = {}
  if fcrConfigPath :
    with open(fcrConfigPath) as fcrConfigFile :
      fcrConfigYaml = yaml.safe_load(fcrConfigFile.read())
    if fcrConfigYaml :
      fcrConfig = fcrConfigYaml

  # now incorporate this configuration into our variables
  if 'srcs' in fcrConfig :
    for aSrc in fcrConfig['srcs'] :
      srcDict[aSrc] = True
  fcArguments = []
  if 'arguments' in fcrConfig :
    fcArguments = fcrConfig['arguments']
  if 'environment' in fcrConfig :
    for aKey, aVal in fcrConfig['environment'].items() :
      os.putenv(aKey, aVal)

  ################################################################
  # now build the frama-c command

  fcCmd.append("-json-compilation-database=./compile_commands.json")
  for anArg in fcArguments :
    fcCmd.append(str(anArg))
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
