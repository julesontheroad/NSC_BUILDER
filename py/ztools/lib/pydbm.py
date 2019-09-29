'''
Pydbm - Library Data:
* Name: Pydbm
* Author: dagnelies
* License: Apache 2.0 -> https://github.com/dagnelies/pydbm/blob/master/LICENSE
https://github.com/dagnelies/pydbm
'''
"""A smart dbm clone / persistant dictionary.

This is ideal for dictionaries which either need persistence,
are too big to fit in memory or both. It's high performance and supports
both synchronous and asynchronous modes.

The keys have a max size of 2^16 bytes (~65kb) and the values are limited to 2^32 bytes (~4Gb).


How is the file structured?
---------------------------

It starts with a text line "SIMPLE-DATA-FORMAT 1.0", followed by the data.
For each item:
	item header:
		- a "\n". This is useful to check data integrity as wells as to inspect the raw file.
		- a "+" if the bucket is used, "-" if it is free (a deleted item for instance).
		- size of the "bucket" as 4-byte int
		- size of the key as 2-byte int
		- size of the value as 4-byte int
	item content:
		- the key
		- the value

...the reason to add a "bucket" size is because it might be different than its content size!
Why? Because this isn't an "add only" thing. Entries might be frequently updated or deleted.
When this happens, buckets are freed and it's "polite" to recycle that free space.

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
"""

import io
import os.path
import bisect


def _int2bytes(i,n):
	return i.to_bytes(n, byteorder='little', signed=False)

def _bytes2int(b):
	return int.from_bytes(b, byteorder='little', signed=False)

class PyDBM:
	START_FLAG = b'FILE-DICT v1'
	FREE_BUCKET = b'\n-'
	USED_BUCKET = b'\n+'

# cached: fast reads but memory consuming
# no cache: slow reads but low memory consumption

# sync: slow writes but safe (never loses/corrups data, even in hard crashes)
# async: fast writes but unsafe (buffers IO operations and might result in lost/corrupted data if the process is killed unexpectedly)

	def __init__(self, path, readonly=False, async_=False):
		self.path = path
		self.readonly = readonly
		#self.cachesize = cachesize
		self.async_ = async_

		if readonly == True:
			file = io.open(path, 'rb')
		elif os.path.exists(path):
			file = io.open(path, 'r+b')
		else:
			file = io.open(path, 'w+b')

		self._file = file
		self._offsets = {}
		self._free_buckets = []

		if not file.peek():
			file.write( self.START_FLAG )
			return

		if file.read(len(self.START_FLAG)) != self.START_FLAG:
			raise path + " is not a " + self.START_FLAG + " file, has wrong version, or is corrupt."

		while file.peek():
			offset = file.tell()

			(used, bucket_size, key_size, value_size) = self._readHeader()

			if not used:
				self._free_buckets.append( (bucket_size, offset) )
			else:
				key = file.read(key_size)
				self._offsets[key] = offset

			file.seek(offset + bucket_size)

		self._free_buckets.sort()

		
	def _readHeader(self, offset=None):
		file = self._file
		if offset:
			file.seek(offset)

		mark = file.read(2)
		if mark != self.USED_BUCKET and mark != self.FREE_BUCKET:
			raise Exception(self.path + " contains corrupt data at byte " + str(offset) + ".")
		
		used = (mark == self.USED_BUCKET)
		bucket_size = _bytes2int(file.read(4))
		key_size = _bytes2int(file.read(2))
		value_size = _bytes2int(file.read(4))
		
		return (used, bucket_size, key_size, value_size)


	def _releaseBucket(self, offset):
		self._file.seek(offset)
		self._file.write(self.FREE_BUCKET)
		size = _bytes2int(self._file.read(4))
		bisect.insort(self._free_buckets, (size,offset) )

	def _findBestBucket(self, size):
		index = bisect.bisect( self._free_buckets, (size,0) )
		if index >= len( self._free_buckets ):
			return None
		else:
			#print("bucket %d -> %d" % (size, self._free_buckets[index][0]))
			if size < 0.8 * self._free_buckets[index][0]:
				return None # We don't want to waste more than 20% place of a bucket
			else:
				return self._free_buckets.pop(index)
		
		
	def __getitem__(self, key):
		offset = self._offsets[key]
		(used, bucket_size, key_size, value_size) = self._readHeader(offset)
		key = self._file.read(key_size)
		value = self._file.read(value_size)
		return value
		
	def __setitem__(self, key, value):
		if key in self._offsets:
			old_offset = self._offsets[key]
		else:
			old_offset = None

		bucket_size = 4 + 2 + 2 + 4 + len(key) + len(value)
		key_size = len(key)
		value_size = len(value)

		bucket = self._findBestBucket(bucket_size)

		if bucket:
			# let's erase our "ideal" size, we don't want to resize it
			(bucket_size, offset) = bucket
			self._file.seek(offset)
		else:
			self._file.seek(0, os.SEEK_END)
			offset = self._file.tell()
		
		
		if self.async_:
			# some people want it fast!
			# but be warned, if it crashes in the middle, you'll have corrupt data
			self._file.write(self.USED_BUCKET)
			self._file.write(_int2bytes(bucket_size, 4))
			self._file.write(_int2bytes(key_size, 2))
			self._file.write(_int2bytes(value_size, 4))
			self._file.write(key)
			self._file.write(value)
		else:
			# some people want is safe!
			# until we're sure it's finished, let's mark this bucket as empty!
			self._file.write(self.FREE_BUCKET)
			self._file.write(_int2bytes(bucket_size, 4))
			self._file.write(_int2bytes(key_size, 2))
			self._file.write(_int2bytes(value_size, 4))
			self._file.write(key)
			self._file.write(value)
			self._file.flush()

			# now that everything has been written...
			self._file.seek(offset)
			self._file.write(self.USED_BUCKET)
			self._file.flush()

		if old_offset:
			self._releaseBucket(old_offset)
			if not self.async_:
				self._file.flush()

		self._offsets[key] = offset
			
		
	def __delitem__(self, key):
		offset = self._offsets[key]
		self._releaseBucket(offset)
		del self._offsets[key]
		
		if not self.async_:
			self._file.flush()

		
	def __contains__(self, key):
		return (key in self._offsets)
	
	def keys(self):
		return self._offsets.keys()
	
	def __iter__(self):
		# TODO
		return None

	def __len__(self):
		return len(self._offsets)
		

	
	def size(self):
		self._file.size()
		
	def flush(self):
		self._file.flush()
		
	def close(self):
		self._file.close()

