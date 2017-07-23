#!/usr/bin/env python3

import argparse, os
import logging as log
from fushigi import *

log.basicConfig(level=log.INFO) # change to warning when finished

# Config

argparser = argparse.ArgumentParser(description='Tools for ふしぎ電車 archive files')
argparser.add_argument('command', help='command to perform on the targets',
                       choices=['format', 'metadata', 'unpack', 'repack'])
argparser.add_argument('files', metavar='target', nargs='+', help='source file or directory to act upon')
argparser.add_argument('--output', dest='output', default='./asset_dump', help='directory containing output files, defaults to ./asset_dump')

args = argparser.parse_args()

# Body

def process_file(file_path):
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
            elif command in 'unpack':
                asset_dir = os.path.join(args.output, basename)
                util.ensure_dir_exists(asset_dir)

                if len(os.listdir(asset_dir)) > 0:
                    response = input('Directory %s already exists. Empty and re-unpack? (y/N)'.format(asset_dir))
                    if response.lower() in ('y', 'no'):
                        util.clear_dir_contents(asset_dir)
                    else:
                        return

                # folder creation and file unpacking

    else:
        log.error('unsupported extension: %s', extension)
        return

for path in args.files:
    is_file = os.path.isfile(path)
    is_dir = os.path.isdir(path)
    if not (is_file or is_dir):
        log.warn('%s does not exist; skipping', path)
    elif is_file:
        process_file(path)
    else: # is_dir
        files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        for filename in files:
            process_file(filename)
