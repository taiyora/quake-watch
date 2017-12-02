# quake-watch

Uses the GeoNet API to get the latest earthquakes that have occurred in New Zealand, and displays them live in a pretty CLI window.

![quake-watch](https://github.com/jl-eiki/quake-watch/blob/master/screenshots/2017-12-03.png)

## Install

```pip install -r requirements.txt```

## Run

```python quake-watch.py```

If using Windows, it is recommended to use a console emulator such as [cmder](http://cmder.net/) to run quake-watch. This will provide nicer colors than the default Windows terminal, and reduce display issues with the [asciimatics](https://github.com/peterbrittain/asciimatics) library that is used.

## Usage

There are command-line arguments available:

  * ```-m``` ```--mmi-threshold``` Specifies the minimum [MMI value](https://www.geonet.org.nz/earthquake/mmi) to query GeoNet for. Default is ```-1``` (all earthquakes will be retrieved, including insignificant ones that cannot be felt)
