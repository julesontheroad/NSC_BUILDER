'''	
versions = 
      0:       "1.0.0", -> keygeneration = 0
    450:       "1.0.0", -> keygeneration = 0
    65796:     "2.0.0", -> keygeneration = 1
    131162:    "2.1.0", -> keygeneration = 1
    196628:    "2.2.0", -> keygeneration = 1
    262164:    "2.3.0", -> keygeneration = 1
    201327002: "3.0.0", -> keygeneration = 2
    201392178: "3.0.1", -> keygeneration = 3
    201457684: "3.0.2", -> keygeneration = 3
    268435656: "4.0.0", -> keygeneration = 4
    268501002: "4.0.1", -> keygeneration = 4
    269484082: "4.1.0", -> keygeneration = 4
    335544750: "5.0.0", -> keygeneration = 5
    335609886: "5.0.1", -> keygeneration = 5
    335675432: "5.0.2", -> keygeneration = 5
    336592976: "5.1.0", -> keygeneration = 5
    402653494: "6.0.0-4", -> keygeneration = 6 
    402653514: "6.0.0", -> keygeneration = 6
    402653544: "6.0.0", -> keygeneration = 6
    402718730: "6.0.1", -> keygeneration = 6
    403701850: "6.1.0", -> keygeneration = 6
	404750336: "6.2.0" -> keygeneration = 7
    404750376: "6.2.0-40" -> keygeneration = 7
'''	

def getTopRSV(keygeneration, RSV):
	if keygeneration == 0:
		return 450	
	if keygeneration == 1:
		return 262164
	if keygeneration == 2:
		return 201327002
	if keygeneration == 3:
		return 201457684
	if keygeneration == 4:
		return 269484082
	if keygeneration == 5:
		return 336592976
	if keygeneration == 6:
		return 403701850
	if keygeneration == 7:
		return 404750376
	else:
		return RSV

def getMinRSV(keygeneration, RSV):
	if keygeneration == 0:
		return 0	
	if keygeneration == 1:
		return 65796
	if keygeneration == 2:
		return 201327002
	if keygeneration == 3:
		return 201392178
	if keygeneration == 4:
		return 268435656
	if keygeneration == 5:
		return 335544750
	if keygeneration == 6:
		return 402653494
	if keygeneration == 7:
		return 404750336
	else:
		return RSV		
		
def getFWRangeKG(keygeneration):
	if keygeneration == 0:
		return "(1.0.0)"	
	if keygeneration == 1:
		return "(2.0.0 - 2.3.0)"	
	if keygeneration == 2:
		return "(3.0.0)"	
	if keygeneration == 3:
		return "(3.0.1 - 3.0.2)"	
	if keygeneration == 4:
		return "(4.0.0 - 4.1.0)"	
	if keygeneration == 5:
		return "(5.0.0 - 5.1.0)"
	if keygeneration == 6:
		return "(6.0.0 - 6.1.0)"
	if keygeneration == 7:
		return "(6.2.0 - >6.2.0)"
	else:
		return "UNKNOWN"			

def getFWRangeRSV(RSV):
	if RSV > 404750376:
		return "(>6.2.0-40)"
	if RSV == 404750376:
		return "(6.2.0-40)"
	if RSV == 404750336:
		return "(6.2.0)"			
	if RSV >= 403701850:
		return "(6.1.0)"	
	if RSV >= 402718730:
		return "(6.0.1)"	
	if RSV >= 402653514:
		return "(6.0.0)"	
	if RSV >= 402653494:
		return "(6.0.0-4)"			
	if RSV >= 336592976:
		return "(5.1.0)"	
	if RSV >= 335675432:
		return "(5.0.2)"			
	if RSV >= 335609886:
		return "(5.0.1)"			
	if RSV >= 335544750:
		return "(5.0.0)"	
	if RSV >= 269484082:
		return "(4.1.0)"	
	if RSV >= 268501002:
		return "(4.0.1)"	
	if RSV >= 268435656:
		return "(4.0.0)"	
	if RSV >= 201457684:
		return "(3.0.2)"					
	if RSV >= 201392178:
		return "(3.0.1)"				
	if RSV >= 201327002:
		return "(3.0.0)"	
	if RSV >= 262164:
		return "(2.3.0)"	
	if RSV >= 196628:
		return "(2.2.0)"	
	if RSV >= 131162:
		return "(2.1.0)"	
	if RSV >= 65796:
		return "(2.0.0)"	
	if RSV >= 450:
		return "(1.0.0)"	
	if RSV >= 0:
		return "(1.0.0)"	
	else:
		return range	


def getSize(bytes):
	if bytes>(1024*1024*1024):
		Gbytes=bytes/(1024*1024*1024)
		Gbytes=round(Gbytes,2)
		Gbytes=str(Gbytes)+"GB"
		return Gbytes
	if bytes>(1024*1024):
		Mbytes=bytes/(1024*1024)
		Mbytes=round(Mbytes,2)
		Mbytes=str(Mbytes)+"MB"
		return Mbytes		
	if bytes>(1024):
		Kbytes=bytes/(1024)
		Kbytes=round(Kbytes,2)
		Kbytes=str(Kbytes)+"KB"	
		return Kbytes		
	else:
		bytes=str(bytes)+"B"	
		return bytes
		
def getTypeFromCNMT(number):	
	if number == 0:
		return "Meta: "
	if number == 1:
		return "Program: "
	if number == 2:
		return "Data: "
	if number == 3:
		return "Control: "
	if number == 4:
		return "HtmlDoc: "
	if number == 5:
		return "LegalInf: "
	if number == 6:
		return "Delta: "














	
		