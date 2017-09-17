import os, png, io
from .util import * # in package
import logging as log

file_fingerprint_table = {
    0x424D: 'bmp',
    0x4869: 'him',
    0x4F67: 'ogg',
    0x5249: 'wav'
}

def get_extension(data):
    # there are some silly 1-byte entries i've chosen to preserve as '.nul'
    if len(data) >= 2:
        fingerprint = struct.unpack('>H', data[:2])[0]
        # TGA has its identifier in the footer >_>
        if fingerprint in file_fingerprint_table:
            return file_fingerprint_table[fingerprint]
        elif length > 18 and data[-18:-2].decode('utf-8') == 'TRUEVISION-XFILE':
            return 'tga'
        else:
            return 'nul'
    return 'nul'

# This can probably cleaned up, but currently I'm just implementing off the asm
def decompress(raw_data, target_length):
    decompressed = bytearray(target_length)
    src_index = 0
    dst_index = 0
    code = 0
    back = 0

    while src_index < len(raw_data) and dst_index < target_length:
        if code == 0:
            code = raw_data[src_index]
            src_index += 1
            if code < 0x20:
                back = 0
                if code < 0x1D:
                    code += 1
                elif code == 0x1D:
                    code = raw_data[src_index] + 0x1E
                    src_index += 1
                elif code == 0x1E:
                    code = raw_data[src_index]
                    src_index += 1
                    code <<= 8
                    code |= raw_data[src_index]
                    src_index += 1
                    code += 0x11E
                elif code == 0x1F:
                    code = raw_data[src_index]
                    src_index += 1
                    code <<= 8
                    code |= raw_data[src_index]
                    src_index += 1
                    code <<= 8
                    code |= raw_data[src_index]
                    src_index += 1
                    code <<= 8
                    code |= raw_data[src_index]
                    src_index += 1
            else:
                if code >= 0x80:
                    back = ((code & 0x1F) << 8) | raw_data[src_index]
                    src_index += 1
                    code = (code >> 5) & 3
                else:
                    code2 = code & 0x60
                    if code2 == 0x20:
                        back = (code >> 2) & 7
                        code &= 3
                    else:
                        code &= 0x1F
                        if code2 == 0x40:
                            back = raw_data[src_index]
                            src_index += 1
                            code += 4
                        else:
                            back = (code << 8) | raw_data[src_index]
                            src_index += 1
                            code = raw_data[src_index]
                            src_index += 1

                            if code == 0xFE:
                                code = raw_data[src_index]
                                src_index += 1
                                code <<= 8
                                code |= raw_data[src_index]
                                src_index += 1
                                code += 0x102
                            elif code == 0xFF:
                                code = raw_data[src_index]
                                src_index += 1
                                code <<= 8
                                code |= raw_data[src_index]
                                src_index += 1
                                code <<= 8
                                code |= raw_data[src_index]
                                src_index += 1
                                code <<= 8
                                code |= raw_data[src_index]
                                src_index += 1
                            else:
                                code += 4
                back += 1
                code += 3

        length = code
        if dst_index + length > target_length:
            length = target_length - dst_index

        code -= length

        if back > 0:
            # because of the way the compression works, you can't actually simplify this
            # since it can be used to duplicate one byte a bunch of times
            for i in range(length):
                decompressed[dst_index + i] = decompressed[dst_index + i - back]
            dst_index += length
        else:
            decompressed[dst_index:dst_index + length] = raw_data[src_index:src_index + length]
            src_index += length
            dst_index += length

    return decompressed

def him4(offset, file_handler, asset_dir, file_id):
    f = file_handler

    f.seek(offset)
    compressed_size = read_int(f)
    original_size = read_int(f)

    if compressed_size > 0:
        raw_data = f.read(compressed_size)
        data = decompress(raw_data, original_size)
    else:
        data = f.read(original_size)

    log.info('Unpacking ' + str(file_id))
    log.debug('offset: %s, asset_dir: %s, file_id: %s, compressed_size: %s, original_size: %s',
        offset, asset_dir, file_id, compressed_size, original_size)

    extension = get_extension(data)
    file_path = os.path.join(asset_dir, str(file_id) + '.' + extension)
    with open(file_path, 'wb') as new_file:
        new_file.write(data)

def him5(header, file_handler, folder_dir):
    f = file_handler

    f.seek(header['offset'])
    header['compressed_size'] = read_int(f)
    header['original_size'] = read_int(f)
    #header['file_type'] = read_byte(f)

    if header['compressed_size'] > 0:
        raw_data = f.read(header['compressed_size'])
        data = decompress(raw_data, header['original_size'])
    else:
        data = f.read(header['original_size'])

    log.info('Unpacking ' + header['filename'])
    log.debug('Header: %s', header)

    extension = get_extension(data)
    file_path = os.path.join(folder_dir, header['filename'] + '.' + extension)
    with open(file_path, 'wb') as new_file:
        new_file.write(data)        
