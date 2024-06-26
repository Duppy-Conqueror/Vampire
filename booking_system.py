# booking_system.py
import os
import json
import config
import valid_datetime
import venue
from list_bookings import get_booking_list
from booking import Booking

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Returns True if the booking exists in the bookings file. False otherwise
def booking_exist(id: str):
	with open("data/bookings.json",'r') as f:
		data = json.load(f)
	bookings = data['bookings']
	for booking in bookings:
		if id == booking.get('id'):
			return True
	return False

# Search for a booking by the booking ID
# Returns a Booking object, None otherwise
def get_booking(id: str):
	
	with open("data/bookings.json",'r') as f:
		data = json.load(f)
	bookings = data['bookings']

	for booking in bookings:
		if id == booking.get('id'):
			return Booking(booking['date'], booking['begin'], booking['end'], booking['venue'], booking['user'], booking['id'])
	return None

# Check whether the booking can be inserted without any error
def valid_insert(year:str, month:str, day:str, begin_hour:str, begin_minute:str, end_hour:str, end_minute:str, venue_name: str, user:str) -> str:

	# Part 1: Check user inputs

	# 1.1: Check the validity of the date
	if valid_datetime.valid_date(year, month, day) == False:
		return config.INVALID_DATE
	
	date: str = valid_datetime.get_date_string(year, month, day)

	# 1.2: Check the validity of the begin and end times
	if valid_datetime.valid_time(begin_hour, begin_minute) == False or valid_datetime.valid_time(begin_hour, begin_minute) == False:
		return config.INVALID_TIME
	
	begin: str = valid_datetime.get_time_string(begin_hour, begin_minute)
	end: str = valid_datetime.get_time_string(end_hour, end_minute)

	# 1.3: Check the validity of the time interval
	if valid_datetime.valid_interval(begin,end) == False:
		return config.INVALID_INTERVAL

	# 1.4 Check if the date has passed
	if valid_datetime.past_check(date, begin) == True:
		return config.PASSED

	# 1.5 Check if the date is 14 days after today
	if valid_datetime.future_check(date, begin) == True:
		return config.TOO_FAR_AHEAD

	# 1.6: Check if the venue exists
	# Extract the venue info for further operations
	venue_code = venue.name_to_code.get(venue_name)
	if venue_code is None:
		return config.INVALID_CODE

	# 1.7: Check the length of the user's name
	if len(user) > 20:
		return config.TOO_LONG

	# Part 2: Object extractions and timeclash checking

	# Part 2.1: Search for bookings on the same day
	existingBookings: list[Booking] = get_booking_list(valid_datetime.get_date_string(year, month, day))

	# Part 2.2: Timeclash checking
	for booking in existingBookings:
		# Yes: Check any timeclashes at the same venue
		if booking.venue == venue_name:
			if valid_datetime.timeclash((booking.begin, booking.end), (begin, end)) == True:
				return config.TIMECLASH

	# Booking insertion is valid, return CONFIRM
	return config.CONFIRM

# FORMAT OF A BOOKING ID: Year[0:1] - Month[2:3] - Day[4:5] - Begin_time[6:9] - End_time[10:13] - Venue_code[14:]
# Generate a booking ID using the user inputs (Unique as far as I can see)
# Expected input: YYYY-mm-dd, HH:MM, HH:MM, venue_code
def generate_id(date:str, begin:str, end:str, venue_code:str):
	return date[2:].replace('-','') + begin.replace(':','') + end.replace(':','') + venue_code

# Booking insertion (Called only when valid_insert() returns AVAILABLE)
# Returns the insertion success indicator and a booking ID for reference if the insertion is successful
# Returns the unknown error indicator otherwise
def insert_booking(date:str,begin:str,end:str,venue_code:str,user:str):
	# Extract the venue info for further operations
	venue_info = venue.venue_map[venue_code]

	# Assign a booking ID
	id = generate_id(date, begin, end, venue_code)

	# Create a new booking 
	newBooking = {'date': f'{date}', 'begin': f'{begin}', 'end': f'{end}', 'venue': f'{venue_info["name"]}', 'user': f'{user}', 'id': f'{id}'}

	# File access and overwriting
	with open('data/bookings.json', 'r') as f:
		data = json.load(f)
	bookings: list = data["bookings"]
	bookings.append(newBooking)
	bookings.sort(key= lambda x: x["id"])
	data = {"bookings": bookings}
	with open('data/bookings.json', 'w') as f:
		json.dump(data, f, indent=4)

	# Check if the new booking exists in the json file
	if booking_exist(id):
		return [config.INSERT_SUCCESS, id]
	else:
		return config.UNKNOWN_ERROR

# Check whether a booking with the input ID exists
# Returns an integer indicating the index of the booking in the list
def valid_delete(id: str):
	booking = get_booking(id)
	if booking is None:
		return config.BOOKING_NOT_FOUND
	else:
		return booking

# Booking deletion (Called only when valid_delete() returns an existing booking)
# Returns the deletion success indicator if the deletion is successful
# Returns the unknown error indicator otherwise
def delete_booking(id: str):
	index = -1
	with open("data/bookings.json") as f:
		data = json.load(f)
	bookings: list = data["bookings"]
	for i in range(len(bookings)):
		if bookings[i].get("id") == id:
			index = i
	bookings.pop(index)
	data = {"bookings": bookings}
	with open('data/bookings.json', 'w') as f:
		json.dump(data, f, indent=4)

	# Check if the booking no longer exists in the json file
	if not booking_exist(id):
		return config.DELETE_SUCCESS
	else:
		return config.UNKNOWN_ERROR

# Transfer expired bookings from bookings.json to bookings_past.json
# Returns the number of bookings archived
def backup_booking() -> int:
	# Get bookings from bookings.json
	with open("data/bookings.json",'r') as f:
		recent_bookings = json.load(f)
	
	recent_bookings: list = recent_bookings['bookings']
	expired_bookings = [x for x in recent_bookings if valid_datetime.past_check(x['date'], x['end'])]
	
	# Remove expired bookings from bookings.json
	recent_bookings = [x for x in recent_bookings if x not in expired_bookings]
	with open('data/bookings.json', 'w') as f:
		json.dump({"bookings": recent_bookings}, f, indent=4)

	# Add expired bookings into bookings_past.json
	with open('data/bookings_past.json', 'r+') as f: 
		past_bookings = json.load(f)
		past_bookings['bookings'] += expired_bookings
		f.seek(0)
		json.dump(past_bookings, f, indent = 4)

	return len(expired_bookings)