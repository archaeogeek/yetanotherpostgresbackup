## Copyright (c) 2011 Astun Technology

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

### Cleanup.py - Class to clean up database backup files after a defined number of days

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
		






