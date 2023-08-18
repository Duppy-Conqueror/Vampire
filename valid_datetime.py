# valid_datetime.py
import datetime

from config import tzoffset

# ========== Date-related functions below ==========
# Expected input: YYYY-mm-dd
def dateConverter(date:str):
	return [int(date[0:4]),int(date[5:7]),int(date[8:10])]

def valid_date(date:str):

	# Attempt to convert string to datetime object
	try:
		datetime.datetime.strptime(date, '%Y-%m-%d')
		return True
	except ValueError:
		return False

# ========== Date-related functions above ==========
# ========== Time-related functions below ==========

SAME = 0
BEFORE = -1
AFTER = 1

# Expected input: HH:MM
def timeConverter(time:str):
	return [int(time[0:2]),int(time[3:5])]

# Expected input: HH:MM
def valid_time(time:str):

	if len(time) != 5:
		return False

	for i in range(len(time)):
		if i == 2:
			if time[i] != ":":
				return False
		else:
			if time[i].isnumeric() == False:
				return False

	hour = timeConverter(time)[0]
	minute = timeConverter(time)[1]

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
	time1_hour = timeConverter(time1)[0]
	time1_minute = timeConverter(time1)[1]
	time2_hour = timeConverter(time2)[0]
	time2_minute = timeConverter(time2)[1]

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
	exist_begin = existingInterval[0]
	exist_end = existingInterval[1]
	input_begin = inputInterval[0]
	input_end = inputInterval[1]
  
	# Return False if:
	# 1. Two intervals are completely disjoint (Completely before or after)
	# 2. Two Intervals have only one intersection: One interval's begin time and another one interval's end time
	if (compare(input_begin, exist_begin) == BEFORE and compare(input_end, exist_begin) == BEFORE) or (compare(input_begin, exist_end) == AFTER and compare(input_end, exist_end) == AFTER):
		return False
	if (compare(input_begin, exist_begin) == BEFORE and compare(input_end, exist_begin) == SAME) or (compare(input_begin, exist_end) == SAME and compare(input_end, exist_end) == AFTER):
		return False
	return True

# ========== Time-related functions above ==========
# ====== Datetimeime-related functions below =======

# Return True if the booking datetime has passed
def past_check(date:str, time:str):
	year = dateConverter(date)[0]
	month = dateConverter(date)[1]
	day = dateConverter(date)[2]
	hour = timeConverter(time)[0]
	minute = timeConverter(time)[1]
	return (datetime.datetime.utcnow() + datetime.timedelta(hours=tzoffset)) > datetime.datetime(year,month,day,hour,minute)

# Return True if the booking date is 14 days after today
def tooFarAhead(date:str, time:str):
	year = dateConverter(date)[0]
	month = dateConverter(date)[1]
	day = dateConverter(date)[2]
	hour = timeConverter(time)[0]
	minute = timeConverter(time)[1]
	return datetime.datetime(year,month,day,hour,minute) > (datetime.datetime.utcnow() + datetime.timedelta(days=14,hours=tzoffset))