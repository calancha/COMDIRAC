"""
  Retrieve input sandbox for a DIRAC job
"""

import DIRAC
from DIRAC.Core.Base import Script

import os
import pprint

class Params:
  def __init__ ( self ):
    self.outputDir = None
    self.verbose = False
    self.downloadJDL = False
    self.inputSandbox = False
    self.noJobDir = False
    self.jobGroup = []

  def setOutputDir( self, arg = None ):
    self.outputDir = arg

  def getOutputDir( self ):
    return self.outputDir

  def setDownloadJDL( self, arg = None ):
    self.downloadJDL = True

  def getDownloadJDL( self ):
    return self.downloadJDL

  def setInputSandbox( self, arg = None ):
    self.inputSandbox = True

  def getInputSandbox( self ):
    return self.inputSandbox

  def setVerbose( self, arg = None ):
    self.verbose = True

  def getVerbose( self ):
    return self.verbose

  def setNoJobDir( self, arg = None ):
    self.noJobDir = True

  def getNoJobDir( self ):
    return self.noJobDir

  def setJobGroup( self, arg = None ):
    if arg:
      self.jobGroup.append( arg )

  def getJobGroup( self ):
    return self.jobGroup

params = Params()

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] ... JobID ...' % Script.scriptName,
                                     'Arguments:',
                                     '  JobID:    DIRAC Job ID' ] ) )

Script.registerSwitch( "D:", "OutputDir=", "destination directory", params.setOutputDir )
Script.registerSwitch( "j", "JDL", "download job JDL instead of input sandbox", params.setDownloadJDL )
Script.registerSwitch( "", "Sandbox", "donwload input sandbox, even if JDL was required", params.setInputSandbox )
Script.registerSwitch( "v", "verbose", "verbose output", params.setVerbose )
Script.registerSwitch( "n", "NoJobDir", "do not create job directory", params.setNoJobDir )
Script.registerSwitch( "g:", "JobGroup=", "Get output for jobs in the given group", params.setJobGroup )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

from DIRAC.Interfaces.API.Dirac  import Dirac
from DIRAC.Core.Utilities.Time import toString, date, day

dirac = Dirac()
exitCode = 0

for jobGroup in params.getJobGroup():
  jobDate = toString( date() - 30 * day )

  # Choose jobs no more than 30 days old
  result = dirac.selectJobs( jobGroup = jobGroup, date = jobDate )
  if not result['OK']:
    if not "No jobs selected" in result['Message']:
      print "Error:", result['Message']
      exitCode = 2
  else:
    args += result['Value']

jobs = []

outputDir = params.getOutputDir() or os.path.curdir

for arg in args:
  if os.path.isdir( os.path.join( outputDir, "InputSandbox%s" % arg ) ) and not params.getNoJobDir():
    print "Input for job %s already retrieved, remove the output directory to redownload" % arg
  else:
    jobs.append( arg )

if jobs:
  if not os.path.isdir( outputDir ):
    os.makedirs( outputDir )

  errors = []
  inputs = {}
  for job in jobs:
    if not params.getNoJobDir():
      destinationDir = os.path.join( outputDir, "InputSandbox%s" % job )
    else:
      destinationDir = outputDir
    if not os.path.exists( destinationDir ): os.makedirs( destinationDir )

    inputs[job] = {"destinationDir" : destinationDir}

    if params.getInputSandbox() or not params.getDownloadJDL():
      result = dirac.getInputSandbox( job, outputDir = outputDir, noJobDir = params.getNoJobDir() )
      if result['OK']:
        inputs[job]["isb"] = destinationDir
      else:
        errors.append( result["Message"] )
        exitCode = 2

    if params.getDownloadJDL():
      result = dirac.getJobJDL( job, printOutput = False )
      if result['OK']:
        jdl = pprint.pformat( result["Value"] )
        f = open ( os.path.join( destinationDir, "%s.jdl" % job ), 'w' )
        f.write( jdl )
        f.close()
        inputs[job]["jdl"] = jdl
      else:
        errors.append( result["Message"] )
        exitCode = 2

  for error in errors:
    print "ERROR: %s" % error

  if params.getVerbose():
    for j, d in inputs.items():
      if "isb" in d: print "%s: InputSandbox" % j, d["isb"]
      if "jdl" in d: print "%s: JDL" % j, d["jdl"]
DIRAC.exit( exitCode )

