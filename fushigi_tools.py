#!/usr/bin/env python3

import argparse, os
import logging as log
from fushigi import *

log.basicConfig(level=log.WARNING) # change to warning when finished

# Some of the variable naming in this is a bit fucky, since I didn't initially realize that Him5 included a hashmap

# Config

argparser = argparse.ArgumentParser(description='Tools for ふしぎ電車 archive files')
argparser.add_argument('command', help='command to perform on the targets',
                       choices=['format', 'metadata', 'unpack', 'repack'])
argparser.add_argument('files', metavar='target', nargs='+', help='source file or directory to act upon')
argparser.add_argument('--output', dest='output', default='./asset_dump', help='directory containing output files, defaults to ./asset_dump')

args = argparser.parse_args()

# Body

def process_file(file_path):
    log.info('Processing file: ' + file_path)
    basename = os.path.basename(file_path)
    name, extension = os.path.splitext(basename)

    if extension == '.HXP':
        print('Processing: ' + basename)

        with open(file_path, 'rb') as main_file:
            file_format, metadata = parser.file_info(main_file)
            command = args.command

            if command == 'format':
                print('File Format:', file_format)
            elif command == 'metadata':
                util.print_list(metadata)
            elif command == 'unpack':
                asset_dir = os.path.join(args.output, basename + ';' + file_format)
                util.ensure_dir_exists(asset_dir)

                if len(os.listdir(asset_dir)) > 0:
                    response = input('Directory %s already exists. Empty and re-unpack? (y/N)'.format(asset_dir))
                    if response.lower() in ('y', 'no'):
                        util.clear_dir_contents(asset_dir)
                    else:
                        return

                if file_format == 'Him4':
                    for index, offset in enumerate(metadata):
                        unpacker.him4(offset, main_file, asset_dir, index)
                elif file_format == 'Him5':
                    for folder in metadata:
                        for file in folder['files']:
                            unpacker.him5(file, main_file, asset_dir)

    else:
        log.error('unsupported extension: %s', extension)
        return

def process_folder(path):
    log.info('Processing folder: ' + path)
    # this is gross and bad i'm sorry
    input_dir, basename = os.path.split(path[:-1])
    filename, file_format = basename.split(';')
    name, extension = os.path.splitext(filename)

    if extension == '.HXP':
        print('Processing: ' + basename)

        output_path = os.path.join(args.output, filename)
        if os.path.exists(output_path):
            response = input('File %s already exists. Remove and re-pack? (y/N)'.format(output_path))
            if response.lower() in ('y', 'no'):
                os.remove(output_path)
            else:
                return

        contents = sorted([os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])

        if file_format == 'Him4':
            repacker.him4(contents, output_path)
        else:
            repacker.him5(contents, output_path)

    else:
        log.error('unsupported extension: %s', extension)
        return

for path in args.files:
    is_file = os.path.isfile(path)
    is_dir = os.path.isdir(path)
    if not (is_file or is_dir):
        log.warn('%s does not exist; skipping', path)
    elif is_file:
        if args.command in ('format', 'metadata', 'unpack'):
            process_file(path)
        else:
            log.error('%s is a file; please specify a directory to repack')
    else: # is_dir
        if args.command in ('format', 'metadata', 'unpack'):
            files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            for filename in files:
                process_file(filename)
        else:
            process_folder(path)
