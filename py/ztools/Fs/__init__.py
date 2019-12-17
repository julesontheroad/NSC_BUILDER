from Fs.Xci import Xci
from Fs.pXci import uXci
from Fs.pXci import nXci
from Fs.pXci import lXci
from Fs.Nca import Nca
from Fs.Nsp import Nsp
from Fs.Rom import Rom
from Fs.Nacp import Nacp
from Fs.Pfs0 import Pfs0
from Fs.Hfs0 import Hfs0
from Fs.Ticket import Ticket
from Fs.File import File
from Fs.ChromeNsp import ChromeNsp
from Fs.ChromeXci import ChromeXci
from Fs.ChromeNacp import ChromeNacp

def factory(name):
	if name.endswith('.xci'):
		f = Xci()
	elif name.endswith('.xcz'):
		f = Xci()		
	elif name.endswith('.nsp'):
		f = Nsp()
	elif name.endswith('.nsz'):
		f = Nsp()		
	elif name.endswith('.nsx'):
		f = Nsp()
	elif name.endswith('.nca'):
		f =  Nca()
	elif name.endswith('.ncz'):
		f =  File()		
	elif name.endswith('.nacp'):
		f =  Nacp()
	elif name.endswith('.tik'):
		f =  Ticket()
	elif name.endswith('.hfs0'):
		f =  Hfs0()		
	else:
		f = File()
	return f