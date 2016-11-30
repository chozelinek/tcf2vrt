# tcf2vrt

Converter from TCF format into VRT and inline XML.

## Requirements

- python3
- lxml

## Usage

Convert all files in input folder with extension `.tcf` into VRT files and save the output in the output folder.

```shell
python3 tcf2vrt.py -i /path/to/input/folder/ -o /path/to/output/folder -f vrt -e *.tcf
```

Get more information running `python3 tcf2vrt.py -h`:

```
usage: tcf2vrt.py [-h] -i INPUT [-o OUTPUT] [-e EXTENSION] -f {vrt,xml}

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to the input files directory.
  -o OUTPUT, --output OUTPUT
                        path to the output files directory.
  -e EXTENSION, --extension EXTENSION
                        pattern for the extension of the files.
  -f {vrt,xml}, --format {vrt,xml}
                        output format, VRT or inline XML
```