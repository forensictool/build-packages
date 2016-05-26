#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# version of script: 22 May 2016

import sys
import os.path
import json
import string
from os import chmod
import shutil
import os.path
from pprint import pprint
import subprocess
import fileinput
import re
import datetime
import time

if not os.path.isfile('debpackage.json'):
	print("ERROR: Not foud debpackage.json in current directory")
	sys.exit(-1)

## LOAD PACKAGE INFO
with open('debpackage.json') as data:
	debpackage = json.load(data)

## REPLACE VERSION_BUILD IN PRO FILE
VERSION_BUILD = os.popen("git rev-list HEAD --count").read()
VERSION_BUILD = VERSION_BUILD.strip()
print("VERSION_BUILD: " + VERSION_BUILD)
debpackage['version']['build'] = VERSION_BUILD
with fileinput.FileInput(debpackage['project'], inplace=True) as f:
	for line in f:
		m = re.match(r"^[ ]*VERSION_BUILD[ ]*=[ ]*\d+[ ]*$", line)
		if m != None:
			print("VERSION_BUILD = " + VERSION_BUILD, end='\n');
		else:
			print(line, end='');

VERSION = debpackage['version']['major'] + '.' + debpackage['version']['minor'] + '.' + debpackage['version']['build']

## BUILD PROJECT
os.popen("rm -rf tmp && rm -rf bin && qmake & make").read()

## REMOVE DIST FOLDER
if os.path.exists('dist'):
	shutil.rmtree('dist')

if not os.path.exists('dist'):
    os.makedirs('dist')

# rm *.deb


print("Script for creating .deb package for " + debpackage['name'])

make_dirs = [
	'dist/debian/DEBIAN',
	'dist/debian/usr/lib',
	'dist/debian/usr/share/doc/' + debpackage['name'],
	'dist/debian/usr/share/man'
]

for sdir in make_dirs:
	if not os.path.exists(sdir):
		os.makedirs(sdir)

## COPY BINARY
os.popen("strip -S -o dist/debian/usr/lib/" + debpackage['lib'] + "." + VERSION + " bin/" + debpackage['lib'] + "." + VERSION).read()
os.popen("cd dist/debian/usr/lib/ && ln -s " + debpackage['lib'] + "." + VERSION + " " + debpackage['lib'] + '.' + debpackage['version']['major']).read()

## COPYRIGHT
with open('dist/debian/usr/share/doc/' + debpackage['name'] + '/copyright','w') as f:
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
with open('dist/debian/usr/share/doc/' + debpackage['name'] + '/README','w') as f:
	today = datetime.date.today()
	f.write("""Plugin detection os of Ubuntu for coex application.

Product: """ + debpackage['name'] + """
Version: """ + VERSION + """
Date: """ + time.strftime("%Y-%m-%d %H:%M") + """
Address: Russia, Tomsk, st. Lenina, 40
Organization: TUSUR
Author: Evgenii Sopov

Developers:
Evgenii Sopov (mrseakg@gamil.com)
""")

## THE CHNAGELOG FILE

with open('dist/debian/usr/share/doc/'  + debpackage['name'] + '/changelog','w') as f:
	today = datetime.date.today()
	f.write(debpackage['name'] + " (" + VERSION + "); urgency=low\n")
	f.write("\n")
	f.write(str(os.popen('git log --no-merges --format="  * %s" v' + debpackage['version']['major'] + '.' + debpackage['version']['minor']).read()))
	f.write("\n")
	f.write("-- " + debpackage['maintainer']['name'] + " " + debpackage['maintainer']['email'] + " " + time.strftime("%Y-%m-%d %H:%M") + "\n")

os.system("gzip -9 -n dist/debian/usr/share/doc/" + debpackage['name'] + "/changelog")


## THE CONTROL FILE
with open('dist/debian/DEBIAN/control','w') as f:
	today = datetime.date.today()
	f.write("""Package: """ + debpackage['name'] + """
Version: """ + VERSION + """
Section: admin
Priority: optional
Architecture: """ + debpackage['architecture'] + """
Depends: coex-core (= 0.1.0), libc6
Installed-Size: """ + os.popen("du -hks dist/debian/ | awk '{print $1}'").read().strip() + """
Maintainer: """ + debpackage['maintainer']['name'] + """ <""" + debpackage['maintainer']['email'] + """>
Description: """ + debpackage['description'] + "\n")

## POST INSTALL
with open('dist/debian/DEBIAN/postinst','w') as f:
	today = datetime.date.today()
	f.write("""#!/bin/sh -e

sudo ldconfig

exit 0
""")


## MD5SUM
os.system("cd dist/debian && find usr -type f | while read f; do md5sum \"$f\"; done > DEBIAN/md5sums")

## non-standard-dir-perm usr/ 0775 != 0755
os.system("chmod 0644 dist/debian/DEBIAN/control")
os.system("chmod 0644 dist/debian/DEBIAN/md5sums")

os.system("chmod 0755 dist/debian/DEBIAN/postinst")
os.system("chmod 0755 dist/debian/usr")
os.system("chmod 0755 -R dist/debian/usr/lib")
os.system("chmod 0644 dist/debian/usr/lib/" + debpackage['lib'] + "." + VERSION)
os.system("chmod 0755 dist/debian/usr/share")
os.system("chmod 0755 dist/debian/usr/share/doc")
os.system("chmod 0755 dist/debian/usr/share/doc/" + debpackage['name'])
os.system("chmod 0644 dist/debian/usr/share/doc/" + debpackage['name'] + '/copyright')
os.system("chmod 0644 dist/debian/usr/share/doc/" + debpackage['name'] + '/README')
os.system("chmod 0644 dist/debian/usr/share/doc/" + debpackage['name'] + '/changelog.gz')
os.system("chmod 0755 dist/debian/usr/share/man")

## MAKE PACKAGE
os.system("cd dist && fakeroot dpkg-deb --build ./debian " + debpackage['name'] + "-" + VERSION + ".deb")
os.system("lintian dist/*.deb > dist/lintian.log")


## The package assembly
# name="$papackage_name""_""$version""_""$platform.deb"
# echo $name

# mv debian.deb $name

# rm -r debian/

