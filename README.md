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

Get more information running:

```shell
python3 tcf2vrt.py -h
```