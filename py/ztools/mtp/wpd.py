"""A wrapper to use the Windows Portable Device Api (WPD)"""

import comtypes
from comtypes import GUID
from comtypes.automation import *
from comtypes.client import *
from ctypes import *
import re
from collections import namedtuple
import struct
import binascii
import struct

def parse32le(data):
 return struct.unpack('<I', data)[0]

def dump32le(value):
 return struct.pack('<I', value)

def parse32be(data):
 return struct.unpack('>I', data)[0]

def dump32be(value):
 return struct.pack('>I', value)

def parse16le(data):
 return struct.unpack('<H', data)[0]

def dump16le(value):
 return struct.pack('<H', value)

def parse16be(data):
 return struct.unpack('>H', data)[0]

def dump16be(value):
 return struct.pack('>H', value)

def parse8(data):
 return struct.unpack('B', data)[0]

def dump8(value):
 return struct.pack('B', value)

class Struct(object):
 LITTLE_ENDIAN = '<'
 BIG_ENDIAN = '>'
 PADDING = '%dx'
 CHAR = 'c'
 STR = '%ds'
 INT64 = 'Q'
 INT32 = 'I'
 INT16 = 'H'
 INT8 = 'B'

 def __init__(self, name, fields, byteorder=LITTLE_ENDIAN):
  self.tuple = namedtuple(name, (n for n, fmt in fields if not isinstance(fmt, int)))
  self.format = byteorder + ''.join(self.PADDING % fmt if isinstance(fmt, int) else fmt for n, fmt in fields)
  self.size = struct.calcsize(self.format)

 def unpack(self, data, offset = 0):
  return self.tuple(*struct.unpack_from(self.format, data, offset))

 def pack(self, **kwargs):
  return struct.pack(self.format, *self.tuple(**kwargs))


UsbDevice = namedtuple('UsbDevice', 'handle, idVendor, idProduct')
MtpDeviceInfo = namedtuple('MtpDeviceInfo', 'manufacturer, model, serialNumber, operationsSupported, vendorExtension')
USB_CLASS_PTP = 6
PTP_OC_GetDeviceInfo = 0x1001
PTP_OC_OpenSession = 0x1002
PTP_OC_CloseSession = 0x1003
PTP_RC_OK = 0x2001
PTP_RC_SessionNotOpen = 0x2003
PTP_RC_ParameterNotSupported = 0x2006
PTP_RC_DeviceBusy = 0x2019
PTP_RC_SessionAlreadyOpened = 0x201E


def parseDeviceId(id):
 match = re.search('(#|\\\\)vid_([a-f0-9]{4})&pid_([a-f0-9]{4})(&|#|\\\\)', id, re.IGNORECASE)
 return [int(match.group(i), 16) if match else None for i in [2, 3]]


# from . import *
# from .. import *

# Create and import the python comtypes wrapper for the needed DLLs
comtypes.client._generate.__verbose__ = False
_oldImport = comtypes.client._generate._my_import
def _newImport(fullname):
 try:
  import importlib
  importlib.invalidate_caches()
 except:
  # Python 2
  pass
 _oldImport(fullname)
comtypes.client._generate._my_import = _newImport

GetModule('PortableDeviceApi.dll')
GetModule('PortableDeviceTypes.dll')
from comtypes.gen.PortableDeviceApiLib import *
from comtypes.gen.PortableDeviceApiLib import _tagpropertykey as tpka
from comtypes.gen.PortableDeviceTypesLib import *


def propkey(fmtid, pid):
 key = _tagpropertykey()
 key.fmtid = GUID(fmtid)
 key.pid = pid
 return pointer(key)

wpdCommonGuid = '{F0422A9C-5DC8-4440-B5BD-5DF28835658A}'
wpdMtpGuid = '{4D545058-1A2E-4106-A357-771E0819FC56}'

WPD_PROPERTY_COMMON_COMMAND_CATEGORY = propkey(wpdCommonGuid, 1001)
WPD_PROPERTY_COMMON_COMMAND_ID = propkey(wpdCommonGuid, 1002)
WPD_PROPERTY_COMMON_HRESULT = propkey(wpdCommonGuid, 1003)

WPD_COMMAND_MTP_EXT_EXECUTE_COMMAND_WITHOUT_DATA_PHASE = propkey(wpdMtpGuid, 12)
WPD_COMMAND_MTP_EXT_EXECUTE_COMMAND_WITH_DATA_TO_READ = propkey(wpdMtpGuid, 13)
WPD_COMMAND_MTP_EXT_EXECUTE_COMMAND_WITH_DATA_TO_WRITE = propkey(wpdMtpGuid, 14)
WPD_COMMAND_MTP_EXT_READ_DATA = propkey(wpdMtpGuid, 15)
WPD_COMMAND_MTP_EXT_WRITE_DATA = propkey(wpdMtpGuid, 16)
WPD_COMMAND_MTP_EXT_END_DATA_TRANSFER = propkey(wpdMtpGuid, 17)

