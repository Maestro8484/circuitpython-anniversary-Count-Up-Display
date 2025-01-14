# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
This example will figure out the current local time using the internet, and
then draw out a count-up clock since an event occurred!
Once the event is happening, a new graphic is shown
Additionally displays total days, minutes and seconds elapsed since the event
All large numbers are formatted with commas for readability
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
# Add comma to the glyphs we need to load
big_font.load_glyphs(b'0123456789,') # pre-load glyphs for fast printing

years_position = (118, 10)
days_position = (7,36)
hours_position = (122, 35)
minutes_position = (30, 60)
total_days_position = (30, 85)    # Position for total days display
total_minutes_position = (30, 110) # Position for total minutes display
total_seconds_position = (30, 135) # Position for total seconds display
text_color = 0x418fde    #0x66a3ff light blue

text_areas = []
# Add text areas for all displays including total days
for pos in (years_position, days_position, hours_position, minutes_position, 
            total_days_position, total_minutes_position, total_seconds_position):
    textarea = Label(big_font, text='  ')
    textarea.x = pos[0]
    textarea.y = pos[1]
    textarea.color = text_color
    pyportal.splash.append(textarea)
    text_areas.append(textarea)
refresh_time = None

def format_with_commas(number):
    """Format a number with commas as thousand separators"""
    return "{:,}".format(number)

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
    
    # Calculate total seconds first
    total_seconds = int(since + (years_since * 31536000))  # 31536000 = seconds in a year
    
    # Calculate total minutes from total seconds
    total_minutes = int(total_seconds // 60)
    
    # Calculate total days from total seconds
    total_days = int(total_seconds // 86400)  # 86400 = seconds in a day
    
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
    print("Total days elapsed: %s" % format_with_commas(total_days))
    print("Total minutes elapsed: %s" % format_with_commas(total_minutes))
    print("Total seconds elapsed: %s" % format_with_commas(total_seconds))
    
    # Format all numbers with commas
    text_areas[0].text = '{}'.format(years_since)  # years typically won't need commas
    text_areas[1].text = '{}'.format(days_since)   # days within a year won't need commas
    text_areas[2].text = '{}'.format(hours_since)  # hours won't need commas
    text_areas[3].text = '{}'.format(mins_since)   # minutes won't need commas
    text_areas[4].text = format_with_commas(total_days)     # format total days with commas
    text_areas[5].text = format_with_commas(total_minutes)  # format total minutes with commas
    text_areas[6].text = format_with_commas(total_seconds)  # format total seconds with commas

    # update every 10 seconds
    time.sleep(10)
