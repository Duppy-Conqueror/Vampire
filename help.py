# help.py
import discord

import config

def compose_help():
	embedHelp = discord.Embed(colour=config.colour_info, title="List of commands")
	embedHelp.add_field(name=":round_pushpin: /venuelist", value="Lists out all the venues.", inline=False)
	embedHelp.add_field(name=":round_pushpin: /venueinfo <venue_name>", value="Get further information of a venue.", inline=False)
	embedHelp.add_field(name=":book: /showall", value="Shows all the bookings within 14 days.", inline=False)
	embedHelp.add_field(name=":book: /show <year> <month> <day>", value="Shows all the room bookings on the given date.", inline=False)
	embedHelp.add_field(name=":book: /today", value="Shows today's booking(s).", inline=False)
	embedHelp.add_field(name="+ /add <year> <month> <day> <begin_hour> <begin_minute> <end_hour> <end_minute> <venue_name> <user>", value="Adds a new booking to the record.\n- Time inputs are in 24-hour format.", inline=False)
	embedHelp.add_field(name="- /remove <id>", value="Removes a booking based on the booking ID.", inline=False)
	embedHelp.add_field(name=":file_cabinet: /backup", value="Archive past bookings. Owner only.", inline=False)
	embedHelp.add_field(name=":question: /help", value="Leads you to this page :)", inline=False)
	return embedHelp
