#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, json, fileinput, re, shutil, time, datetime, platform

class DebPackage:
	def __init__(self, packagefolder, outputfolder):
		self.packagefolder = packagefolder;
		self.outputfolder = outputfolder;
	def __enter__(self):
		return self
	def __exit__(self, exc_type, exc_value, traceback):
		print(" -> Remove tmp folder")
		# self.rmTmp()
	def check(self):
		print("Test")
	def parseVersion(self):
		self.version_major = 0;
		self.version_minor = 0;
		self.version_build = 0;
		## VERSION parse file version.pri
		with fileinput.FileInput(self.packagefolder + '/version.pri', inplace=False) as f:
			for line in f:
				version_major = re.match(r"^[ ]*VERSION_MAJOR[ ]*=[ ]*(\d+)[ ]*$", line)
				if version_major != None:
					self.version_major = version_major.group(1)
				version_minor = re.match(r"^[ ]*VERSION_MINOR[ ]*=[ ]*(\d+)[ ]*$", line)
				if version_minor != None:
					self.version_minor = version_minor.group(1)
				version_build = re.match(r"^[ ]*VERSION_BUILD[ ]*=[ ]*(\d+)[ ]*$", line)
				if version_build != None:
					self.version_build = version_build.group(1)
		self.version = self.version_major + "." + self.version_minor + "." + self.version_build
		print(" -> Package version: " + self.version)

	def findArchitecture(self):
		self.architecture = "unknown"
		if platform.machine() == "x86_64":
			self.architecture = "amd64"
		elif platform.machine() == "x86":
			self.architecture = "i686"
		print(" -> Package architecture: " + self.architecture)
		if self.architecture == "unknown":
			sys.exit(-2)
	def buildapp(self, item):
		buildtype = item['type']
		print(" -> Build " + buildtype)
		self.rmTmp();
		self.makeTmpDirs('bin', item['name']);
		self.makeProject(item['project'])
		self.writeCopyright(item)
		self.writeReadme(item)
		self.writeChangeLog(item)
		self.writeControlFile(item)
		self.writePostInstall(item)
		self.writeMd5Sum(item)
		self.copyBinaryApp(item)
		self.fixCHMOD(item)
		self.makePackage(item)

	def buildlib(self, item):
		buildtype = item['type']
		print(" -> Build " + buildtype)
	
	def buildappui(self, item):
		buildtype = item['type']
		print(" -> Build " + buildtype)
	
	def make(self):
		print(" -> Build package " + self.packagefolder)
		if not os.path.isfile(self.packagefolder + '/debpackage.json'):
			print("ERROR: Not foud debpackage.json")
			sys.exit(-1)

		## LOAD PACKAGES INFO
		with open(self.packagefolder + '/debpackage.json') as data:
			self.json = json.load(data)
		self.build = self.json['build']
		self.maintainer = self.json['maintainer']
		self.repository = self.json['repository']
		self.parseVersion();
		self.findArchitecture();
		for item in self.build:
			if item['type'] == 'app':
				self.buildapp(item)
				sys.exit(0)
			elif item['type'] == 'lib':
				self.buildlib(item)
			elif item['type'] == 'app-ui':
				self.buildlib(item)
			else:
				print(" -> Failed build: unknown type")

	def rmTmp(self):
		if os.path.exists('tmp'):
			shutil.rmtree('tmp')

	def makeTmpDirs(self, foldertype, packagename):
		if not os.path.exists('tmp'):
			os.makedirs('tmp')
		make_dirs = [
			'tmp/debian/DEBIAN',
			'tmp/debian/usr/' + foldertype,
			'tmp/debian/usr/share/man'
		]
		for sdir in make_dirs:
			if not os.path.exists(sdir):
				os.makedirs(sdir)

	def makeProject(self, projectname):
		## BUILD PROJECT
		os.popen("cd " + self.packagefolder + " && rm -rf tmp && rm -rf bin && qmake " + projectname + " && make").read()

	## COPYRIGHT
	def writeCopyright(self, item):
		dirpath = 'tmp/debian/usr/share/doc/' + item['name']
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)
		with open(dirpath + '/copyright','w') as f:
			f.write("""The MIT License (MIT)

Copyright (c) 2016 COEX
 
Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the \"Software\"), to deal in
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions: 
The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software. 
THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.""")

	## THE README FILE
	def writeReadme(self, item):
		dirpath = 'tmp/debian/usr/share/doc/' + item['name']
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)
		with open(dirpath + '/README','w') as f:
			today = datetime.date.today()
			f.write("""Plugin detection os of Ubuntu for coex application.

Product: """ + item['name'] + """
Version: """ + self.version + """
Date: """ + time.strftime("%Y-%m-%d %H:%M") + """
Address: Russia, Tomsk, st. Lenina, 40
Organization: TUSUR
Author: Coex Group

Developers:
Evgenii Sopov (mrseakg@gamil.com)
""")

	## THE CHNAGELOG FILE
	def writeChangeLog(self, item):
		dirpath = 'tmp/debian/usr/share/doc/' + item['name']
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)
		with open(dirpath + '/changelog','w') as f:
			today = datetime.date.today()
			f.write(item['name'] + " (" + self.version + "); urgency=low\n")
			f.write("\n")
			f.write(str(os.popen('git log --no-merges --format="  * %s" v' + self.version).read()))
			f.write("\n")
			f.write("-- " + self.maintainer['name'] + " " + self.maintainer['email'] + " " + time.strftime("%Y-%m-%d %H:%M") + "\n")
		os.system("gzip -9 -n tmp/debian/usr/share/doc/" + item['name'] + "/changelog")

	## THE CONTROL FILE
	## TODO Depends: libc6
	def writeControlFile(self, item):
		with open('tmp/debian/DEBIAN/control','w') as f:
			today = datetime.date.today()
			f.write("""Package: """ + item['name'] + """
Version: """ + self.version + """
Section: admin
Priority: optional
Architecture: """ + self.architecture + """
Depends: libc6
Installed-Size: """ + os.popen("du -hks tmp/debian/ | awk '{print $1}'").read().strip() + """
Maintainer: """ + self.maintainer['name'] + """ <""" + self.maintainer['email'] + """>
Description: """ + item['description'] + "\n")

	## POST INSTALL
	def writePostInstall(self, item):
		with open('tmp/debian/DEBIAN/postinst','w') as f:
			today = datetime.date.today()
			f.write("""#!/bin/sh -e

sudo ldconfig

exit 0
""")

	## MD5SUM
	def writeMd5Sum(self, item):
		os.system("cd tmp/debian && find usr -type f | while read f; do md5sum \"$f\"; done > DEBIAN/md5sums")

	## COPY BINARY APP
	def copyBinaryApp(self, item):
		os.popen("strip -S -o tmp/debian/usr/bin/" + item['name'] + " " + self.packagefolder + "/bin/" + item['name']).read()
		os.system("chmod 0644 tmp/debian/usr/bin/" + item['name'])

	## COPY BINARY LIB
	def copyBinaryLib(self, item):
		## COPY BINARY
		os.popen("strip -S -o dist/debian/usr/lib/" + debpackage['lib'] + "." + VERSION + " bin/" + debpackage['lib'] + "." + VERSION).read()
		os.popen("cd tmp/debian/usr/lib/ && ln -s " + debpackage['lib'] + "." + VERSION + " " + debpackage['lib'] + '.' + debpackage['version']['major']).read()

	def fixCHMOD(self, item):
		## non-standard-dir-perm usr/ 0775 != 0755
		os.system("chmod 0644 tmp/debian/DEBIAN/control")
		os.system("chmod 0644 tmp/debian/DEBIAN/md5sums")

		os.system("chmod 0755 tmp/debian/DEBIAN/postinst")
		os.system("chmod 0755 tmp/debian/usr")
		os.system("chmod 0755 -R tmp/debian/usr/bin")
		
		os.system("chmod 0755 tmp/debian/usr/share")
		os.system("chmod 0755 tmp/debian/usr/share/doc")
		os.system("chmod 0755 tmp/debian/usr/share/doc/" + item['name'])
		os.system("chmod 0644 tmp/debian/usr/share/doc/" + item['name'] + '/copyright')
		os.system("chmod 0644 tmp/debian/usr/share/doc/" + item['name'] + '/README')
		os.system("chmod 0644 tmp/debian/usr/share/doc/" + item['name'] + '/changelog.gz')
		os.system("chmod 0755 tmp/debian/usr/share/man")

	## MAKE PACKAGE
	def makePackage(self, item):
		basename = self.outputfolder + "/" + item['name'] + "-" + self.version + "_" + self.architecture;
		debname = basename + ".deb";
		lintianlog = basename + "-lintian.log";
		os.system("cd tmp && fakeroot dpkg-deb --build ./debian ../" + debname)
		os.system("lintian " + debname + " > " + lintianlog)
