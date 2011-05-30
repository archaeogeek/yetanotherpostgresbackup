# import modules
import pg, os, sys, shutil
from datetime import date
import ConfigParser

#astun
from Required import ConfigParse, Email, OutPut, Data, CleanUp

class databaseBackup():

	def __init__(self):
		
		# get today's date
		now = date.today()
		self.dateStr = now.isoformat()
		
		# generic config
		opts = ConfigParse.OptParser()
		dbcreds = opts.ConfigSectionMap('DatabaseConnection')
		backupcreds = opts.ConfigSectionMap('BackupCreds')

		#Backup
		self.pg_dump_path = backupcreds['pg_dump_path']
		self.remote_locn = backupcreds['remote_locn']
		self.local_locn = backupcreds['local_locn']

		#Output to log file
		self.out = OutPut.ClassOutput('Dbf_BU')

		#Cleanup
		self.cleanup = CleanUp.ClassCleanUp(self.out)


		#Email
		self.sendmail = Email.sendEmail(self.out)

		#Database Connection
		self._Data = Data.ClassData(self.out)
		self.host = dbcreds['host']
		self.username = dbcreds['username']
		self.password = dbcreds['password']
		self.port = int(dbcreds['port'])


	def fileCopy(self, dbf):
		"""If a remote location is defined, copy the dump file there and delete the local copy"""
		if self.remote_locn:
			self.remote_file = self.remote_locn + self.dump_file
		
			try:
				shutil.copy(self.local_file, self.remote_file)
				os.remove(self.local_file)
				self.out.OutputInfo("Successfully copied %s to remote location %s." % (self.local_file, self.remote_locn))
				self.out.OutputInfo("Remote backup of database %s succeeded on %s." % (dbf, self.dateStr))			
				self.cleanup.FileCleanup(dbf, self.remote_locn)
			except:
				self.out.OutputError("Could not copy file %s to remote location %s." % (self.local_file, self.remote_locn) )
				email_subject = "Remote Backup Failed"
				email_body = "The remote backup of database %s failed on %s" % (dbf, self.dateStr)
				self.sendmail.sendEmail(email_subject, email_body)
				sys.exit(1)
		else:
			self.cleanup.FileCleanup(dbf, self.local_locn)
		

	def encodingcheck(self, dbf):
		"""check the client encoding and the database encoding, and flag up if there is a mismatch between the two that might cause the backup to fail"""
		
		eSQL = "SHOW client_encoding"
		e_sql = self._conn.query(eSQL)
		e_res = e_sql.getresult()
		for row in e_res:
			client_encode = row[0]
		dSQL = "SELECT pg_encoding_to_char(encoding) FROM pg_database WHERE datname = '%s'" % dbf
		d_sql = self._conn.query(dSQL)
		d_res = d_sql.getresult()
		for row in d_res:
			db_encode = row[0]
			if client_encode != db_encode:
				try:
					os.putenv('PGCLIENTENCODING','UTF8')
					self.out.OutputInfo("Temporarily changing PGCLIENTENCODING variable.")				
				except:
					self.out.OutputError("Could not change client encoding. Backup aborted.")
					email_subject = "Backup aborted"
					email_body = "Database % backup aborted due to encoding issues on %s" % (dbf, self.dateStr)
					self.sendmail.sendEmail(email_subject, email_body)
					self._Data.ClosePostgres()
					sys.exit(1)
				
	
	def backup(self):
		"""MAIN DATABASE BACKUP FUNCTION"""

		#set up logging
      		self._sName = '%s_backup' % self.dateStr
      		self.out.SetFilename( self._sName + '.log' )
      		self.out.SetOutputLevel(OutPut.OUTPUTLEVEL_INFO)
      		self.out.SetFileLogging( True )
      		self.out.OutputInfo('___________________________')
      		self.out.OutputInfo('Database Backup starting')

		try:
			self._conn = self._Data.OpenPostgres()
		
		except:
			print "I cannot connect to the supplied database"
			self.out.OutputError("Problem connecting to database %s." % self.dbname) 
			self._Data.ClosePostgres()
			sys.exit(1)

		# see what databases are actually on this server (ignoring template databases, and the postgis/postgres special ones)
		sSelSQL = "SELECT datname FROM pg_database WHERE datistemplate = 'f' AND datname NOT LIKE '%postgis%' AND datname NOT LIKE 'postgres'"
		q_sql = self._conn.query(sSelSQL)
		res= q_sql.getresult()

		# iterate through list of databases and run pg_dump with appropriate options
		for row in res:
			db = row[0]
			self.encodingcheck(db)
			self.dump_file = db +'_' + self.dateStr + '.backup'
			self.local_file = self.local_locn + self.dump_file
	
			try:
				cmd=self.pg_dump_path +' --host=%s --username=%s --port=%d -F c -b -C -c %s > %s' % (self.host, self.username, self.port, db, self.local_file)
				res = os.system(cmd)
				self.out.OutputInfo("PG_Dump ran successfully on %s." % db) 
			except:
				self.out.OutputError("Problem running PG_Dump on %s." % db) 
				self.email_subject = "Local Backup Failed"
				self.email_body = "The local backup of database %s failed on %s" % (db, self.dateStr)
				self.sendmail.sendEmail(email_subject, email_body)
				self._Data.ClosePostgres()
				sys.exit(1)
			finally:
				self.fileCopy(db)
		self._Data.ClosePostgres()
		return		
	


def main():

 	gothunderbirdsgo = databaseBackup()
	gothunderbirdsgo.backup()

if __name__ == "__main__":
    main()






		

