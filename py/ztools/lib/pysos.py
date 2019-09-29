"""SOS: Simple Objects Storage / persistant dictionaries and lists.

This is ideal for lists or dictionaries which either need persistence,
are too big to fit in memory or both. It's high performance and supports
both synchronous and asynchronous modes.

Dictionaries
============

How is the file structured?
---------------------------

It's based on pure text files and might look like this:
```
# comment line
"key"    "value"
"content"    ["arbitrary JSON",123,true,null,["sub-list"],{"key":"value"}]
"encoding"    "UTF-8"
# commenting lines is useful to mark deleted items
# instead of rewriting a huge file
"foo"    123

# empty lines are allowed too
```
    

Each line is either an commented line starting with #.
Or a json key value pair separated by a tab.

How does it work?
-----------------

Two structures are kept in memory:
- a dictionary "key -> file offset"
- a list of free buckets (size, file offset), sorted by size

When an item is added, the best fitting bucket is looked up.
Or, if there is none, it's put at the end.

When an item is removed, simply set it's key size to 0 to mark it as deleted and add the bucket's (size,offset) to the "free list".

When an item is updated, we *NEVER* update the value in place.
Why not? Because if process is killed in the middle of the write, you'll have inconsistent data.
It'll contain a portion of the new value, and the remainder of the old value.
Therefore, we'll play it safe: write the new item, and when it's done, remove the old one.

In order to ensure proper consistency, it is therefore important to write the key size (marking it valid) at the very last.


What happens in case of a crash?
--------------------------------

By simply reading the file, we can build both the (key -> offset) index and the free buckets list on the fly.
And since we always add/update values safely by marking it valid at the end, we can ensure their consistency.

...as a last comment: when a bucket is filled with a smaller content, the remaining space becomes a new bucket.
...except if it's too small to be worthwhile (< 20 bytes). Here also, first write the new bucket, then resize the old one!



Lists
=====

What is it complicated anyway?
------------------------------
Imagine we would store it "in order" in a file:
````
A
B
C
...
```
This would be a disaster,since when we update B to B', we would have to either shift all following items, a no-go.
Or work with indexes:
````
1:A
#obsolete B
3:C
2:B'
...
```
That's already much better, and is the structure we use, thereby using a dictionary underneath.
With the only difference that the keys are ints.

The other difficulty are deletitions. If you remove B', you have to update all indexes following the item.
Going in the file and updating millions of indexes is a no-go too.


How does it work?
-----------------
Using a very simple but efficient trick!
First, new items will always use an autoincrement as key.
Then, a mapping will be used:
list index -> dict key -> value

The way to perform the mapping is utterly simple: it's the sorted keys of the dictionary!
"""

import io
import os.path
import bisect
try:
    import ujson as json
except:
    import json


    
def parseLine(line):
    #print(line)
    (left, sep, right) = line.partition(b'\t')
    key = json.loads( left.decode('utf8') )
    value = json.loads( right.decode('utf8') )
    return ( key, value )
    
def parseKey(line):
    (left, sep, right) = line.partition(b'\t')
    key = json.loads( left.decode('utf8') )
    return key
    
def parseValue(line):
    (left, sep, right) = line.partition(b'\t')
    value = json.loads( right.decode('utf8') )
    return value


