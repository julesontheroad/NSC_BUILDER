import sys, os
from struct import pack as pk, unpack as upk

try:
    input = raw_input
except NameError:
    pass

def gen_header(argc, argv):
    stringTable = '\x00'.join([os.path.basename(file) for file in argv[2:]])
    headerSize = 0x10 + (argc-2)*0x18 + len(stringTable)
    remainder = 0x10 - headerSize%0x10
    headerSize += remainder
    
    fileSizes = [os.path.getsize(file) for file in argv[2:]]
    fileOffsets = [sum(fileSizes[:n]) for n in range(argc-2)]
    
    fileNamesLengths = [len(os.path.basename(file))+1 for file in argv[2:]] # +1 for the \x00 separator
    stringTableOffsets = [sum(fileNamesLengths[:n]) for n in range(argc-2)]
    
    header =  b''
    header += b'PFS0'
    header += pk('<I', argc-2)
    header += pk('<I', len(stringTable)+remainder)
    header += b'\x00\x00\x00\x00'
    
    for n in range(argc-2):
        header += pk('<Q', fileOffsets[n])
        header += pk('<Q', fileSizes[n])
        header += pk('<I', stringTableOffsets[n])
        header += b'\x00\x00\x00\x00'
    header += stringTable.encode()
    header += remainder * b'\x00'
    
    return header   

def mk_nsp(argc, argv):
    if argc < 3:
        print('Usage is: %s output file1 file2 ...' % sys.argv[0])
        return 1
        
    name = argv[1]
    outf = open(name, 'wb')
    
    print('Generating header...')
    header = gen_header(argc, argv)
    outf.write(header)
    
    for f in argv[2:]:
        print('Appending %s...' % f)
        with open(f, 'rb') as inf:
            while True:
                buf = inf.read(4096)
                if not buf:
                    break
                outf.write(buf)
    
    print('Saved to %s!' % outf.name)
    outf.close()
    
    return 0
    
if __name__ == '__main__':
    sys.exit(mk_nsp(len(sys.argv), sys.argv))
