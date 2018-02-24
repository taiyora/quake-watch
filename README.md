# quake-watch

Uses the GeoNet API to get the latest earthquakes that have occurred in NZ, and displays them live in a pretty CLI window.

## Install

```pip install -r requirements.txt```

## Run

```python quake-watch.py```

If using Windows, it is recommended to use a console emulator such as [cmder](http://cmder.net/) to run quake-watch. This will provide nicer colors than the default Windows terminal, and reduce display issues with the [asciimatics](https://github.com/peterbrittain/asciimatics) library that is used.

## Usage

There are several command-line arguments available:

  * ```-m``` ```--mmi-threshold``` Specifies the minimum [MMI value](https://www.geonet.org.nz/earthquake/mmi) to query GeoNet for. Default is ```-1``` (all earthquakes will be retrieved, including insignificant ones that cannot be felt)
  * ```-n``` ```--display-n``` Specifies how many earthquakes to display at a time. Default is ```20```
  * ```-u``` ```--update-frequency``` Specifies how often to update the feed, in minutes. Default is ```5 minutes```
  * ```-d``` ```--decimal-precision``` Specifies how many decimal places to show for magnitude and depth values. Default is ```1```, max is ```6```
  * ```-hd``` ```--highlight-depth``` Turns on highlighting of depth values.
  * ```-hl``` ```--highlight-locality``` Allows you to specify a location that will be highlighted in the list if an earthquake occurs there.