class Dict(dict):
    START_FLAG = b'# FILE-DICT v1\n'

    def __init__(self, path):
        self.path = path
        
        if os.path.exists(path):
            file = io.open(path, 'r+b')
        else:
            file = io.open(path, 'w+b')
            file.write( self.START_FLAG )
            file.flush()
        
        self._file = file
        self._offsets = {}   # the (size, offset) of the lines, where size is in bytes, including the trailing \n
        self._free_lines = []
        self._observers = []
        
        offset = 0
        while True:
            line = file.readline()
            if line == b'': # end of file
                break
            
            # ignore empty lines
            if line == b'\n':
                offset += len(line) 
                continue
            
            if line.startswith(b'#'):	# skip comments but add to free list
                if len(line) > 5:
                    self._free_lines.append( (len(line), offset) )
            else:
                # let's parse the value as well to be sure the data is ok
                key = parseKey(line)
                self._offsets[key] = offset
            
            offset += len(line) 
        
        self._free_lines.sort()
        print("free lines: " + str(len(self._free_lines)))
        
    def _freeLine(self, offset):
        self._file.seek(offset)
        self._file.write(b'#')
        self._file.flush()
        
        line = self._file.readline()
        size = len(line) + 1   # one character was written beforehand
        
        if size > 5:
            bisect.insort(self._free_lines, (len(line)+1, offset) )
        
    def _findLine(self, size):
        index = bisect.bisect( self._free_lines, (size,0) )
        if index >= len( self._free_lines ):
            return None
        else:
            return self._free_lines.pop(index)
        
    def _isWorthIt(self, size):
        # determines if it's worth to add the free line to the list
        # we don't want to clutter this list with a large amount of tiny gaps
        return (size > 5 + len(self._free_lines))
        
    def __getitem__(self, key):
        offset = self._offsets[key]
        self._file.seek(offset)
        line = self._file.readline()
        value = parseValue(line)
        return value
        
    def __setitem__(self, key, value):
        # trigger observers
        if self._observers:
            old_value = self[key] if key in self else None
            for callback in self._observers:
                callback(key, value, old_value)
        
        if key in self._offsets:
            # to be removed once the new value has been written
            old_offset = self._offsets[key]
        else:
            old_offset = None
            
        
        line = json.dumps(key,ensure_ascii=False) + '\t' + json.dumps(value,ensure_ascii=False) + '\n'
        line = line.encode('UTF-8')
        size = len(line)
        
        found = self._findLine(size)

        if found:
            # great, we can recycle a commented line
            (place, offset) = found
            self._file.seek(offset)
            diff = place - size
            # if diff is 0, we'll override the line perfectly:        XXXX\n -> YYYY\n
            # if diff is 1, we'll leave an empty line after:          XXXX\n -> YYY\n\n
            # if diff is > 1, we'll need to comment out the rest:     XXXX\n -> Y\n#X\n (diff == 3)
            if diff > 1:
                line += b'#'
                if diff > 5:
                    # it's worth to reuse that space
                    bisect.insort(self._free_lines, (diff, offset + size) )
                
        else:
            # go to end of file
            self._file.seek(0, os.SEEK_END)
            offset = self._file.tell()
        
        # if it's a really big line, it won't be written at once on the disk
        # so until it's done, let's consider it a comment
        self._file.write(b'#' + line[1:])
        if line[-1] == 35:
            # if it ends with a "comment" (bytes to recycle),
            # let's be clean and avoid cutting unicode chars in the middle
            while self._file.peek(1)[0] & 0x80 == 0x80: # it's a continuation byte
                self._file.write(b'.')
        self._file.flush()
        # now that everything has been written...
        self._file.seek(offset)
        self._file.write(line[0:1])
        self._file.flush()
    
        # and now remove the previous entry
        if old_offset:
            self._freeLine(old_offset)
        
        self._offsets[key] = offset
        
        
            
        
    def __delitem__(self, key):
        # trigger observers
        if self._observers:
            old_value = self[key]
            for callback in self._observers:
                callback(key, None, old_value)
                
        offset = self._offsets[key]
        self._freeLine(offset)
        del self._offsets[key]
        
        
    def __contains__(self, key):
        return (key in self._offsets)
    
    def observe(self, callback):
        self._observers.append(callback)
        
    
    def keys(self):
        return self._offsets.keys()
    
    def clear(self):
        self._file.truncate(0)
        self._file.flush()
        self._offsets = {}
        self._free_lines = []
        
    def items(self):
        offset = 0
        while True:
            # if somethig was read/written while iterating, the stream might be positioned elsewhere
            if self._file.tell() != offset:
                self._file.seek(offset) #put it back on track
            
            line = self._file.readline()
            if line == b'': # end of file
                break
            
            offset += len(line)
            # ignore empty and commented lines
            if line == b'\n' or line[0] == 35:
                continue
            yield parseLine(line)
    
    def __iter__(self):
        return self.keys()
    
    def values(self):
        for item in self.items():
            yield item[1]
            
    def __len__(self):
        return len(self._offsets)
        

    
    def size(self):
        self._file.size()
        
        
    def close(self):
        self._file.close()
        print("free lines: " + str(len(self._free_lines)))




