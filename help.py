# help.py
import discord

import config

def composeHelp():
	embedHelp = discord.Embed(colour=config.colour_info, title="List of commands")
	embedHelp.add_field(name=":round_pushpin: /venuelist", value="Lists out all the venues.", inline=False)
	embedHelp.add_field(name=":round_pushpin: /venueinfo <venue_code>", value="Get further information of a venue.", inline=False)
	embedHelp.add_field(name=":book: /showall", value="Shows all the bookings within 14 days.", inline=False)
	embedHelp.add_field(name=":book: /show <date>", value="Shows all the room bookings on the given date.\n- <date> is input in YYYY-mm-dd format.", inline=False)
	embedHelp.add_field(name=":book: /today", value="Shows today's booking(s).", inline=False)
	embedHelp.add_field(name="+ /add <date> <begin> <end> <venue_code> <user>", value="Adds a new booking to the record.\n- <date> is input in YYYY-mm-dd format.\n- <begin> and <end> are input in 24-hour HH:MM format.", inline=False)
	embedHelp.add_field(name="- /remove <id>", value="Removes a booking based on the booking ID.", inline=False)
	embedHelp.add_field(name=":question: /help", value="Leads you to this page :)", inline=False)
	return embedHelp
