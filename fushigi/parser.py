from .util import * # in package
import logging as log

def file_info(file_handler):
    f = file_handler

    # Format
    log.info('file format start: 0x%08X', f.tell())
    file_format = f.read(4).decode('shift_jis')
    log.debug('file format: %s', file_format)
    folder_count = read_int(f) # in hindsight this is a terrible name, but i cba to change it
    log.debug('folder count: %s', folder_count)

    if file_format == 'Him4':
        log.info('files start: 0x%08X', f.tell())
        files = []
        for i in range(folder_count):
            files.append(read_int(f))
        log.debug('files: %s', files)

        return file_format, files

    elif file_format == 'Him5':
        # Folders
        log.info('folders start: 0x%08X', f.tell())
        folders = []
        for i in range(folder_count):
            folders.append({
                'size': read_int(f),
                'offset': read_int(f),
                'files': []
            })
        log.debug('folders: %s', folders)

        # Files
        log.info('files start: 0x%08X', f.tell())
        for folder in folders:
            folder_size = folder['size']
            if folder_size > 0:
                data = read_chunk(folder['offset'], folder_size, f)
                while data.tell() < folder_size - 1:
                    folder['files'].append({
                        'filename_length': read_byte(data), # except not actually! it's this value -6, not including the null byte
                        'offset': read('>I', 4, data), # big endian because why the fuck not
                        'filename': read_null_term_string(data)
                    })
                    #skip_if_null_byte(f) # this is a result of the hashing, but can be ignored for unpacking
        log.debug('completed folders: %s', folders)

        return file_format, folders

    log.error('unsupported file format: %s', file_format)