WPD_PROPERTY_MTP_EXT_OPERATION_CODE = propkey(wpdMtpGuid, 1001)
WPD_PROPERTY_MTP_EXT_OPERATION_PARAMS = propkey(wpdMtpGuid, 1002)
WPD_PROPERTY_MTP_EXT_RESPONSE_CODE = propkey(wpdMtpGuid, 1003)
WPD_PROPERTY_MTP_EXT_TRANSFER_CONTEXT = propkey(wpdMtpGuid, 1006)
WPD_PROPERTY_MTP_EXT_TRANSFER_TOTAL_DATA_SIZE = propkey(wpdMtpGuid, 1007)
WPD_PROPERTY_MTP_EXT_TRANSFER_NUM_BYTES_TO_READ = propkey(wpdMtpGuid, 1008)
WPD_PROPERTY_MTP_EXT_TRANSFER_NUM_BYTES_TO_WRITE = propkey(wpdMtpGuid, 1010)
WPD_PROPERTY_MTP_EXT_TRANSFER_DATA = propkey(wpdMtpGuid, 1012)

class PROPVARIANT(Structure):
 _fields_ = [
  ('vt', c_ushort),
  ('reserved1', c_ubyte),
  ('reserved2', c_ubyte),
  ('reserved3', c_ulong),
  ('ulVal', c_ulong),
  ('reserved4', c_ulong),
 ]


class MtpContext(object):
 def __init__(self):
  self.name = 'Windows-MTP'
  self.classType = USB_CLASS_PTP

 def __enter__(self):
  comtypes.CoInitialize()
  return self

 def __exit__(self, *ex):
  comtypes.CoUninitialize()

 def listDevices(self, vendor):
  return (dev for dev in _listDevices() if dev.idVendor == vendor)

 def openDevice(self, device):
  return _MtpDriver(device.handle)


def _listDevices():
 """Lists all detected MTP devices"""
 # Create a device manager object
 pdm = CreateObject(PortableDeviceManager)

 length = c_ulong(0)
 pdm.GetDevices(POINTER(c_wchar_p)(), pointer(length))
 devices = (c_wchar_p * length.value)()
 pdm.GetDevices(devices, pointer(length))

 for id in devices:
  idVendor, idProduct = parseDeviceId(id)
  yield UsbDevice(id, idVendor, idProduct)

