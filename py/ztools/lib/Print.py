import Status

global silent
enableInfo = True
enableError = True
enableWarning = True
enableDebug = False

silent = False

def info(s):
	if not silent and enableInfo:
		Status.print_(s)

def error(s):
	if not silent and enableError:
		Status.print_(s)

def warning(s):
	if not silent and enableWarning:
		Status.print_(s)

def debug(s):
	if not silent and enableDebug:
		Status.print_(s)