# valid_datetime.py
import datetime as dt
from config import tzoffset

# ========== Date-related functions below ==========
def get_date_string(year:str, month:str, day:str) -> str:
	return str(dt.date(year=int(year), month=int(month), day=int(day)))

# Expected input: YYYY-mm-dd
def date_to_tuple(date:str):
	return int(date[0:4]), int(date[5:7]), int(date[8:10])

def valid_date(year:str, month:str, day:str) -> bool:

	# Check if inputs are integers. Return False if any of them are not
	if not (year.isdigit() and month.isdigit() and day.isdigit()):
		return False

	year = int(year)
	month = int(month)
	day = int(day)

	# Check if year is in range [1,9999], month is in range [1,12], day is in range [1,31]
	# Return False if any of them are not in their corresponding range
	if year < 1 or year > 9999:
		return False
	if month < 1 or month > 12:
		return False
	if day < 1 or day > 31:
		return False
	
	# Determine if the year is a leap year
	is_leap: bool = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

	# Big months: return True as day is in [1,31]
	if month in [1, 3, 5, 7, 8, 10, 12]:
		return True
	# Small months (except Feburary): return True if day is in [1,30]
	elif month in [4, 6, 9, 11]:
		return day < 31
	# Feburary: return True if (It is a leap year and day is in [1,29]) or (It is not a leap year and day is in [1,28])
	else:
		return (is_leap == True and day < 30) or (is_leap == False and day < 29)
	
# ========== Date-related functions above ==========
# ========== Time-related functions below ==========

SAME = 0
BEFORE = -1
AFTER = 1

def get_time_string(hour:str, minute:str) -> str:
	if (len(hour) == 1):
		hour = "0" + hour
	if (len(minute) == 1):
		minute = "0" + minute
	return hour + ":" + minute

# Expected input: HH:MM
def time_to_tuple(time:str):
	return int(time[0:2]), int(time[3:5])

# Expected input: HH:MM
def valid_time(hour:str, minute:str):

	if not (hour.isdigit() and minute.isdigit()):
		return False

	hour = int(hour)
	minute = int(minute)
	# Return False if:
	# 1. hour is not in [0,24]
	# 2. minute is not in [0,59]
	if hour < 0 or hour > 24 or minute < 0 or minute > 59:
		return False

	# Special case: 24:00 (Only for end time)
	if hour == 24 and minute != 0:
		return False

# Comapare two times
# Reason for not using datetime.time: 24:00 is a possible input, which datetime.time does not allow
def compare(time1:str, time2:str):
	time1_hour, time1_minute = time_to_tuple(time1)
	time2_hour, time2_minute = time_to_tuple(time2)

	if time1_hour < time2_hour:
		return BEFORE
	elif time1_hour > time2_hour:
		return AFTER

	# time1_hour == time2_hour
	else:
		if time1_minute < time2_minute:
			return BEFORE
		elif time1_minute > time2_minute:
			return AFTER
		else:
			return SAME

# Expected inputs: HH:MM, HH:MM
def valid_interval(begin:str,end:str):
	return compare(begin,end) == BEFORE

# Accept two lists with length 2 for each, storing strings 
def timeclash(existingInterval, inputInterval):
	exist_begin, exist_end = existingInterval
	input_begin, input_end = inputInterval
  
	# Return False if:
	# 1. Two intervals are completely disjoint (Completely before or after)
	# 2. Two Intervals have only one intersection: One interval's begin time and another one interval's end time
	if (compare(input_begin, exist_begin) == BEFORE and compare(input_end, exist_begin) == BEFORE) or (compare(input_begin, exist_end) == AFTER and compare(input_end, exist_end) == AFTER):
		return False
	if (compare(input_begin, exist_begin) == BEFORE and compare(input_end, exist_begin) == SAME) or (compare(input_begin, exist_end) == SAME and compare(input_end, exist_end) == AFTER):
		return False
	return True

# ========== Time-related functions above ==========
# ====== Datetime-related functions below =======

# Return True if the booking datetime has passed
def past_check(date:str, time:str):
	year, month, day = date_to_tuple(date)
	hour, minute = time_to_tuple(time)
	return (dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(hours=tzoffset)).replace(tzinfo=None) > dt.datetime(year=year, month=month, day=day, hour=hour, minute=minute)

# Return True if the booking date is 14 days after today
def future_check(date:str, time:str):
	year, month, day = date_to_tuple(date)
	hour, minute = time_to_tuple(time)
	return dt.datetime(year=year, month=month, day=day, hour=hour, minute=minute) > (dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(days=14, hours=tzoffset)).replace(tzinfo=None)