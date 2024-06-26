# list_bookings.py
import os
import discord
import json
import datetime
from calendar import day_name

import config
from valid_datetime import valid_date, date_to_tuple
from booking import Booking

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Returns a list of bookings (in the form of a Booking object) on a specific day
# Expected input: YYYY-mm-dd
def get_booking_list(date:str) -> list[Booking]:
	# File access
	with open("data/bookings.json", 'r') as f:
		recent_bookings = json.load(f)
	recent_bookings = [x for x in recent_bookings["bookings"] if x['date'] == date]

	with open("data/bookings_past.json", 'r') as f:
		past_bookings = json.load(f)
	past_bookings = [x for x in past_bookings["bookings"] if x['date'] == date]

	# Extract only the bookings on that day
	return [Booking(x['date'], x['begin'], x['end'], x['venue'], x['user'], x['id']) for x in recent_bookings + past_bookings]

# For bot commands show(), showall() and today()
# Compose an embed page to list bookings of a day
def compose_bookings(year:str, month:str, day:str, user_input:bool = True):

	# If the date is not input by the user, skip this step
	if user_input == True:
		if valid_date(year=year, month=month, day=day) == False:
			title = config.INVALID_DATE[0]
			description = config.INVALID_DATE[1]
			embedErr = discord.Embed(colour=config.colour_error, title=title, description=description)
			return embedErr

	# Obtain a datetime.date object to get the day name of a date
	date = datetime.date(int(year), int(month), int(day))
	bookings = get_booking_list(str(date))
	title = f'{date} ({str(day_name[date.weekday()])})'
	description = ''
	if len(bookings) == 0:
		description = '```No room bookings on this day!```'
		embedList = discord.Embed(colour=config.colour_info, title=title, description=description)
		return embedList
	else:
		description = '=' * 30 + '\n'
		for b in bookings:
			description += f'Time: {b.begin} - {b.end}\nVenue: {b.venue}\nUser: {b.user}\nID: {b.id}\n'
			description += '=' * 30 + '\n'
		description = f'```{description}```'
		embedList = discord.Embed(colour=config.colour_info, title=title, description=description)
		return embedList

# For bot command today()
# Return an embed page of today's bookings
def compose_today_bookings():
	date = (datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=config.tzoffset)).date()
	date_string = str(date)
	oldEmbedList = compose_bookings(year=date_string[0:4], month=date_string[5:7], day=date_string[8:10], user_input=False)
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
	date = (datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=config.tzoffset)).date()
	for _ in range(14):
		year, month, day = date_to_tuple(str(date))
		embedList = compose_bookings(year, month, day, False)
		pages.append(embedList)
		date += datetime.timedelta(days=1)
	return pages
