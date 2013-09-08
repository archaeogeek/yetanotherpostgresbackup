yetanotherpostgresbackup
========================

Python script for backing up all postgresql databases on a server, moving them to a remote location, clearing up old files and emailing problems

Tested with python 2.6 but should/may work with 2.5+. Should work with windows and linux variants- not tested with Mac.

**Requirements**

  - Python 2.5+
  - PostgreSQL 8.x +
  - PygreSQL for your version of python- get it [here](http://www.pygresql.org/)
  
 **Instructions**

  - Edit the supplied config.ini.sample to match your database credentials (host, username, password, port, database name).  Note that you can choose any database on the server- it's just a way into the catalog. 
  - Choose a path on the local file system, and a remote file server (UNC file paths please) if required. If the remote location is not required, leave that option blank.
  - Fill in the path to pg_dump (linux) or pg_dump.exe (windows) for you postgresql installation.
  - Fill in the number of days you'd like old backups to be kept for- any older than this will be removed.
  - Choose a logging level from the options given.
  - If your server can send emails, fill in the SMTP server address, a sender and a recipient address- yetanotherdatabasebackup will use this to try and notify you of any problems with the backup.

**Usage**

    python databasebackup.py -f config.ini

**Caveats**

  This was done to scratch an itch and teach myself further python. As such it's fairly rudimentary! Given time I will improve the code and may add additional functionality as necessary. 
