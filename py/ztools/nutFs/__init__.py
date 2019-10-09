import nutFs.Nsp
import nutFs.Xci
import nutFs.Nca
import nutFs.Nacp
import nutFs.Ticket
import nutFs.Cnmt
import nutFs.File

def factory(name):
	if name.endswith('.xci'):
		f = nutFs.Xci.Xci()
	elif name.endswith('.xcz'):
		f = nutFs.Xci.Xci()
	elif name.endswith('.nsp'):
		f = nutFs.Nsp.Nsp()
	elif name.endswith('.nsz'):
		f = nutFs.Nsp.Nsp()
	elif name.endswith('.nsx'):
		f = nutFs.Nsp.Nsp()
	elif name.endswith('.nca'):
		f =  nutFs.Nca.Nca()
	elif name.endswith('.nacp'):
		f =  nutFs.Nacp.Nacp()
	elif name.endswith('.tik'):
		f =  nutFs.Ticket.Ticket()
	elif name.endswith('.cnmt'):
		f =  nutFs.Cnmt.Cnmt()
	else:
		f = nutFs.File.File()

	return f