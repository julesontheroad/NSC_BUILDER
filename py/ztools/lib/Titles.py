#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import re
import time
import json
import Title
import operator
import Config
import Print
import threading

global titles
titles = {}

if os.path.isfile('titles.json'):
	os.rename('titles.json', 'titledb/titles.json')

def data():
	return titles

def items():
	return titles.items()

def get(key):
	return titles[key]
	
def contains(key):
	return key in titles
	
def set(key, value):
	titles[key] = value
	
#def titles():
#	return titles
	
def keys():
	return titles.keys()
	
def loadTitleFile(path, silent = False):
	timestamp = time.clock()
	with open(path, encoding="utf-8-sig") as f:
		loadTitleBuffer(f.read(), silent)
	Print.info('loaded ' + path + ' in ' + str(time.clock() - timestamp) + ' seconds')
	
def loadTitleBuffer(buffer, silent = False):
	firstLine = True
	map = ['id', 'key', 'name']
	for line in buffer.split('\n'):
		line = line.strip()
		if len(line) == 0 or line[0] == '#':
			continue
		if firstLine:
			firstLine = False
			if re.match('[A-Za-z\|\s]+', line, re.I):
				map = line.split('|')
				
				i = 0
				while i < len(map):
					if map[i] == 'RightsID':
						map[i] = 'id'
					if map[i] == 'TitleKey':
						map[i] = 'key'
					if map[i] == 'Name':
						map[i] = 'name'
					i += 1
				continue
		
		t = Title.Title()
		t.loadCsv(line, map)

		if not t.id in keys():
			titles[t.id] = Title.Title()
			
		titleKey = titles[t.id].key
		titles[t.id].loadCsv(line, map)

		if not silent and titleKey != titles[t.id].key:
			Print.info('Added new title key for ' + str(titles[t.id].name) + '[' + str(t.id) + ']')

confLock = threading.Lock()	
def load():
	confLock.acquire()
	global titles
	if os.path.isfile("titledb/titles.json"):
		timestamp = time.clock()
		with open('titledb/titles.json', encoding="utf-8-sig") as f:
			for i, k in json.loads(f.read()).items():
				#if k['frontBoxArt'] and k['frontBoxArt'].endswith('.jpg'):
				#	k['iconUrl'] = k['frontBoxArt']
				#	k['frontBoxArt'] = None
				titles[i] = Title.Title()
				titles[i].__dict__ = k

		Print.info('loaded titledb/titles.json in ' + str(time.clock() - timestamp) + ' seconds')

	if os.path.isfile("titles.txt"):
		loadTitleFile('titles.txt', True)

	try:
		files = [f for f in os.listdir(Config.paths.titleDatabase) if f.endswith('.txt')]
		files.sort()
	
		for file in files:
			loadTitleFile(Config.paths.titleDatabase + '/' + file, False)
	except BaseException as e:
		Print.error('title load error: ' + str(e))
	confLock.release()

	
def export(fileName = 'titles.txt', map = ['id', 'rightsId', 'key', 'isUpdate', 'isDLC', 'isDemo', 'name', 'version', 'region', 'retailOnly']):
	buffer = ''
	
	buffer += '|'.join(map) + '\n'
	for t in sorted(list(titles.values())):
		buffer += t.serialize(map) + '\n'
		
	with open(fileName, 'w', encoding='utf-8') as csv:
		csv.write(buffer)

def save(fileName = 'titledb/titles.json'):
	confLock.acquire()
	try:
		j = {}
		for i,k in titles.items():
			if not k.id or k.id == '0000000000000000':
				continue
			if k.description:
				k.description = k.description.strip()
			j[k.id] = k.__dict__
		with open(fileName, 'w') as outfile:
			json.dump(j, outfile, indent=4)
	except:
		confLock.release()
		raise

	confLock.release()

class Queue:
	def __init__(self):
		self.queue = []
		self.lock = threading.Lock()
		self.i = 0

	def add(self, id, skipCheck = False):
		self.lock.acquire()
		id = id.upper()
		if not id in self.queue and (skipCheck or self.isValid(id)):
			self.queue.append(id)
		self.lock.release()

	def shift(self):
		self.lock.acquire()
		if self.i >= len(self.queue):
			self.lock.release()
			return None

		self.i += 1

		r =self.queue[self.i-1]
		self.lock.release()
		return r

	def empty(self):
		return bool(self.size() == 0)

	def get(self, idx = None):
		if idx == None:
			return self.queue
		return self.queue[idx]

	def isValid(self, id):
		return contains(id)

	def load(self):
		try:
			with open('conf/queue.txt', encoding="utf-8-sig") as f:
				for line in f.read().split('\n'):
					self.add(line.strip())
		except BaseException as e:
			pass

	def size(self):
		return len(self.queue) - self.i

	def save(self):
		self.lock.acquire()
		try:
			with open('conf/queue.txt', 'w', encoding='utf-8') as f:
				for id in self.queue:
					f.write(id + '\n')
		except:
			pass
		self.lock.release()

global queue
queue = Queue()