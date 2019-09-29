#!/usr/bin/python3
# -*- coding: utf-8 -*-

import io
import re
from Utils import read_at, read_u8, read_u32, read_u64, memdump

class FsAccessControl:
	def __init__(self, fp):
		self.f = fp
		self._parse()

	def __str__(self):
		string = '    FS Access Control:\n'
		string += '      Version:            %d\n'    % self.version
		string += '      Permission bitmask: %016x\n' % self.permissions
		return string

	def _parse(self):
		self.version     = read_u8(self.f, 0x0)
		self.permissions = read_u64(self.f, 0x4)

class ServiceAccessControl:
	def __init__(self, fp):
		self.f = fp
		self._parse()

	def __str__(self):
		string = '    Service Access Control:\n'
		string += '      ' + '\n      '.join('%02x - %s' % (int.from_bytes(b, byteorder='little'), s) 
			for s, b in self.services.items()) + '\n'
		return string

	def _parse(self):
		serv = re.compile(b'([\x02-\x07])(([a-z0-9-]+:?)+)', re.I)
		self.services = {r[2].decode(): r[1] for r in re.finditer(serv, self.f.read())}

class KernelAccessControl:
	def __init__(self, fp):
		self.f = fp
		self._parse()

	def __str__(self):
		string = '    Kernel Access Control:\n'
		string += '      Placeholder\n'
		return string

	def _parse(self):
		# TODO
		pass

class ACID:
	def __init__(self, fp):
		self.f = fp
		self._parse()

	def __str__(self):
		string = '  ACID:\n'
		string += '    ACID flags:     %d\n'          % self.flags
		string += '    TitleID range:  %016x-%016x\n' % (self.tid_min, self.tid_max)
		string += memdump(self.rsa_sig, message='    RSA signature:  \n') + '\n'
		string += memdump(self.rsa_pubk, message='    RSA public key: \n') + '\n'
		string += '\n' + str(self.fs_access_control)
		string += '\n' + str(self.service_access_control)
		string += '\n' + str(self.kernel_access_control)
		return string

	def _parse(self):
		self.rsa_sig  = read_at(self.f, 0x0, 0x100)
		self.rsa_pubk = read_at(self.f, 0x100, 0x100)
		if read_at(self.f, 0x200, 0x4) != b'ACID':
			raise ValueError('Invalid ACID magic')
		self.flags   = read_u32(self.f, 0x20C)
		self.tid_min = read_u64(self.f, 0x210)
		self.tid_max = read_u64(self.f, 0x218)

		fs_access_control_offset      = read_u32(self.f, 0x220)
		fs_access_control_size        = read_u32(self.f, 0x224)
		service_access_control_offset = read_u32(self.f, 0x228)
		service_access_control_size   = read_u32(self.f, 0x22C)
		kernel_access_control_offset  = read_u32(self.f, 0x230)
		kernel_access_control_size    = read_u32(self.f, 0x234)

		self.fs_access_control      = FsAccessControl(io.BytesIO(read_at(self.f, 
			fs_access_control_offset, fs_access_control_size)))
		self.service_access_control = ServiceAccessControl(io.BytesIO(read_at(self.f, 
			service_access_control_offset, service_access_control_size)))
		self.kernel_access_control  = KernelAccessControl(io.BytesIO(read_at(self.f, 
			kernel_access_control_offset, kernel_access_control_size)))

class ACI0:
	def __init__(self, fp):
		self.f = fp
		self._parse()

	def __str__(self):
		string = '  ACI0:\n'
		string += '    TitleID: %016x\n' % self.tid
		string += '\n' + str(self.fs_access_control)
		string += '\n' + str(self.service_access_control)
		string += '\n' + str(self.kernel_access_control)
		return string

	def _parse(self):
		if read_at(self.f, 0x0, 0x4) != b'ACI0':
			raise ValueError('Invalid ACI0 magic')
		self.tid = read_u64(self.f, 0x10)

		fs_access_control_offset      = read_u32(self.f, 0x20)
		fs_access_control_size        = read_u32(self.f, 0x24)
		service_access_control_offset = read_u32(self.f, 0x28)
		service_access_control_size   = read_u32(self.f, 0x2C)
		kernel_access_control_offset  = read_u32(self.f, 0x30)
		kernel_access_control_size    = read_u32(self.f, 0x34)

		self.fs_access_control      = FsAccessControl(io.BytesIO(read_at(self.f, 
			fs_access_control_offset, fs_access_control_size)))
		self.service_access_control = ServiceAccessControl(io.BytesIO(read_at(self.f, 
			service_access_control_offset, service_access_control_size)))
		self.kernel_access_control  = KernelAccessControl(io.BytesIO(read_at(self.f, 
			kernel_access_control_offset, kernel_access_control_size)))

class NPDM:
	process_categories = {
		0: 'Regular title',
		1: 'Kernel built-in'
	}
	def __init__(self, fp):
		self.f = fp
		self._parse()

	def __str__(self):
		string = ''
		#string += 'NPDM:\n'
		string += '  Title name:                 %s\n'   % self.title_name
		string += '  Process category:           %s\n'   % self.process_category
		string += '  Product code:               %s\n'   % self.product_code
		string += '  MMU flags:                  %d\n'   % self.mmu_flags
		string += '  Main stack thread priority: %d\n'   % self.main_thread_priority
		string += '  Main thread stack size:     0x%x\n' % self.main_thread_stack_size
		string += '  Default CPU ID:             %d\n'   % self.default_cpu_id
		string += '  System resource size:       %d\n'   % self.resource_size 
		string += '\n'
		string += str(self.acid)
		string += '\n'
		string += str(self.aci0)
		return string
    
	def _parse(self):
		if read_at(self.f, 0x0, 0x4) != b'META':
			raise ValueError('Invalid META magic')
		self.mmu_flags              = read_u8(self.f, 0xC)
		self.main_thread_priority   = read_u8(self.f, 0xE)
		self.default_cpu_id         = read_u8(self.f, 0xF)
		self.resource_size          = read_u32(self.f, 0x14)
		self.process_category       = self.process_categories[read_u32(self.f, 0x18)]
		self.main_thread_stack_size = read_u32(self.f, 0x1C)
		self.title_name             = read_at(self.f, 0x20, 0x30).strip(b'\0').decode()
		self.product_code           = read_at(self.f, 0x30, 0x40).strip(b'\0').decode()
		if self.product_code=='':
			self.product_code=0
		
		aci0_offset = read_u32(self.f, 0x70)
		aci0_size   = read_u32(self.f, 0x74)
		acid_offset = read_u32(self.f, 0x78)
		acid_size   = read_u32(self.f, 0x7C)

		self.acid = ACID(io.BytesIO(read_at(self.f, acid_offset, acid_size)))
		self.aci0 = ACI0(io.BytesIO(read_at(self.f, aci0_offset, aci0_size)))
		
	def ret(self):
		aci0_offset = read_u32(self.f, 0x70)
		aci0_size   = read_u32(self.f, 0x74)
		acid_offset = read_u32(self.f, 0x78)
		acid_size   = read_u32(self.f, 0x7C)	
		return read_at(self.f, 0x0, acid_offset+acid_size)