class _MtpDriver(object):
 """Send and receive MTP packages to a device."""
 def __init__(self, device):
  self.device = CreateObject(PortableDevice)
  self.device.Open(device, CreateObject(PortableDeviceValues))

 def _initCommandValues(self, command, context=None):
  params = CreateObject(PortableDeviceValues)
  params.SetGuidValue(WPD_PROPERTY_COMMON_COMMAND_CATEGORY, command.contents.fmtid)
  params.SetUnsignedIntegerValue(WPD_PROPERTY_COMMON_COMMAND_ID, command.contents.pid)
  if context:
   params.SetStringValue(WPD_PROPERTY_MTP_EXT_TRANSFER_CONTEXT, context)
  return params

 def _initPropCollection(self, values):
  params = CreateObject(PortableDevicePropVariantCollection)
  for value in values:
   p = PROPVARIANT()
   p.vt = VT_UI4
   p.ulVal = value
   params.Add(cast(pointer(p), POINTER(tag_inner_PROPVARIANT)))
  return params

 def _initInitialCommand(self, command, code, args):
  params = self._initCommandValues(command)
  params.SetUnsignedIntegerValue(WPD_PROPERTY_MTP_EXT_OPERATION_CODE, code)
  params.SetIPortableDevicePropVariantCollectionValue(WPD_PROPERTY_MTP_EXT_OPERATION_PARAMS, self._initPropCollection(args))
  return params

 def _initDataCommand(self, command, context, lengthKey, data):
  params = self._initCommandValues(command, context)
  params.SetUnsignedLargeIntegerValue(lengthKey, len(data))
  params.SetBufferValue(WPD_PROPERTY_MTP_EXT_TRANSFER_DATA, (c_ubyte * len(data)).from_buffer_copy(data), len(data))
  return params

 def _send(self, params):
  result = self.device.SendCommand(0, params)
  code = result.GetErrorValue(cast(WPD_PROPERTY_COMMON_HRESULT, POINTER(tpka)))
  if code != 0:
   raise Exception('MTP SendCommand failed: 0x%x' % code)
  return result

 def _readResponse(self, context):
  params = self._initCommandValues(WPD_COMMAND_MTP_EXT_END_DATA_TRANSFER, context)
  result = self._send(params)
  return self._getResponse(result)

 def _getContext(self, result):
  return result.GetStringValue(cast(WPD_PROPERTY_MTP_EXT_TRANSFER_CONTEXT, POINTER(tpka)))

 def _getResponse(self, result):
  return result.GetUnsignedIntegerValue(cast(WPD_PROPERTY_MTP_EXT_RESPONSE_CODE, POINTER(tpka)))

 def reset(self):
  pass

 def sendCommand(self, code, args):
  """Send a PTP/MTP command without data phase"""
  params = self._initInitialCommand(WPD_COMMAND_MTP_EXT_EXECUTE_COMMAND_WITHOUT_DATA_PHASE, code, args)
  result = self._send(params)
  return self._getResponse(result)

 def sendWriteCommand(self, code, args, data):
  """Send a PTP/MTP command with write data phase"""
  params = self._initInitialCommand(WPD_COMMAND_MTP_EXT_EXECUTE_COMMAND_WITH_DATA_TO_WRITE, code, args)
  params.SetUnsignedLargeIntegerValue(WPD_PROPERTY_MTP_EXT_TRANSFER_TOTAL_DATA_SIZE, len(data))
  result = self._send(params)
  context = self._getContext(result)

  params = self._initDataCommand(WPD_COMMAND_MTP_EXT_WRITE_DATA, context, WPD_PROPERTY_MTP_EXT_TRANSFER_NUM_BYTES_TO_WRITE, data)
  result = self._send(params)

  return self._readResponse(context)

 def sendReadCommand(self, code, args):
  """Send a PTP/MTP command with read data phase"""
  params = self._initInitialCommand(WPD_COMMAND_MTP_EXT_EXECUTE_COMMAND_WITH_DATA_TO_READ, code, args)
  result = self._send(params)
  context = self._getContext(result)
  length = result.GetUnsignedIntegerValue(cast(WPD_PROPERTY_MTP_EXT_TRANSFER_TOTAL_DATA_SIZE, POINTER(tpka)))

  params = self._initDataCommand(WPD_COMMAND_MTP_EXT_READ_DATA, context, WPD_PROPERTY_MTP_EXT_TRANSFER_NUM_BYTES_TO_READ, b'\0'*length)
  result = self._send(params)
  data, length = result.GetBufferValue(cast(WPD_PROPERTY_MTP_EXT_TRANSFER_DATA, POINTER(tpka)))

  return self._readResponse(context), bytes(bytearray(data[:length]))
  
def _checkResponse(code, acceptedCodes=[]):
	if code not in [PTP_RC_OK] + acceptedCodes:
		msg = 'MTP error 0x%x' % code
	if code == PTP_RC_ParameterNotSupported:
		raise InvalidCommandException(msg)
	else:
		raise MtpException(msg)
	
def parseString(data, offset):
  length = parse8(data[offset:offset+1])
  offset += 1
  end = offset + 2*length
  return end, data[offset:end].decode('utf16')[:-1]

def parseIntArray(data, offset):
  length = parse32le(data[offset:offset+4])
  offset += 4
  end = offset + 2*length
  return end, [parse16le(data[o:o+2]) for o in range(offset, end, 2)]
  
def _parseDeviceInfo(data):
	offset = 8
	offset, vendorExtension = parseString(data, offset)
	offset += 2

	offset, operationsSupported = parseIntArray(data, offset)
	offset, eventsSupported = parseIntArray(data, offset)
	offset, devicePropertiesSupported = parseIntArray(data, offset)
	offset, captureFormats = parseIntArray(data, offset)
	offset, imageFormats = parseIntArray(data, offset)

	offset, manufacturer = parseString(data, offset)
	offset, model = parseString(data, offset)
	offset, version = parseString(data, offset)
	offset, serial = parseString(data, offset)  
	return MtpDeviceInfo(manufacturer, model, serial, set(operationsSupported), vendorExtension) 
  
def is_switch_connected():
	try:
		pdm = CreateObject(PortableDeviceManager)
		length = c_ulong(0)
		pdm.GetDevices(POINTER(c_wchar_p)(), pointer(length))
		devices = (c_wchar_p * length.value)()
		pdm.GetDevices(devices, pointer(length))
		for id in devices:
			idVendor, idProduct = parseDeviceId(id)
			if idVendor!=None and idProduct!=None:
				dev=UsbDevice(id, idVendor, idProduct)
				dev2=MtpContext()
				switch=dev2.openDevice(dev)
				break
		response, data = switch.sendReadCommand(PTP_OC_GetDeviceInfo, [])
		TEST=_parseDeviceInfo(data)
		if TEST.model=="Switch":
			return True
		else:
			return False
	except:return False		