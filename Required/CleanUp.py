# import modules
import os
import time
from datetime import date
import glob

# Import Astun stuff
import OutPut, ConfigParse

class ClassCleanUp:

	def __init__(self, Out):
		# get today's date
		now = date.today()
		self.dateStr = now.isoformat()

		# generic config
		opts = ConfigParse.OptParser()
		backupcreds = opts.ConfigSectionMap('BackupCreds')


		#Days to keep files for
		self.days = int(backupcreds['days'])

		#Output
		self.out = Out
		

	def OlderThan(self, days,ftime):
		"""Function for returning a date in the past given today's date and a number of days to go back by"""
		secondsinaday = 24 * 60 * 60
		try:
			return (ftime < (time.time() - days * secondsinaday))
		except:
			self.out.OutputError("Problem with 'olderthan' function.")
			
	def FileCleanup(self, dbf, location):
		"""Clean up files older than the defined number of days from the given location"""
		for f in glob.glob(location + dbf + '*.backup'):
			try:
				if self.OlderThan(self.days, os.stat(f).st_mtime):
					os.remove(f)
					self.out.OutputInfo("Removed old file %s." % f) 
				else:
					self.out.OutputInfo("No old files to remove.")
			except:
				self.out.OutputError("Problem with the 'file_cleanup' function. Backup aborted.")
				sys.exit(1)
		