class List(list):
    START_FLAG = b'# FILE-LIST v1\n'
    
    def __init__(self, path):
        self._dict = Dict(path)
        self._indexes = sorted( self._dict.keys() )
        self._observers = []
    
    def __getitem__(self, i):
        key = self._indexes[i]
        return self._dict[key]
        
    def __setitem__(self, i, value):
        # trigger observers
        if self._observers:
            old_value = self[i]
            for callback in self._observers:
                callback(i, value, old_value)
                
        key = self._indexes[i]
        self._dict[key] = value
    
    def append(self, value):
        # trigger observers
        if self._observers:
            for callback in self._observers:
                callback(len(self._indexes), value, None)
                
        if len(self._indexes) == 0:
            key = 0
        else:
            key = self._indexes[-1] + 1
                
        self._dict[key] = value
        self._indexes.append(key)
        
    def __delitem__(self, i):
        # trigger observers
        if self._observers:
            old_value = self[i]
            for callback in self._observers:
                callback(i, None, old_value)
                
        key = self._indexes[i]
        del self._dict[key]
        del self._indexes[i]
    
    def __len__(self):
        return len(self._indexes)
        
    def __contains__(self, key):
        raise Exception('Operation not supported for lists')
    
    # this must be overriden in order to provide the correct order
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]
    
    def observe(self, callback):
        self._observers.append(callback)
        
    def clear(self):
        self._dict.clear()
        self._indexes = []
    
    
    def size(self):
        self._dict.size()
        
    def close(self):
        self._dict.close()


def load(path):
    file = open(path, 'rb')
    first = file.readline()
    
    if first == Dict.START_FLAG:
        file.close()
        return Dict(path)
    if first == List.START_FLAG:
        file.close()
        return List(path)
        
    for line in file:
        if line[0] == 0x23:
            continue
        key = parseKey(line)
        if isinstance(key, int):
            file.close()
            return List(path)
        else:
            file.close()
            return Dict(path)
    raise Exception("Empty collection without header. Cannot determine whether it is a list or a dict.")
    
import csv
import chardet
#from chardet.universaldetector import UniversalDetector
#import cchardet as chardet

def detectEncoding(path):
    with open(path, 'rb') as f:
        res = chardet.detect( f.read(10*1024*1024) )
    print(res)
    return res['encoding']
    
    detector = UniversalDetector()
    for line in open(path, 'rb'):
        detector.feed(line)
        if detector.done: break
    detector.close()
    print(detector.result)
    return detector.result.encoding
    
def csv2sos(path, keys=None, encoding=None, dialect=None):
    
    if not encoding:
        encoding = detectEncoding(path)
        print('Detected encoding: %s' % encoding)
    
    csvfile = open(path, 'rt', encoding=encoding)
    sosfile = open(path + '.sos', 'wt', encoding='utf8')

    if not dialect:
        dialect = csv.Sniffer().sniff(csvfile.read(1024*1024), delimiters=[';','\t',','])
        print('Detected csv dialect: %s' % dialect)
    
    csvfile.seek(0)
    reader = csv.DictReader(csvfile, dialect=dialect)
    i = 0
    for row in reader:
        sosfile.write(str(i) + '\t' + json.dumps(row, ensure_ascii=False) + '\n')
        i += 1
        if i % 100000 == 0:
            print("%10d items converted" % i)

    csvfile.close()    
    sosfile.close()
