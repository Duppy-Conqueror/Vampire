# list_bookings.py
import os
import discord
import json
import datetime
from calendar import day_name

import config
from valid_datetime import valid_date
from booking import Booking

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Returns a list of bookings (in the form of a Booking object) on a specific day
# Expected input: YYYY-mm-dd
def listBookings(date:str):
	booking_list = []

	# File access
	with open("data/bookings.json") as f:
		data = json.load(f)
	bookings = data["bookings"]

	# Extract only the bookings on that day
	for i in range(len(bookings)):
		if (bookings[i].get("date") == date):
			booking_list.append(Booking(bookings[i].get("date"),bookings[i].get("begin"),bookings[i].get("end"),bookings[i].get("venue"),bookings[i].get("user"),bookings[i].get("id")))
  
	return booking_list

# Not in use
# List today's booking
# def listBookings_today():
#   date = str(datetime.date.today())
#   return listBookings(date)

# Not in use
# List the bookings within 9 days (including today)
# def listBookings_9Days():
#   booking_list = []
  
#   booking_list = listBookings_today()
  
#   date = datetime.date.today()
#   for i in range(8):
#     date += datetime.timedelta(days=1)
#     booking_list.extend(listBookings(str(date)))
#   return booking_list

# Compose an embed page to list bookings of a day
def compose_bookings(date:str, user_input:bool = True):

	# If the date is not input by the user, skip this step
	if user_input == True:
		if valid_date(date) == False:
		  title = config.INVALID_DATE[0]
		  description = config.INVALID_DATE[1]
		  embedErr = discord.Embed(colour=config.colour_error, title=title, description=description)
		  return embedErr

	# Obtain a datetime.date object to get the day name of a date
	formatted_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
	booking_list = listBookings(date)
	title = f'{date} ({str(day_name[formatted_date.weekday()])})'
	description = ''
	if len(booking_list) == 0:
		description = '```No room bookings on this day!```'
		embedList = discord.Embed(colour=config.colour_info,title=title,description=description)
		return embedList
	else:
		description = '=' * 30 + '\n'
		for booking_ in booking_list:
			description += f'Time: {booking_.begin} - {booking_.end}\nVenue: {booking_.venue}\nUser: {booking_.user}\nID: {booking_.id}\n'
			description += '=' * 30 + '\n'
			description = f'```{description}```'
		embedList = discord.Embed(colour=config.colour_info,title=title,description=description)
		return embedList

# For bot command today()
# Return an embed page of today's bookings
def compose_today_bookings():
	date = datetime.date.today()
	oldEmbedList = compose_bookings(str(date), False)
	title = f'Today ({str(date)}, {str(day_name[date.weekday()])})'
	description = ''

	if oldEmbedList.description == '```No room bookings on this day!```':
		description = '```No room bookings today!```'
	else:
		description = oldEmbedList.description
  
	newEmbedList = discord.Embed(colour=config.colour_info,title=title,description=description)
	return newEmbedList

# For bot command showall()
# Return a list of embed pages of bookings, with one page per day
def compose_all_bookings():
	pages = []
	date = datetime.date.today()
	for i in range(14):
		embedList = compose_bookings(str(date), False)
		pages.append(embedList)
		date += datetime.timedelta(days=1)
	return pages