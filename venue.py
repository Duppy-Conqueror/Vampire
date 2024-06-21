# venue.py
import discord
import os
import csv

import config

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

""" Format of venues.csv:
Venue,Code,Level,Capacity
<venue1_name>,<venue1_code>,<venue1_level>,<venue1_capacity>
<venue2_name>,<venue2_code>,<venue2_level>,<venue2_capacity>
...
"""

# Open venues.csv
def get_venue_list() -> list:
	venue_infos = csv.reader(open('data/venues.csv', 'r'))
	next(venue_infos)	# Skip the first line
	return [x for x in venue_infos]

# Returns a map with venue code as key and its corresponding venue information as key
def get_venue_map() -> dict[str, dict]:
	venue_infos = csv.reader(open('data/venues.csv', 'r'))
	next(venue_infos)
	return {x[1]: {'name': x[0], 'level': x[2], 'capacity': x[3]} for x in venue_infos}

# Returns two dictionaries:
#	name_to_code: {venue_name: venue_code}
# 	code_to_name: {venue_code: venue_name}
def get_name_code_maps() -> tuple[dict, dict]:
	venue_map = get_venue_map().items()
	return {v['name']: k for k, v in venue_map}, {k: v['name'] for k, v in venue_map}

# Get the list of venue names
def get_venue_names() -> list:
	return [v.get('name') for _, v in get_venue_map().items()]

# Global variables
venue_map = get_venue_map()
venue_names: list = get_venue_names()
name_to_code, code_to_name = get_name_code_maps()
NUM_PAGES = 7

# Helper function of compose_venue_list()
# Return the index where the venue item belongs to
def calculute_assigned_page(name: str, level: str) -> int:
	if level == "1":
		return 0
	elif level == "LG3":
		return 2
	elif level == "LG4":
		return 3
	elif level == "LG5":
		return 4
	else:	# level == "LG1"
		if "LC" not in name:	# Rooms at LG1 (non-LC rooms)
			return 1
		else:
			if "0" in name and "10" not in name:
				return 5
			else:
				return 6

# For bot command venuelist()
def compose_venue_list():
	# Divide the list into 7 pages:
	# Rooms at 1
	# Rooms at LG1 (non-LC rooms)
	# Rooms at LG3
	# Rooms at LG4
	# Rooms at LG5
	# LC-01 to LC-09
	# LC-10 to LC-18
	name_field = ['']  * NUM_PAGES
	capacity_field = [''] * NUM_PAGES
	code_field = [''] * NUM_PAGES

	for code, info in venue_map.items():
		name = info['name']
		level = info['level']
		capacity = info['capacity']
		index = calculute_assigned_page(name, level)
		name_field[index] += name + '\n'
		code_field[index] += code + '\n'
		capacity_field[index] += capacity + '\n'
  
	pages = []

	for i in range(NUM_PAGES):
		page = discord.Embed(
					colour=config.colour_info,
					description="All the group study rooms are shown here",
					title="List of Group Study Rooms",
				)
		page.add_field(name="Venue", value=name_field[i])
		page.add_field(name="Capacity", value=capacity_field[i], inline=True)
		page.add_field(name="Venue code", value=code_field[i], inline=True)
		pages.append(page)

	return pages

# For bot command venueinfo()
def compose_venue_info(venue_name: str):
	# Search for the venue code according to the venue name
	venue_code = name_to_code.get(venue_name)

	# Showing an error message if venue code is not found
	if venue_code is None:
		embedInfo = discord.Embed(
						colour=config.colour_error,title="Venue not found!",
						description="Make sure you pick the venues in the options!"
					)
	else:
		venue_info = venue_map.get(venue_code)
		embedInfo = discord.Embed(
						colour=config.colour_info,
						title=venue_info['name']
					)
		embedInfo.add_field(name="Level", value=venue_info['level'])
		embedInfo.add_field(name="Capacity", value=venue_info['capacity'], inline=True)
		embedInfo.set_author(name="Information for")
	return embedInfo
