# import modules
import ConfigParser
from optparse import OptionParser

class OptParser():

	def __init__(self):
		parser=OptionParser()
		parser.add_option("-f","--file", dest="filename")
		(options, args) = parser.parse_args()
		self.options = options

	def ConfigSectionMap(self, section):
		"""Generic function for parsing options in a config file and returning a dictionary of the results"""

   		file_name = self.options.filename
		
		
		Config = ConfigParser.ConfigParser()
		Config.read(file_name)
		dict1 = {}
    		options = Config.options(section)
    		for option in options:
        		try:
           			dict1[option] = Config.get(section, option)
            			if dict1[option] == -1:
                			DebugPrint("skip: %s" % option)
        		except:
           			print("exception on %s!" % option)
            			dict1[option] = None    
 
		return dict1






