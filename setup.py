from distutils.core import setup
import py2exe

import modulefinder
modulefinder.AddPackagePath("mail.mime", "base")
modulefinder.AddPackagePath("mail.mime", "multipart")
modulefinder.AddPackagePath("mail.mime", "nonmultipart")
modulefinder.AddPackagePath("mail.mime", "audio")
modulefinder.AddPackagePath("mail.mime", "image")
modulefinder.AddPackagePath("mail.mime", "message")
modulefinder.AddPackagePath("mail.mime", "application")

setup(console=['database_backup.py'])
