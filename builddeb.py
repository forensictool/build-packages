#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# version of script: 22 May 2016

import sys
sys.path.append('./libs/')

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
from DebPackage import DebPackage

if not os.path.isfile('debpackages.json'):
	print("ERROR: Not foud debpackages.json in current directory")
	sys.exit(-1)

inputfolder = 'repositories'

if not os.path.exists(inputfolder):
    os.makedirs(inputfolder)
if not os.path.exists('output'):
    os.makedirs('output')
    	
## LOAD PACKAGES INFO
with open('debpackages.json') as data:
	jsond = json.load(data)

debpackages = jsond['build']

for item in debpackages:
	buildtype = item['type'];
	if buildtype == "git":
		foldername = item['name']
		repourl = item['url']
		print(" * " + foldername)
		if not os.path.exists(inputfolder + '/' + foldername):
			print("\tStart clone from " + repourl + " ... ");
			os.popen("git clone " + repourl + " " + inputfolder + "/" + foldername).read()
			print(" OK ");
		else:
			print("\tStart update ... ");
			os.popen("cd " + inputfolder + "/" + foldername + " && git checkout  && git pull").read()
			print("\tOK ");
		with DebPackage("./" + inputfolder + "/" + foldername, 'output') as debpackage:
			debpackage.make();


# TODO make different packages and package all-in-one

