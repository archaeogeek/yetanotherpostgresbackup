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

### database_backup.py - Script to back up postgresql databases on a server,
### to a local or remote location, and clean up after a defined number of days

# import modules
import os, sys, shutil, subprocess
from datetime import date
from optparse import OptionParser

#astun
from Required import ConfigParse, Email, OutPut, Data, CleanUp


class databaseBackup():

    def __init__(self):
        desc = """Back up all databases on a definted host and port to defined
        local and/or remote locations.
        Email comments if backup fails, and remove old backups after a defined
        number of days.
        Usage: database_backup.py -f filename"""
        parser = OptionParser(description=desc)
        parser.add_option("-f", "--file", dest="filename")
        (options, args) = parser.parse_args()
        self.options = options
        self.filename = options.filename

        # get today's date
        now = date.today()
        self.dateStr = now.isoformat()

        # generic config
        opts = ConfigParse.ConfParser(filename=self.filename)
        dbcreds = opts.ConfigSectionMap(filename=self.filename, section='DatabaseConnection')
        backupcreds = opts.ConfigSectionMap(filename=self.filename, section='BackupCreds')

        #Backup
        self.pg_dump_path = backupcreds['pg_dump_path']
        self.remote_locn = backupcreds['remote_locn']
        self.local_locn = backupcreds['local_locn']

        #Output to log file
        outputcreds = opts.ConfigSectionMap(filename= self.filename, section='Output')
        self.outputlevel = outputcreds['outputlevel']
        self.out = OutPut.ClassOutput('Dbf_BU')

        #Cleanup
        self.cleanup = CleanUp.ClassCleanUp(self.out, self.filename)

        #Email
        self.sendmail = Email.sendEmail(self.out, self.filename)

        #Database Connection
        self._Data = Data.ClassData(self.out, self.filename)
        self.host = dbcreds['host']
        self.username = dbcreds['username']
        self.password = dbcreds['password']
        self.port = int(dbcreds['port'])

    def ExtraErrorHandling(self):
        '''generic function for printing error message before exiting script'''
        e = sys.exc_info()[1]
        print "Error: %s" % e
        sys.exit(1)

    def fileCopy(self, dbf):
        """If a remote location is defined, copy the dump file there and delete
         the local copy"""
        if self.remote_locn:
            self.remote_file = self.remote_locn + self.dump_file

            try:
                shutil.copy(self.local_file, self.remote_file)
                os.remove(self.local_file)
                self.out.OutputInfo("Successfully copied %s to remote location %s." % (self.local_file, self.remote_locn))
                self.out.OutputInfo("Remote backup of database %s succeeded on %s." % (dbf, self.dateStr))
                self.cleanup.FileCleanup(dbf, self.remote_locn)
            except:
                self.out.OutputError("Could not copy file %s to remote location %s." % (self.local_file, self.remote_locn))
                email_subject = "Remote Backup Failed"
                email_body = "The remote backup of database %s failed on %s" % (dbf, self.dateStr)
                self.sendmail.sendEmail(email_subject, email_body)
                sys.exit(1)
        else:
            self.cleanup.FileCleanup(dbf, self.local_locn)

    def encodingcheck(self, dbf):
        """check the client encoding and the database encoding, and flag up if
         is a mismatch between the two that might cause the backup to fail"""

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
        if self.outputlevel == 'INFO':
            self.out.SetOutputLevel(OutPut.OUTPUTLEVEL_INFO)
        elif self.outputlevel == 'ERROR':
            self.out.SetOutputLevel(OutPut.OUTPUTLEVEL_ERROR)
        else:
            self.out.SetOutputLevel(OutPut.OUTPUTLEVEL_DEBUG)
        self.out.SetFileLogging(True)
        self.out.OutputInfo('___________________________')
        self.out.OutputInfo('Database Backup starting')

        try:
            self._conn = self._Data.OpenPostgres()
            # see what databases are actually on this server (ignoring
            # databases, and the postgis/postgres special ones)
            sSelSQL = "SELECT datname FROM pg_database WHERE datistemplate = 'f' AND (datname NOT LIKE '%postgis%' OR datname NOT LIKE 'postgres' OR datname NOT LIKE 'template%')"
            q_sql = self._conn.query(sSelSQL)
            res = q_sql.getresult()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.out.OutputError("Problem connecting with the given credentials. See error log for details. Backup aborting.")
            sys.exit(1)

        #set the PGPASSWORD environment variable
        os.putenv('PGPASSWORD', self.password)

        # iterate through list of databases and run pg_dump with appropriate
        # options
        try:
            for row in res:
                db = row[0]
                self.encodingcheck(db)
                self.dump_file = db + '_' + self.dateStr + '.backup'
                self.local_file = self.local_locn + self.dump_file
                dbnostr = db.replace(' ', '_', 1)
                self.dump_file = dbnostr + '_' + self.dateStr + '.backup'

                cmd=self.pg_dump_path +' --host=%s --username=%s --port=%d -F c -b -C -c %s > %s' % (self.host, self.username, self.port, db, self.local_file)
                try:
                    self.out.OutputInfo("Backing up database %s" % db)
                    res = subprocess.call(cmd, shell=True)
                    self.out.OutputInfo("PG_Dump ran successfully on %s." % db)
                except (KeyboardInterrupt, SystemExit):
                    self.out.OutputError("Keyboard interrupt detected. Script aborting")
                    raise
                except:  # this needs to deal with when the pg_dump command
                # asks for a password because there's no appropriate pgpass file
                # otherwise it doesn't time out or anything helpful
                    self.out.OutputError("Problem running PG_Dump on %s." % db)
                    self.email_subject = "Local Backup Failed"
                    self.email_body = "The local backup of database %s failed on %s" % (db, self.dateStr)
                    self.sendmail.sendEmail(self.email_subject, self.email_body)
                    self._Data.ClosePostgres()
                    sys.exit(1)
                finally:
                    self.fileCopy(db)
            self._Data.ClosePostgres()
            return
        except (KeyboardInterrupt, SystemExit):
                raise


def main():
    try:
        gothunderbirdsgo = databaseBackup()
        gothunderbirdsgo.backup()
    except (KeyboardInterrupt, SystemExit):
        raise

if __name__ == "__main__":

    main()









