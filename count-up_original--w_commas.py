# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
This example will figure out the current local time using the internet, and
then draw out a count-up clock since an event occurred!
Once the event is happening, a new graphic is shown
Displays years, days, hours, and minutes elapsed since the event
"""
import time
import board
from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label

# The time of the thing!
EVENT_YEAR = 2013
EVENT_MONTH = 1
EVENT_DAY = 13
EVENT_HOUR = 18
EVENT_MINUTE = 55
# we'll make a python-friendly structure
event_time = time.struct_time((EVENT_YEAR, EVENT_MONTH, EVENT_DAY,
                               EVENT_HOUR, EVENT_MINUTE, 0,  # we don't track seconds
                               -1, -1, False))  # we dont know day of week/year or DST

# determine the current working directory
# needed so we know where to find files
cwd = ("/"+__file__).rsplit('/', 1)[0]
# Initialize the pyportal object and let us know what data to fetch and where
# to display it
pyportal = PyPortal(status_neopixel=board.NEOPIXEL,
                    default_bg=cwd+"/countup_background.bmp")

big_font = bitmap_font.load_font(cwd+"/fonts/CooperBlack-28.pcf")
big_font.load_glyphs(b'0123456789') # pre-load glyphs for fast printing

years_position = (118, 10)
days_position = (7,36)
hours_position = (122, 35)
minutes_position = (30, 60)
text_color = 0x418fde    #0x66a3ff light blue

text_areas = []
# Add text areas for the basic time display
for pos in (years_position, days_position, hours_position, minutes_position):
    textarea = Label(big_font, text='  ')
    textarea.x = pos[0]
    textarea.y = pos[1]
    textarea.color = text_color
    pyportal.splash.append(textarea)
    text_areas.append(textarea)
refresh_time = None

while True:
    # only query the online time once per hour (and on first run)
    if (not refresh_time) or (time.monotonic() - refresh_time) > 3600:
        try:
            print("Getting time from internet!")
            pyportal.get_local_time()
            refresh_time = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    now = time.localtime()
    print("Current time:", now)

    # We're going to do a little cheat here, since circuitpython can't
    # track huge amounts of time, we'll calculate the delta years here
    if now[0] > (EVENT_YEAR+1):  # we add one year to avoid half-years
        years_since = now[0] - (EVENT_YEAR+1)
        # and then set the event_time to not include the year delta
        event_time = time.struct_time((EVENT_YEAR+years_since, EVENT_MONTH, EVENT_DAY,
                                       EVENT_HOUR, EVENT_MINUTE, 0,  # we don't track seconds
                                       -1, -1, False))  # we dont know day of week/year or DST
    else:
        years_since = 0
    print(event_time)
    since = time.mktime(now) - time.mktime(event_time)
    print("Time since not including years (in sec):", since)
    
    # Calculate regular time components
    sec_since = since % 60
    since //= 60
    mins_since = since % 60
    since //= 60
    hours_since = since % 24
    since //= 24
    days_since = since % 365
    since //= 365
    years_since += since
    
    print("%d years, %d days, %d hours, %d minutes and %s seconds" %
          (years_since, days_since, hours_since, mins_since, sec_since))
    
    text_areas[0].text = '{}'.format(years_since)
    text_areas[1].text = '{}'.format(days_since)
    text_areas[2].text = '{}'.format(hours_since)
    text_areas[3].text = '{}'.format(mins_since)

    # update every 10 seconds
    time.sleep(10)
