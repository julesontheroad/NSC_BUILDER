#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import Fs
import pathlib
import re
import Status
import time
import Print
import threading
import json

global files
files = {}

global lock
lock = threading.Lock()

global hasScanned
global hasLoaded
hasScanned = False
hasLoaded = False

def get(key):
	return files[key]

def getByTitleId(id):
	for k,f in files.items():
		if f.titleId == id:
			return f
	return None
	
def scan(base):
	global hasScanned
	if hasScanned:
		return

	hasScanned = True
	i = 0

	fileList = {}

	Print.info(base)
	for root, dirs, _files in os.walk(base, topdown=False):
		for name in _files:
			if pathlib.Path(name).suffix == '.nsp' or pathlib.Path(name).suffix == '.nsx':
				path = os.path.abspath(root + '/' + name)
				fileList[path] = name

	status = Status.create(len(fileList), desc = 'Scanning files...')

	try:
		for path, name in fileList.items():
			try:
				status.add(1)

				if not path in files:
					Print.info('scanning ' + name)
					nsp = Fs.Nsp(path, None)
						
					files[nsp.path] = nsp
					#files[nsp.path].readMeta()

					i = i + 1
					if i % 20 == 0:
						save()
			except KeyboardInterrupt:
				status.close()
				raise
			except BaseException as e:
				Print.info('An error occurred processing file: ' + str(e))
				status.close()
		save()
		status.close()
	except BaseException as e:
		Print.info('An error occurred scanning files: ' + str(e))

def removeEmptyDir(path, removeRoot=True):
	if not os.path.isdir(path):
		return

	# remove empty subfolders
	_files = os.listdir(path)
	if len(_files):
		for f in _files:
			if not f.startswith('.') and not f.startswith('_'):
				fullpath = os.path.join(path, f)
				if os.path.isdir(fullpath):
					removeEmptyDir(fullpath)

	# if folder empty, delete it
	_files = os.listdir(path)
	if len(_files) == 0 and removeRoot:
		Print.info("Removing empty folder:" + path)
		os.rmdir(path)

def load(fileName = 'titledb/files.json'):
	global hasLoaded

	if hasLoaded:
		return

	hasLoaded = True

	try:
		timestamp = time.clock()

		if os.path.isfile(fileName):
			with open(fileName, encoding="utf-8-sig") as f:
				for k in json.loads(f.read()):
					t = Fs.Nsp(k['path'], None)
					t.timestamp = k['timestamp']
					t.titleId = k['titleId']
					t.version = k['version']

					if not t.path:
						continue

					path = os.path.abspath(t.path)
					if os.path.isfile(path): 
						files[path] = t #Fs.Nsp(path, None)
	except:
		raise
	Print.info('loaded file list in ' + str(time.clock() - timestamp) + ' seconds')

def save(fileName = 'titledb/files.json', map = ['id', 'path', 'version', 'timestamp', 'hasValidTicket']):
	lock.acquire()

	try:
		j = []
		for i,k in files.items():
			j.append(k.dict())
		with open(fileName, 'w') as outfile:
			json.dump(j, outfile, indent=4, sort_keys=True)
	except:
		lock.release()
		raise
	lock.release()

if os.path.isfile('files.json'):
	os.rename('files.json', 'titledb/files.json')