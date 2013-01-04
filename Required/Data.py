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

### Data.py - Class to manage connections to a database, plus generic utility
### functions for working with data in postgresql

###
import os
import sys
import pg
import csv

# Import Astun stuff
import OutPut, ConfigParse


class ClassData:

    conn1 = 0

    def __init__(self, Out):
        opts = ConfigParse.ConfParser()
        dbcreds = opts.ConfigSectionMap('DatabaseConnection')

        self.dbname = dbcreds['dbname']
        self.host = dbcreds['host']
        self.username = dbcreds['username']
        self.password = dbcreds['password']
        self.port = int(dbcreds['port'])

        self._conn = 0
        self._output = Out
        self._bError = False

        #Output to log file
        self.out = OutPut.ClassOutput('Sparql Downloader')

    #####
    # Open connection to postgres
    ###

    def OpenPostgres(self):

        ## To ensure we have a connection
        if (self._conn == 0):
            self._output.OutputInfo('Opening PostgreSQL connection')

        try:
            # Get the config settings
            sHost = self.host
            sDatabase = self.dbname
            sUser = self.username
            sPwd = self.password
            sPort = self.port

            # Now connect
            self._conn = pg.connect(host=sHost, user=sUser, dbname=sDatabase, passwd=sPwd, port= sPort)

        except KeyboardInterrupt:
            self._output.OutputError('Keyboard interrupt detected', False)
            raise

        except:
            self._output.OutputError('On connecting to Postgres DB', True)
            self._output.OutputException(sys.exc_info(), True)
            self._bError = True

        return self._conn

    #####

    #####
    # Close a connection
    ###

    def ClosePostgres(self):
        # Close the connection
        if self._conn != 0:
            self._output.OutputInfo('Closing PostgreSQL connection')

        try:
            self._conn.close()

        except KeyboardInterrupt:
            self._output.OutputError('Keyboard interrupt detected', False)
            raise

        except:
            self._output.OutputError('On closing PostgresSQL connection', True)
            self._output.OutputException(sys.exc_info(), True)
            self._conn = 0

        return
        #####

    def DoesTableExist(self, table):
        '''generic function to check if a table exists or not'''
        sSQL = "SELECT relname from pg_class WHERE relname = '%s'" % table
        q = self._conn.query(sSQL)
        return q.getresult()

    def DoesColumnExist(self, table, column):
        ''' generic function to check if a given column exists in a given
        table, if it does, then do nothing, if it doesn't then add it'''
        sSQL = "SELECT attname FROM pg_attribute WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = '%s') AND attname = '%s'" % (table, column)
        q = self._conn.query(sSQL)
        if q.getresult():
            pass
        else:
            sSQL2 = "ALTER TABLE %s ADD COLUMN %s varchar" % (table, column)
            self._conn.query(sSQL2)

    def DropTable(self, tablename):
        ''' generic function for dropping a database table called [tablename]'''
        res = self.DoesTableExist(tablename)
        if res:
            sDropSQL = 'DROP TABLE %s' % tablename
            try:
                self._conn.query(sDropSQL)
            except:
                self.out.OutputError("There was a problem dropping table %s." % tablename)
        else:
            pass  #if it doesn't exist we don't need to drop it

    def AlterTable(self, tablename):
        '''generic function for creating a backup version of a table called
        [tablename] to tablename_PREV'''

        res = self.DoesTableExist(tablename)
        if not res:
            self.out.OutputInfo("No previous version of %s exists." % tablename)
        else:
            sAlterSQL = "ALTER TABLE %s RENAME TO %s_prev" % (tablename, tablename)
            try:
                self.DropTable('%s_prev' % tablename)
                self._conn.query(sAlterSQL)
            except:
                self.out.OutputError("Could not rename %s" % tablename)

    def CreateTable(self, tablename, fields):
        '''generic function for creating a database table called [tablename],
        if passed a list of fields.'''

        self.AlterTable(tablename)
        self.DropTable('%s_prev' % tablename)

        fieldslist = ",".join([' %s %s' % (key, value) for key, value in fields.items()])
        try:
            sCreateSQL = 'CREATE TABLE %s (%s)' % (tablename, fieldslist)
            self._conn.query(sCreateSQL)
            self.out.OutputInfo("Table %s created." % tablename)
        except:
            self.out.OutputError("Could not create %s. Script aborting" % tablename)

    def DeleteRows(self, tablename, column, value):
        ''' generic function for deleting rows from [tablename] where [column]
        = [value]'''
        try:
            sDelSQL = "DELETE FROM %s WHERE %s = '%s'" % (tablename, column, value)
            self._conn.query(sDelSQL)
        except:
            self.out.OutputError("Could not delete from %s where % = %" % (tablename, column, value))

    def InsertTable(self, dbdata, table):
        ''' generic function for inserting the values from a dictionary of data
        [dbdata] into a database table [table]'''
        fvals = ', '.join(dbdata.values())
        fkeys = ', '.join(dbdata.keys())

        sInsertSQL = "INSERT INTO %s (%s) VALUES (%s)" % (table, fkeys, fvals)
        try:
            self._conn.query(sInsertSQL.encode('utf8'))
        except:
            pass  #fail silently and move on so that we continue the script

    def getDBInfo(self, fields='id, force', table='policeapi_neighbourhoods'):
        '''generic function for getting id and force information from db for
        creating download url'''

        try:
            sselSQL = 'SELECT %s FROM %s' % (fields, table)
            q_sql = self._conn.query(sselSQL)
        except:
            self.out.OutputError("Cannot access %s" % table)

        res = q_sql.dictresult()
        return res

    def processCSV(self, filename, table, loopNumber):
        '''generic function for processing csv files and copying into given
        table'''
        csvfile = open(filename)
        #parse first line to get column headings- need to wrap them in quotes
        #to preserve spaces and case
        header = {}
        content = {}
        reader = csv.DictReader(csvfile)
        for row in reader:
            if loopNumber == 0:
                for f in row.keys():
                    f = '"' + f + '"'
                    header[f] = 'varchar'
                self.CreateTable(table, header)
                loopNumber +=1
            for key, value in row.items():
                key = '"' + key + '"'
                value = "'" + value + "'"
                content[key] = value
            try:
                self.InsertTable(content, table)
            except:
                e = sys.exc_info()[1]
                print "Error: %s" % e
        csvfile.close()

    def AddGeometryColumn(self, table, geomtype):
        '''generic function to add geometry column in EPSG:27700 format to a
        given table'''
        try:
            sGeomSQL = "select AddGeometryColumn('%s', 'wkb_geometry', 27700, '%s', 2)" % (table, geomtype)
            self._conn.query(sGeomSQL)
            self.out.OutputInfo("Geometry Column successfully added to %s table" % table)
        except:
            self.out.OutputInfo("Could not add geometry column to %s" % table)
            e = sys.exc_info()[1]
            print "Error: %s" % e