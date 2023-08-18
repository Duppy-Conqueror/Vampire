# venue.py
import discord
import os
import csv

import config

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Change working directory to wherever bot.py is in
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Open venues.csv
def get_venue_list():
	venue_f = open('data/venues.csv', 'r')
	data = csv.reader(venue_f)
	venue_list = []
	next(data)             # Skip the first line
	for line in data:      # Load the csv file into a list
		venue_list.append(line)
	return venue_list

# Returns the name of the venue according to the venue_code
# Can be called only when the venue_code exist
def get_venue_name(venue_code: str):
	venue_list = get_venue_list()
	for i in range(len(venue_list)):
		if venue_code == venue_list[i][1]:
			return venue_list[i][0]
	# Nearly impossible
	return None

# For bot command venuelist()
def compose_venue_list():
	venue_list = get_venue_list()

	# Divide the list into 5 pages
	name_field = ['','','','','']
	capacity_field = ['','','','','']
	code_field = ['','','','','']

	cur = 0

	for i in range(len(venue_list)):
		if venue_list[i][0] == "1-351":
			cur = 0
		elif venue_list[i][0] == "LG3 Seminar":
			cur = 1
		elif venue_list[i][0] == "LG4-02":
			cur = 2
		elif venue_list[i][0] == "LC-01":
			cur = 3
		elif venue_list[i][0] == "LC-09":
			cur = 4
		name_field[cur] += venue_list[i][0] + '\n'
		code_field[cur] += venue_list[i][1] + '\n'
		capacity_field[cur] += venue_list[i][3] + '\n'
  
	pages = []
	for i in range(len(name_field)):
		page = discord.Embed(
		colour=config.colour_info,
		description="All the group study rooms are shown here",
		title="List of Group Study Rooms",
		)
		page.add_field(name="Venue",value=name_field[i])
		page.add_field(name="Capacity",value=capacity_field[i],inline=True)
		page.add_field(name="Venue code",value=code_field[i],inline=True)
		pages.append(page)

	return pages

# For bot command venueinfo()
def compose_venue_info(venue_code:str):
	venue_list = get_venue_list()
	venue_info = []
	# Search for the venue according to the venue code
	for i in range(len(venue_list)):
		if venue_code.lower() == venue_list[i][1]:
			venue_info = venue_list[i]
			break

	# Showing an error message if venue is not found
	if venue_info == []:
		embedInfo = discord.Embed(colour=config.colour_error,title="Venue not found!",description="Check your venue code!")
	else:
		embedInfo = discord.Embed(colour=config.colour_info,title=venue_info[0])
		embedInfo.add_field(name="Level",value=venue_info[2])
		embedInfo.add_field(name="Capacity",value=venue_info[3],inline=True)
		embedInfo.set_author(name="Information for")
	return embedInfo