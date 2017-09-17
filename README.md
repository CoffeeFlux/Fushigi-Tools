# Fushigi Tools

Translation tools for ふしぎ電車, a weird old doujin denpa nukige

# Usage

Usage format is as follows:

```
fushigi_tools.py [command] [target] ... --asset_dir [asset_dump]
```

The command can either be:

* format - lists the file format (Him4 and Him5 supported)
* metadata - lists metadata regarding the files
* unpack - dumps archived files into a subdirectory
* repack - NONFUNCTIONAL - takes a folder and repacks its assets

The target can be a single or series of files or folders. If a folder is specified, the program will attempt to extract every .HXP file within it.

The asset directory is an optional argument that will change where the files are dumped during either unpacking or repacking. If left out of the command, it will default to `./asset_dir`.
