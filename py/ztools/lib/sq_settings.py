
def set_dev_environment():
	global key_system
	key_system="development"
def set_prod_environment():	
	global key_system
	key_system="production"

try:
	a=key_system
except:
	set_prod_environment()	