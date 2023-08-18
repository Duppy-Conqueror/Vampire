# search.py
import os
import json

from venue import get_venue_list
from booking import Booking

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Search for a venue by the venue code
# Returns the infomation of the venue (List)
def searchVenue(venue_code:str):

	venue_list = get_venue_list()
	venue_info = []
	for i in range(len(venue_list)):
		if venue_code == venue_list[i][1]:
			venue_info = venue_list[i]
	return venue_info

# Search for a booking by the booking ID
# Returns a booking object, None otherwise
def searchBooking(id: str):
	
	with open("data/bookings.json",'r') as f:
		data = json.load(f)
	bookings = data['bookings']

	for _booking in bookings:
		if id == _booking.get('id'):
			return Booking(_booking.get('date'),_booking.get('begin'),_booking.get('end'),_booking.get('venue'),_booking.get('user'),_booking.get('id'))
	return None