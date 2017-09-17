import os, png, io
from .util import * # in package
import logging as log

def hash(filename, divisor):
	result = 0
	i = 1

	for char in filename:
		result = result ^ i * ord(char)
		i += 0x1F3

	return int((result ^ (result >> 0x0B)) % divisor)

def him4(files, output):
	with open(output, 'wb') as f:
		f.write('Him4'.encode('utf-8'))
		write_int(len(files), f)

		file_offset_pos = f.tell()
		file_data_pos = file_offset_pos + 4*len(files)

		# Hopefully the files are sorted!
		for file in files:
			with open(file, 'rb') as source:
				data = source.read()

			f.seek(file_offset_pos)
			write_int(file_data_pos, f)
			file_offset_pos += 4

			f.seek(file_data_pos)
			write_int(0, f)
			write_int(len(data), f)
			f.write(data)
			file_data_pos = f.tell()

# This is awful and bad and I should probably try to clean it up
def him5(files, output):
	hashmap = {}
	for file in files:
		basename = os.path.split(file)[1]
		name, extension = os.path.splitext(basename)
		namehash = hash(name, 32)
		if not namehash in hashmap:
			hashmap[namehash] = []
		hashmap[namehash].append(file)

	print_dict(hashmap)
