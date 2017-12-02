import json
import requests
import time
from asciimatics.screen import Screen
from datetime import datetime

update_freq = 5 # minutes

# Specify where each screen element should go
ui = {
    'screen': { 'w': 200, 'h': 105 },

    'error' : { 'x': 0, 'y': 0 },
    'header': { 'x': 0, 'y': 1 },

    'quake-list': { 'y':  5 },
    'locality'  : { 'x':  0 },
    'magnitude' : { 'x': 40 }
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

    locality  =     quake['properties']['locality']
    magnitude = str(quake['properties']['magnitude'])

    screen.print_at(locality,  ui['locality'] ['x'], y)
    screen.print_at(magnitude, ui['magnitude']['x'], y)

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

        screen.print_at('-' * ui['screen']['w'],       hx, hy + 1, cb, ab)
        screen.print_at('Locality',  ui['locality'] ['x'], hy + 2)
        screen.print_at('Magnitude', ui['magnitude']['x'], hy + 2)
        screen.print_at('-' * ui['screen']['w'],       hx, hy + 3, cb, ab)

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
