## Copyright (c) 2009 Astun Technology

## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:

## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
## THE SOFTWARE.

###
import os
import sys
import pg

# Import Astun stuff
import OutPut, ConfigParse

class ClassData:

 	_conn1 = 0
  

	def __init__(self, Out):
 		opts = ConfigParse.OptParser()   
		dbcreds = opts.ConfigSectionMap('DatabaseConnection')

		self.dbname = dbcreds['dbname']
		self.host = dbcreds['host']
		self.username = dbcreds['username']
		self.password = dbcreds['password']
		self.port = int(dbcreds['port'])

		self._conn = 0
    		self._output = Out
    		self._bError = False
		#####
 
	#####
	# Open connection to postgres
	###

	def OpenPostgres(self):
		result = None
  
		## To ensure we have a connection
		if ( self._conn == 0):
			self._output.OutputInfo( 'Opening PostgreSQL connection' )
    
		try:
			# Get the config settings
			sHost = self.host
			sDatabase = self.dbname
			sUser = self.username
			sPwd = self.password
			sPort = self.port
    
			# Now connect
			self._conn = pg.connect( host=sHost, user=sUser, dbname=sDatabase, passwd=sPwd, port= sPort)
    
		except KeyboardInterrupt:
			self._output.OutputError('Keyboard interrupt detected', False )
			raise
			    
		except:
			self._output.OutputError( 'On connecting to Postgres DB',True)
			self._output.OutputException( sys.exc_info( ), True)
			self._bError = True
  
		return self._conn

	#####

	#####
	# Close a connection
	###

	def ClosePostgres( self ):
		# Close the connection
		if self._conn <> 0:
			self._output.OutputInfo( 'Closing PostgreSQL connection' )
    
		try:
			self._conn.close( )
    
		except KeyboardInterrupt:
			self._output.OutputError( 'Keyboard interrupt detected', False )
			raise
    
		except:
			self._output.OutputError( 'On closing PostgresSQL connection', True )
			self._output.OutputException( sys.exc_info( ), True )
			self._conn = 0
    
		return
		#####

 
    
    

       


