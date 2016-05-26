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

if not os.path.isfile('debpackages.json'):
	print("ERROR: Not foud debpackages.json in current directory")
	sys.exit(-1)

if not os.path.exists('build'):
    os.makedirs('build')
	
## LOAD PACKAGES INFO
with open('debpackages.json') as data:
	debpackages = json.load(data)


for reponame in debpackages:
	repourl = debpackages[reponame];
	print(" * " + reponame)
	if not os.path.exists('build/' + reponame):
		print("\tStart clone from " + repourl + " ... ");
		os.popen("git clone " + repourl + " build/" + reponame).read()
		print(" OK ");
	else:
		print("\tStart update ... ");
		os.popen("cd build/" + reponame + " && git checkout  && git pull").read()
		print("\tOK ");
	
	
# TODO make different packages and package all-in-one

