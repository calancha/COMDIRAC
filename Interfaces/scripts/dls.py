#!/usr/bin/env python

"""
list FileCatalog file or directory
"""

from COMDIRAC.Interfaces import DSession
from COMDIRAC.Interfaces import createCatalog
from DIRAC.Core.Utilities.List import uniqueElements

if __name__ == "__main__":
  from DIRAC.Core.Base import Script


  Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                       'Usage:',
                                       '  %s [options] [path] ... [path]' % Script.scriptName,
                                       'Arguments:',
                                       ' path:     file/directory path',
                                       '', 'Examples:',
                                       '  $ dls',
                                       '  $ dls ..',
                                       '  $ dls /'] ) )
  Script.registerSwitch( "l", "long", "detailed listing")
  Script.registerSwitch( "L", "list-replicas", "detailed listing with replicas")
  Script.registerSwitch( "f", "full-path", "Show full path")
  Script.registerSwitch( "t", "time", "time based order")
  Script.registerSwitch( "r", "reverse", "reverse sort order")
  Script.registerSwitch( "n", "numericid", "numeric UID and GID")
  Script.registerSwitch( "S", "size", "size based order")
  Script.registerSwitch( "H", "human-readable","size human readable")

  Script.parseCommandLine( ignoreErrors = True )
  opts = [ ntup[0] for ntup in Script.getUnprocessedSwitches() ]
  short_opts = ['l','L','f','t','r','n','S','H']
  long_opts = ['long','list-replicas','full-path','time','reverse',
               'numericid','size','human-readable']
  optsDict = dict( zip( long_opts, short_opts ) )

  for lopt,sopt in optsDict.items():
    opts = [ xopt.replace( lopt, sopt ) for xopt in opts ]

  args = Script.getPositionalArgs()

  from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import FileCatalogClientCLI

  session = DSession( )

  Script.enableCS( )

  fccli = FileCatalogClientCLI( createCatalog( ) )
  # Allow duplicate options: do_ls method take care on how
  # to order files checking which opt. from ['t','S'] comes last.
  options = ''
  arguments = ' '.join( uniqueElements ( args ) )
  cmdArgs = arguments
  if opts:
    options = '-' + ''.join( opts )
    cmdArgs = options + ' ' + arguments

  fccli.do_ls( cmdArgs )
