import humanize
import json
import requests
import time
from asciimatics.screen import Screen
from datetime import datetime
from dateutil import tz

mmi_threshold   = -1
display_n       = 20
update_freq     =  5 # minutes
decimal_prec    =  1
highlight_depth = False
highlight_loc   = ':^)'

# Specify where each screen element should go
ui = {
    'screen': { 'w': 200, 'h': 105 },

    'error' : { 'x': 0, 'y': 0 },
    'header': { 'x': 0, 'y': 1 },

    'quake-list': { 'y':   5 },
    'time-abs'  : { 'x':   0 }, # Absolute time
    'time-ago'  : { 'x':  27 }, # Relative time
    'locality'  : { 'x':  44 },
    'magnitude' : { 'x':  85 },
    'mmi'       : { 'x':  95 },
    'depth'     : { 'x': 103 },
    'quality'   : { 'x': 116 }
}

def printError(screen, message):
    screen.print_at(message, ui['error']['x'], ui['error']['y'], Screen.COLOUR_RED, Screen.A_BOLD)

def getLatestQuakes(screen):
    """Retrieves the latest 100 earthquakes from the GeoNet API."""

    try:
        quakes = requests.get('http://api.geonet.org.nz/quake?MMI=' + str(mmi_threshold))
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

def getColor(value, type='magnitude'):
    if type == 'magnitude':
        if value < 3: return Screen.COLOUR_BLACK
        if value < 4: return Screen.COLOUR_WHITE
        if value < 5: return Screen.COLOUR_BLUE
        if value < 6: return Screen.COLOUR_CYAN
        if value < 7: return Screen.COLOUR_GREEN
        if value < 8: return Screen.COLOUR_YELLOW
        if value < 9: return Screen.COLOUR_RED
        return Screen.COLOUR_MAGENTA

    if type == 'depth':
        if not highlight_depth:
            return Screen.COLOUR_BLACK

        if value >= 200: return Screen.COLOUR_BLACK
        if value >= 100: return Screen.COLOUR_WHITE
        if value >= 50:  return Screen.COLOUR_BLUE
        if value >= 25:  return Screen.COLOUR_CYAN
        if value >= 10:  return Screen.COLOUR_GREEN
        if value >= 5:   return Screen.COLOUR_YELLOW
        if value >= 3:   return Screen.COLOUR_RED
        return Screen.COLOUR_MAGENTA

    return Screen.COLOUR_WHITE

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
    magnitude = str(round(quake['properties']['magnitude'], decimal_prec))
    mmi       = str(      quake['properties']['mmi'])
    depth     = str(round(quake['properties']['depth'], decimal_prec))
    quality   =           quake['properties']['quality']

    # Justify numbers to the right
    magnitude = (( 9 - len(magnitude)) * ' ') + magnitude
    mmi       = (( 5 - len(mmi))       * ' ') + mmi
    depth     = ((10 - len(depth))     * ' ') + depth

    # Print the quality in red if the earthquake data has been tagged as deleted
    locality_col  = Screen.COLOUR_YELLOW if highlight_loc in locality.lower() else Screen.COLOUR_WHITE
    locality_bold = Screen.A_BOLD        if highlight_loc in locality.lower() else Screen.A_NORMAL

    quality_col  = Screen.COLOUR_RED if quality == 'deleted' else Screen.COLOUR_BLACK
    quality_bold = Screen.A_NORMAL   if quality == 'deleted' else Screen.A_BOLD # We don't want the red text to be too glaring

    screen.print_at(time_abs,       ui['time-abs'] ['x'], y, Screen.COLOUR_BLACK, Screen.A_BOLD)
    screen.print_at(time_humanized, ui['time-ago'] ['x'], y)
    screen.print_at(locality,       ui['locality'] ['x'], y, locality_col, locality_bold)
    screen.print_at(magnitude,      ui['magnitude']['x'], y, getColor(quake['properties']['magnitude']),      Screen.A_BOLD)
    screen.print_at(mmi,            ui['mmi']      ['x'], y, getColor(quake['properties']['mmi']),            Screen.A_BOLD)
    screen.print_at(depth,          ui['depth']    ['x'], y, getColor(quake['properties']['depth'], 'depth'), Screen.A_BOLD)
    screen.print_at(quality,        ui['quality']  ['x'], y, quality_col, quality_bold)

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

        # Display extra information if settings are not at their defaults
        if update_freq != 5:
            screen.print_at(str(update_freq) + 'm', hx + 22, hy, Screen.COLOUR_GREEN, ab)

        if mmi_threshold != -1:
            screen.print_at('MMI >= ' + str(mmi_threshold), hx + 27, hy, Screen.COLOUR_BLUE, ab)

        screen.print_at('-' * ui['screen']['w'],           hx, hy + 1, cb, ab)
        screen.print_at('Time occurred', ui['time-abs'] ['x'], hy + 2)
        screen.print_at('Time ago',      ui['time-ago'] ['x'], hy + 2)
        screen.print_at('Locality',      ui['locality'] ['x'], hy + 2)
        screen.print_at('Magnitude',     ui['magnitude']['x'], hy + 2)
        screen.print_at('| MMI',         ui['mmi']      ['x'], hy + 2)
        screen.print_at('Depth (km)',    ui['depth']    ['x'], hy + 2)
        screen.print_at('Quality',       ui['quality']  ['x'], hy + 2)
        screen.print_at('-' * ui['screen']['w'],           hx, hy + 3, cb, ab)

        # Display the latest earthquakes
        quakes_latest = getLatestQuakes(screen)

        n = 0
        for q_id in quakes_latest:
            printQuake(screen, quakes_latest[q_id], n)
            
            n += 1
            if n == display_n:
                break

        screen.refresh()
        time.sleep(update_freq * 60)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-m', '--mmi-threshold', type=int,\
        help='The MMI value to query GeoNet with. Default is -1 (get all earthquakes)')

    parser.add_argument('-n', '--display-n', type=int,\
        help='How many earthquakes to display at a time. Default is 20.')

    parser.add_argument('-u', '--update-frequency', type=int,\
        help='How often to update the feed, in minutes. Default is 5 minutes.')

    parser.add_argument('-d', '--decimal-precision', type=int,\
        help='How many decimal places to show for magnitude and depth values. Default is 1, max is 6.')

    parser.add_argument('-hd', '--highlight-depth', action='store_true',\
        help='Turn on highlighting of depth values.')

    parser.add_argument('-hl', '--highlight-locality', type=str,\
        help='Specify a location to highlight if an earthquake occurs there.')

    args = parser.parse_args()

    mmi_threshold   = args.mmi_threshold      if args.mmi_threshold      else mmi_threshold
    display_n       = args.display_n          if args.display_n          else display_n
    update_freq     = args.update_frequency   if args.update_frequency   else update_freq
    decimal_prec    = args.decimal_precision  if args.decimal_precision  else decimal_prec
    highlight_depth = args.highlight_depth    if args.highlight_depth    else highlight_depth
    highlight_loc   = args.highlight_locality if args.highlight_locality else highlight_loc

    if decimal_prec > 6:
        decimal_prec = 6

    highlight_loc = highlight_loc.lower()

    Screen.wrapper(main)
