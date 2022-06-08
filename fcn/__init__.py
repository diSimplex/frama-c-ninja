# This is the Frama-C-Ninja (fcn) package

import json
import os
import shlex
import sys
import yaml

########################################################################
# Now deal with click commands

def cli() :
  with open("compile_commands.json") as jFile :
    jCompileCommands = json.load(jFile)

  for aCompCmd in jCompileCommands :
    aCmd = shlex.split(aCompCmd['command'])
    print(yaml.dump(aCmd))
