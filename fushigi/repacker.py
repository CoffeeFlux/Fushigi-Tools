import os, png, io
from .util import * # in package
import logging as log

BUCKET_SIZE = 32

def bad_hash(filename, divisor):
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
		log.debug('file offsets: %s, file data: %s', file_offset_pos, file_data_pos)

		# Hopefully the files are sorted!
		for file in files:
			log.debug('packing file: ' + file)
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
	hash_offsets = {}
	metadata_base = 8 # preceded by fingerprint and bucket size
	for file in files:
		basename = os.path.split(file)[1]
		name, extension = os.path.splitext(basename)

		namehash = bad_hash(name, BUCKET_SIZE)
		if not namehash in hashmap:
			hashmap[namehash] = []
		hashmap[namehash].append(file)

	# Sort the groupings for each hash
	for key in hashmap.keys():
		hashmap[key] = sorted(hashmap[key])
	log.debug('hashes: %s', hashmap)

	with open(output, 'wb') as f:
		# Write header, bucket size, and offset section for hashmap
		f.write('Him5'.encode('utf-8'))
		write_int(BUCKET_SIZE, f)
		f.seek(metadata_base + 8 * BUCKET_SIZE)

		# Write entries for each key in the hashmap
		for hash_value in range(BUCKET_SIZE):
			entries = hashmap.get(hash_value, [])
			hash_start_pos = f.tell()
			for file in entries:
				basename = os.path.split(file)[1]
				name, extension = os.path.splitext(basename)
				write_byte(len(name) + 6, f)
				hash_offsets[name] = f.tell()
				write_null(4, f) # to fill in later
				write_null_term_string(name, f)
			if len(entries):
				write_null(1, f)
			hash_end_pos = f.tell()

			# Go back and fill in the offset section
			f.seek(metadata_base + 8 * hash_value)
			write_int(hash_end_pos - hash_start_pos, f)
			write_int(hash_start_pos, f)
			f.seek(hash_end_pos)
		log.debug('hash offsets: %s', hash_offsets)

		# Write the actual data
		for hash_value in sorted(hashmap):
			entries = hashmap[hash_value]
			for file in entries:
				basename = os.path.split(file)[1]
				name, extension = os.path.splitext(basename)

				# Go back and write the offset in the hash table
				data_start_pos = f.tell()
				f.seek(hash_offsets[name])
				write(data_start_pos, '>I', f)
				f.seek(data_start_pos)

				# Write data lengths and raw data
				write_null(4, f) # data is uncompressed
				with open(file, 'rb') as source:
					data = source.read()
				write_int(len(data), f)
				f.write(data)
