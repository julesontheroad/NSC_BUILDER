from Fs.Xci import Xci
from Fs.Nca import Nca
from Fs.Nsp import Nsp
from Fs.Rom import Rom
from Fs.Pfs0 import Pfs0
from Fs.Ticket import Ticket
from Fs.File import File

def factory(name):
	if name.endswith('.xci'):
		f = Xci()
	elif name.endswith('.nsp'):
		f = Nsp()
	elif name.endswith('.nsx'):
		f = Nsp()
	elif name.endswith('.nca'):
		f =  Nca()
	elif name.endswith('.tik'):
		f =  Ticket()
	else:
		f = File()

	return f