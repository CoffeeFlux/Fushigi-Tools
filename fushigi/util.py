import struct, io, errno, os
import logging as log

def format_hex(s): # yes, this is bad; i'll remove it later
    return '0x' + format(s, '02x').upper().zfill(8)

def read(format_str, length, file_handler):
    buf = file_handler.read(length)
    return struct.unpack(format_str, buf)[0]

# Shorthand read functions are assumed to be little-endian, unsigned
def read_int(file_handler):
    return read('<I', 4, file_handler)

def read_byte(file_handler):
    return read('<B', 1, file_handler)

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
    return read_until_null(file_handler).decode('utf-8')

def read_string(file_handler):
    length = read_int(file_handler)
    return file_handler.read(length).decode('utf-8')

def read_chunk(offset, size, file_handler, reset_pos=True):
    initial_pos = file_handler.tell()
    file_handler.seek(offset)
    raw = file_handler.read(size)
    if reset_pos:
        file_handler.seek(initial_pos)
    return io.BytesIO(raw)

def align(n, file_handler):
    while file_handler.tell() % n:
        file_handler.read(1)

def pad(n, file_handler):
    file_handler.read(n)

def get_pos(file_handler):
    return format_hex(file_handler.tell())

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

def print_list(l):
    for element in l:
        print(element)

def print_dict(d):
    for k, v in d.items():
        print(str(k) + ": " + str(v))
