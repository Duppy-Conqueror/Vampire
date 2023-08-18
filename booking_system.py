# booking_system.py
import os
import json
import config
import valid_datetime
import search
import id
from list_bookings import listBookings

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Check whether the booking can be inserted without any error
# Expected input: YYYY-mm-dd, HH:MM, HH:MM, venue_code, user
def valid_insert(date:str,begin:str,end:str,venue_code:str,user:str) -> str:

	# Part 1: Check user inputs

	# 1.1: Check the validity of the date
	if valid_datetime.valid_date(date) == False:
		return config.INVALID_DATE
  
	# 1.2: Check the validity of the begin and end times
	if valid_datetime.valid_time(begin) == False or valid_datetime.valid_time(end) == False:
	    return config.INVALID_TIME
  
	# 1.3: Check the validity of the time interval
	if valid_datetime.valid_interval(begin,end) == False:
		return config.INVALID_INTERVAL

	# 1.4 Check if the date has passed
	if valid_datetime.past_check(date, begin) == True:
		return config.PASSED

	# 1.5 Check if the date is 14 days after today
	if valid_datetime.tooFarAhead(date, begin) == True:
		return config.TOO_FAR_AHEAD

	# 1.6: Check if the venue exists
	# Extract the venue info for further operations
	venue_info = search.searchVenue(venue_code)
	if venue_info == []:
		return config.INVALID_CODE

	# 1.7: Check the length of the user's name
	if len(user) > 20:
		return config.TOO_LONG
  
	# Part 2: Object extractions and timeclash checking

	# Part 2.1: Search for bookings on the same day
	existingBookings = listBookings(date)
  
	# Part 2.2: Timeclash checking
	if (len(existingBookings) > 0):
		for booking in existingBookings:
			# Yes: Check any timeclashes at the same venue
			if booking.venue == venue_info[0]:
				if valid_datetime.timeclash([booking.begin,booking.end],[begin,end]) == True:
					return config.TIMECLASH

	# Booking insertion is valid, return CONFIRM
	return config.CONFIRM

# Booking insertion (Called only when valid_insert() returns AVAILABLE)
# Returns booking ID for reference
# Returns None
def insertBooking(date:str,begin:str,end:str,venue_code:str,user:str):
	# Extract the venue info for further operations
	venue_info = search.searchVenue(venue_code)

	# Assign a booking ID
	id_ = id.generateID(date,begin,end,venue_code)

	# Create a new booking 
	newBooking = {'date': f'{date}', 'begin': f'{begin}', 'end': f'{end}', 'venue': f'{venue_info[0]}', 'user': f'{user}', 'id': f'{id_}'}

	# File access and overwriting
	with open('data/bookings.json', 'r') as f:
		data = json.load(f)
	bookings = data["bookings"]
	bookings.append(newBooking)
	bookings.sort(key= lambda x: x["id"])
	data = {"bookings": bookings}
	with open('data/bookings.json', 'w') as f:
		json.dump(data, f, indent=4)

	# Check if the new booking exists in the json file
	# If yes, return ID
	# If no, return UNKNOWN_ERROR
	temp = search.searchBooking(id_)
	if temp == None:
		return config.UNKNOWN_ERROR
	else:
		return [config.INSERT_SUCCESS, id_]

# Check whether a booking with the input ID exists
# Returns an integer indicating the index of the booking in the list
def valid_delete(id: str):
  booking = search.searchBooking(id=id)
  if booking == None:
    return config.BOOKING_NOT_FOUND
  else:
    return booking

# Booking deletion (Called only when valid_delete() returns an existing booking)
def deleteBooking(id: str):
	index = -1
	with open("data/bookings.json") as f:
		data = json.load(f)
	bookings = data["bookings"]
	for i in range(len(bookings)):
		if bookings[i].get("id") == id:
			index = i
	bookings.pop(index)
	data = {"bookings": bookings}
	with open('data/bookings.json', 'w') as f:
		json.dump(data, f, indent=4)

	# Check if the booking no longer exists in the json file
	# If yes, return DELETE_SUCCESS
	# If no, return UNKNOWN_ERROR
	temp = search.searchBooking(id)
	if temp != None:
		return config.UNKNOWN_ERROR
	else:
		return config.DELETE_SUCCESS