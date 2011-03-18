#!/usr/bin/python
#
# January 28, 2011
#

from datetime import tzinfo, timedelta, datetime
import time
import calendar
import httplib
import sys
import os

###

ZERO = timedelta(0)

class UTC(tzinfo):
	def utcoffset(self, dt):
		return ZERO

	def tzname(self, dt):
		return "UTC"

	def dst(self, dt):
		return ZERO

utc = UTC()

# A class capturing the platform's idea of local time.

import time as _time

STDOFFSET = timedelta(seconds = -_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds = -_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0

Local = LocalTimezone()

###

conf_hostname = None
conf_set = False

if len(sys.argv) == 1:
	print "Usage: %s [-s] <hostname>" % sys.argv[0]
	sys.exit(1)

if len(sys.argv) == 3 and sys.argv[1] == "-s":
	conf_set = True
	conf_hostname = sys.argv[2]
else:
	conf_hostname = sys.argv[1]

c = httplib.HTTPConnection(conf_hostname)
c.request("HEAD", "/")
r = c.getresponse()
header = r.getheaders()
for key, value in header:
	if key == "date":
		date_string = value
		break

# time.mktime() assumes the tuple is in local time,
# calendar.timegm() assumes it's in UTC
time_there = calendar.timegm(time.strptime(date_string, "%a, %d %b %Y %H:%M:%S %Z"))
time_here = calendar.timegm(time.gmtime())
dt = datetime.fromtimestamp(time_there, utc)
print "%s [%d]" % (dt.astimezone(Local).strftime("%Y-%m-%d %H:%M:%S"), time_there - time_here)
if conf_set == True:
	os.system("date %s" % dt.astimezone(Local).strftime("%m%d%H%M.%S"))

