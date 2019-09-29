#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os
import platform

class Server:
	def __init__(self):
		self.hostname = 'localhost'
		self.port = 9000

class Cdn:
	def __init__(self):
		self.region = 'US'
		self.firmware = '5.1.0-0'
		self.deviceId = '0000000000000000'
		self.environment = 'lp1'
		
class Paths:
	def __init__(self):
		self.titleBase = "titles/{name}[{id}][v{version}].nsp"
		self.titleDLC = "titles/DLC/{name}[{id}][v{version}].nsp"
		self.titleUpdate = "titles/updates/{name}[{id}][v{version}].nsp"
		self.titleDemo = "titles/demos/{name}[{id}][v{version}].nsp"
		self.titleDemoUpdate = "titles/demos/updates/{name}[{id}][v{version}].nsp"

		self.nsxTitleBase = None
		self.nsxTitleDLC = None
		self.nsxTitleUpdate = None
		self.nsxTitleDemo = None
		self.nsxTitleDemoUpdate = None

		self.scan = '.'
		self.titleDatabase = 'titledb'
		self.hactool = 'bin/hactool'
		self.keys = 'keys.txt'
		self.NXclientCert = 'nx_tls_client_cert.pem'
		self.shopNCert = 'ShopN.pem'
		self.nspOut = '_NSPOUT'
		self.titleImages = 'titles/images/'
		
		if platform.system() == 'Linux':
			self.hactool = './' + self.hactool + '_linux'

		if platform.system() == 'Darwin':
			self.hactool = './' + self.hactool + '_mac'
			
		self.hactool = os.path.normpath(self.hactool)

	def getTitleBase(self, nsx):
		if nsx:
			f = self.nsxTitleBase or self.titleBase
			f = os.path.splitext(f)[0] + '.nsx'
		else:
			f = self.titleBase
		return f

	def getTitleDLC(self, nsx):
		if nsx:
			f = self.nsxTitleDLC or self.titleDLC
			f = os.path.splitext(f)[0] + '.nsx'
		else:
			f = self.titleDLC
		return f

	def getTitleUpdate(self, nsx):
		if nsx:
			f = self.nsxTitleUpdate or self.titleUpdate
			f = os.path.splitext(f)[0] + '.nsx'
		else:
			f = self.titleUpdate
		return f

	def getTitleDemo(self, nsx):
		if nsx:
			f = self.nsxTitleDemo or self.titleDemo
			f = os.path.splitext(f)[0] + '.nsx'
		else:
			f = self.titleDemo
		return f

	def getTitleDemoUpdate(self, nsx):
		if nsx:
			f = self.nsxTitleDemoUpdate or self.titleDemoUpdate
			f = os.path.splitext(f)[0] + '.nsx'
		else:
			f = self.titleDemoUpdate
		return f
		
class Download:
	def __init(self):
		self.downloadBase = True
		self.demo = False
		self.DLC = True
		self.update = False
		self.sansTitleKey = False
		
cdn = Cdn()
paths = Paths()
download = Download()
server = Server()
threads = 4
jsonOutput = False
isRunning = True

titleUrls = []

def load(confFile):
	global threads
	global jsonOutput
	global titleUrls

	with open(confFile, encoding="utf8") as f:
		j = json.load(f)
	
		try:
			paths.titleBase = j['paths']['titleBase']
		except:
			pass
		
		try:
			paths.titleDLC = j['paths']['titleDLC']
		except:
			pass
		
		try:
			paths.titleUpdate = j['paths']['titleUpdate']
		except:
			pass
		
		try:
			paths.titleDemo = j['paths']['titleDemo']
		except:
			pass
		
		try:
			paths.titleDemoUpdate = j['paths']['titleDemoUpdate']
		except: 
			pass


		try:
			paths.nsxTitleBase = j['paths']['nsxTitleBase']
		except:
			pass
		
		try:
			paths.nsxTitleDLC = j['paths']['nsxTitleDLC']
		except:
			pass
		
		try:
			paths.nsxTitleUpdate = j['paths']['nsxTitleUpdate']
		except:
			pass
		
		try:
			paths.nsxTitleDemo = j['paths']['nsxTitleDemo']
		except:
			pass
		
		try:
			paths.nsxTitleDemoUpdate = j['paths']['nsxTitleDemoUpdate']
		except: 
			pass


	
		try:
			paths.scan = j['paths']['scan']
		except:
			pass

		try:
			paths.nspOut = j['paths']['nspOut']
		except:
			pass
		
		try:
			paths.titleDatabase = ['paths']['titledb']
		except:
			pass
	
		try:
			download.base = j['download']['base']
		except:
			pass
		
		try:
			download.demo = j['download']['demo']
		except:
			pass
		
		try:
			download.DLC = j['download']['dlc']
		except:
			pass
		
		try:
			download.update = j['download']['update']
		except:
			pass

		try:
			cdn.deviceId = j['cdn']['deviceId']
		except:
			pass

		try:
			cdn.region = j['cdn']['region']
		except:
			pass

		try:
			cdn.environment = j['cdn']['environment']
		except:
			pass

		try:
			cdn.firmware = j['cdn']['firmware']
		except:
			pass

		try:
			threads = int(j['download']['threads'])
		except:
			pass

		try:
			server.hostname = j['server']['hostname']
		except:
			pass

		try:
			server.port = int(j['server']['port'])
		except:
			pass
	
		try:
			for url in j['titleUrls']:
				if url not in titleUrls:
					titleUrls.append(url)
		except:
			pass
	
		try:
			download.sansTitleKey = j['download']['sansTitleKey']
		except:
			pass

if os.path.isfile('nut.conf'):
	os.rename('nut.conf', 'conf/nut.conf')


if os.path.isfile('conf/nut.default.conf'):
	load('conf/nut.default.conf')

if os.path.isfile('conf/nut.conf'):
	load('conf/nut.conf')


