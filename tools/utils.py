import datetime
from dateutil import parser
import pytz

TIMEZONE_STR = 'Europe/Brussels'
TIMEZONE = pytz.timezone(TIMEZONE_STR)
UTC = pytz.timezone('UTC')

def str_to_gtime(datetime_str):
    """ Convert all datetime strings to a common format with timezone """
    d = parser.parse(datetime_str)
    try:
        # add timezone to degage strings
        d = TIMEZONE.localize(d)
    except:
        pass
    d = d.strftime("%Y-%m-%dT%H:%M:%S%z")
    return d

def str_to_degage(datetime_str):
    """ Convert datetime str in google format to degage format """
    d = parser.parse(datetime_str)
    return d.strftime("%Y-%m-%d %H:%M")

def str_to_rfc3339(datetime_str):
    """ format used in google API... needs UTC """
    d = parser.parse(datetime_str)
    utc = d.astimezone(UTC)
    return utc.strftime("%Y-%m-%dT%H:%M:%SZ")

def is_future(datetime_str):
    now = datetime.datetime.now().astimezone(TIMEZONE)
    d = parser.parse(datetime_str)
    return (d-now).total_seconds() > -60*60*2
