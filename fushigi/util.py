import struct, io, errno, os
import logging as log

# All reading and writing shorthand is assumed to be little-endian, unsigned

# If multibyte, you must specify endianness here (i.e. 'utf-16LE')
char_encoding = 'utf-8'

# Reading

def read(format_str, length, file_handler):
    buf = file_handler.read(length)
    return struct.unpack(format_str, buf)[0]

def read_int(file_handler):
    return read('<I', 4, file_handler)

def read_byte(file_handler):
    return read('<B', 1, file_handler)

def read_short(file_handler):
    return read('<H', 2, file_handler)

def read_bool(file_handler):
    return read('<?', 1, file_handler)

def read_until_null(file_handler):
    raw = bytearray()
    byte = file_handler.read(1)
    while byte != b'\0':
        raw.extend(byte)
        byte = file_handler.read(1)
    return raw

def read_null_term_string(file_handler):
    return read_until_null(file_handler).decode(char_encoding)

def read_string(file_handler):
    length = read_int(file_handler)
    return file_handler.read(length).decode(char_encoding)

def read_chunk(offset, size, file_handler, reset_pos=True):
    initial_pos = file_handler.tell()
    file_handler.seek(offset)
    raw = file_handler.read(size)
    if reset_pos:
        file_handler.seek(initial_pos)
    return io.BytesIO(raw)

# Writing

def write(value, format_str, file_handler):
    formatted = struct.pack(format_str, value)
    file_handler.write(formatted)

def write_int(value, file_handler):
    write(value, '<I', file_handler)

def write_byte(value, file_handler):
    write(value, '<B', file_handler)

def write_short(value, file_handler):
    write(value, '<H', file_handler)

def write_bool(value, file_handler):
    write(value, '<?', file_handler)

def write_null_term(value, file_handler):
    file_handler.write(value)
    file_handler.write('\0')

def write_null_term_string(value, file_handler):
    file_handler.write(value.encode(char_encoding))
    file_handler.write('\0')

def write_string(value, file_handler):
    encoded = value.encode(char_encoding)
    write_int(len(encoded), file_handler)
    file_handler.write(encoded)

# Other file handler operations

def align(n, file_handler):
    while file_handler.tell() % n:
        file_handler.read(1)

def pad(n, file_handler):
    file_handler.read(n)

def skip_if_null_byte(file_handler):
    initial_pos = file_handler.tell()
    if not read_byte(file_handler) == 0:
        file_handler.seek(initial_pos)

def get_pos(file_handler):
    return format_hex(file_handler.tell())

# File management

def ensure_dir_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            log.debug('Directory at %s already exists', path)
            raise

def clear_dir_contents(folder):
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path): # should probably do error-checking wrt file permissions
            os.unlink(file_path)

# Printing

def print_list(l):
    for element in l:
        print(element)

def print_dict(d):
    for k, v in d.items():
        print(str(k) + ": " + str(v))
