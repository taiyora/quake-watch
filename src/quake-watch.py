import humanize
import json
import requests
import time
from asciimatics.screen import Screen
from datetime import datetime
from dateutil import tz

update_freq = 5 # minutes

# Specify where each screen element should go
ui = {
    'screen': { 'w': 200, 'h': 105 },

    'error' : { 'x': 0, 'y': 0 },
    'header': { 'x': 0, 'y': 1 },

    'quake-list': { 'y':   5 },
    'time-abs'  : { 'x':   0 }, # Absolute time
    'time-ago'  : { 'x':  27 }, # Relative time
    'locality'  : { 'x':  45 },
    'magnitude' : { 'x':  85 },
    'mmi'       : { 'x':  95 },
    'depth'     : { 'x': 105 },
    'quality'   : { 'x': 117 }
}

def printError(screen, message):
    screen.print_at(message, ui['error']['x'], ui['error']['y'], Screen.COLOUR_RED, Screen.A_BOLD)

def getLatestQuakes(screen):
    """Retrieves the latest 100 earthquakes from the GeoNet API."""

    try:
        quakes = requests.get('http://api.geonet.org.nz/quake?MMI=-1')
        quakes.raise_for_status()

    except requests.exceptions.HTTPError        as e: printError(screen, 'HTTP Error: '        + str(e))
    except requests.exceptions.ConnectionError  as e: printError(screen, 'Connection Error: '  + str(e))
    except requests.exceptions.Timeout          as e: printError(screen, 'Timeout: '           + str(e))
    except requests.exceptions.RequestException as e: printError(screen, 'Request Exception: ' + str(e))

    else:
        # Reformat the retrieved earthquake data into a more easy to use and sortable structure
        quakes_json = quakes.json()
        quakes_formatted = {}

        for quake in quakes_json['features']:
            quakes_formatted[quake['properties']['publicID']] = quake # Earthquakes will be indexed by their Public ID
        
        return quakes_formatted

    return {} # Return an empty dictionary if an error occurred, since the program will continue to run fine

def printQuake(screen, quake, n):
    y = ui['quake-list']['y'] + n

    # Convert the time that the earthquake occurred into a human-readable format (e.g. "5 minutes ago")
    current_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    time_formatted = datetime.strptime(quake['properties']['time'], current_format)
    time_humanized = humanize.naturaltime(datetime.utcnow() - time_formatted)

    # Also get the absolute time that the earthquake occurred (in the local timezone)
    tz_from  = tz.gettz('UTC')
    tz_to    = tz.gettz('Pacific/Auckland')
    time_abs = str(time_formatted.replace(tzinfo=tz_from).astimezone(tz_to).ctime())

    locality  =           quake['properties']['locality']
    magnitude = str(round(quake['properties']['magnitude'], 2))
    mmi       = str(      quake['properties']['mmi'])
    depth     = str(round(quake['properties']['depth'],     2))
    quality   =           quake['properties']['quality']

    # Justify numbers to the right
    magnitude = ((9 - len(magnitude)) * ' ') + magnitude
    mmi       = ((5 - len(mmi))       * ' ') + mmi
    depth     = ((9 - len(depth))     * ' ') + depth

    screen.print_at(time_abs,       ui['time-abs'] ['x'], y, Screen.COLOUR_BLACK, Screen.A_BOLD)
    screen.print_at(time_humanized, ui['time-ago'] ['x'], y)
    screen.print_at(locality,       ui['locality'] ['x'], y)
    screen.print_at(magnitude,      ui['magnitude']['x'], y)
    screen.print_at(mmi,            ui['mmi']      ['x'], y)
    screen.print_at(depth,          ui['depth']    ['x'], y)
    screen.print_at(quality,        ui['quality']  ['x'], y, Screen.COLOUR_BLACK, Screen.A_BOLD)

def main(screen):
    # Shorter variable names to make code cleaner
    hx = ui['header']['x']
    hy = ui['header']['y']
    cb = Screen.COLOUR_BLACK
    ab = Screen.A_BOLD

    while True:
        # Clear the screen
        screen.move(0, 0)
        screen.draw(ui['screen']['w'], ui['screen']['h'], char=' ')

        # Display the header
        screen.print_at('Last update: ' + str(datetime.now().strftime('%H:%M:%S')), hx, hy, cb, ab)

        screen.print_at('-' * ui['screen']['w'],           hx, hy + 1, cb, ab)
        screen.print_at('Time occurred', ui['time-abs'] ['x'], hy + 2)
        screen.print_at('Time ago',      ui['time-ago'] ['x'], hy + 2)
        screen.print_at('Locality',      ui['locality'] ['x'], hy + 2)
        screen.print_at('Magnitude',     ui['magnitude']['x'], hy + 2)
        screen.print_at('| MMI',         ui['mmi']      ['x'], hy + 2)
        screen.print_at('    Depth',     ui['depth']    ['x'], hy + 2)
        screen.print_at('Quality',       ui['quality']  ['x'], hy + 2)
        screen.print_at('-' * ui['screen']['w'],           hx, hy + 3, cb, ab)

        # Display the latest earthquakes
        quakes_latest = getLatestQuakes(screen)

        n = 0
        for q_id in quakes_latest:
            printQuake(screen, quakes_latest[q_id], n)
            n += 1

        screen.refresh()
        time.sleep(update_freq * 60)

if __name__ == '__main__':
    Screen.wrapper(main)
