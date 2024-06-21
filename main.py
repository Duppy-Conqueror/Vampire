# main.py
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
import typing

from help import compose_help
from confirmation import Confirmation
from pagination import Pagination
from valid_datetime import get_date_string, get_time_string
import config
import venue
import booking_system
import list_bookings

import nest_asyncio
nest_asyncio.apply()

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Load bot token amd admin's ID
load_dotenv()
TOKEN = str(os.getenv('DISCORD_TOKEN'))
ADMIN_ID = str(os.getenv('ADMIN_ID'))

# Define bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, activity=discord.Game(name="Blood of the Nation"), help_command=None)

# Connect to server
@bot.event
async def on_ready():
	print(f'{bot.user} is trodding upon creation!')
	print(f'{bot.user} is seeking blood in the following guild(s):')
	for guild in bot.guilds:
		print(f'{guild.name} (id: {guild.id})')
		
# Sync slash command tree with new guild
@bot.event
async def on_guild_join(guild):
	await bot.tree.sync()
	print(
		f'{bot.user} joined is trodding upon the following guild:\n'
		f'{guild.name}(id: {guild.id})'
	)

# Help slash command
@commands.guild_only()
@bot.tree.command(description="A guide to all the commands")
async def help(interaction: discord.Interaction):
	response = compose_help()
	await interaction.response.send_message(embed=response)

# List all the venues
@commands.guild_only()
@bot.tree.command(description="List out all the venues")
async def venuelist(interaction: discord.Interaction):
	pages = venue.compose_venue_list()
	async def get_page(page: int):
		embedList = pages[page-1]
		embedList.set_author(name=f"Requested by {interaction.user}")
		n = len(pages)
		embedList.set_footer(text=f"Page {page} from {n}")
		return embedList, n
	await Pagination(interaction, get_page).navigate()

# Get venue info
@commands.guild_only()
@bot.tree.command(description="Get information of the venue")
@app_commands.describe(venue_name="The name of the study room")
async def venueinfo(interaction: discord.Interaction, venue_name: str):
	response = venue.compose_venue_info(venue_name)
	await interaction.response.send_message(embed=response)
	return

# List future bookings within 14 days
@commands.guild_only()
@bot.tree.command(description="List out all the bookings within 14 days")
async def showall(interaction: discord.Interaction):
	pages = list_bookings.compose_all_bookings()
	async def get_page(page: int):
		embedList = pages[page - 1]
		embedList.set_author(name="Information for booking(s) on")
		n = len(pages)
		embedList.set_footer(text=f"Page {page} from {n}")
		return embedList, n
	await Pagination(interaction, get_page).navigate()

# List bookings on a specific day
@commands.guild_only()
@bot.tree.command(description="Show room bookings on the input date")
@app_commands.describe(year="An integer in the range [1, 9999]")
@app_commands.describe(month="An integer in the range [1, 12]")
@app_commands.describe(day="An integer in the range [1, 28/29/30/31], depending on <year> and <month>")
async def show(interaction: discord.Interaction, year:str, month:str, day:str):
	response = list_bookings.compose_bookings(year, month, day)
	if (response.colour != discord.Colour.red()):
		response.set_author(name="Information for booking(s) on")
	await interaction.response.send_message(embed=response)
	return

# Today's booking
@commands.guild_only()
@bot.tree.command(description="Show today's booking(s)")
async def today(interaction: discord.Interaction):
	response = list_bookings.compose_today_bookings()
	response.set_author(name="Information for booking(s) on")
	await interaction.response.send_message(embed=response)
	return

# Add a new booking
@commands.guild_only()
@bot.tree.command(description="Add a booking to the record (Time is input in 24-hour system)")
@app_commands.describe(year="An integer in the range [1, 9999]")
@app_commands.describe(month="An integer in the range [1, 12]")
@app_commands.describe(day="An integer in the range [1, 28/29/30/31], depending on <year> and <month>")
@app_commands.describe(begin_hour="An integer in the range [0, 24]")
@app_commands.describe(begin_minute="An integer in the range [0, 59] (must be 0 if <begin_hour> = 24)")
@app_commands.describe(end_hour="An integer in the range [0, 24]")
@app_commands.describe(end_minute="An integer in the range [0, 59] (must be 0 if <end_hour>` = 24)")
@app_commands.describe(venue_name="The name of the study room")
@app_commands.describe(user="The name of the person booking the room (Keep it within 20 characters!)")
async def add(interaction: discord.Interaction, year:str, month:str, day:str, begin_hour:str, begin_minute:str, end_hour:str, end_minute:str, venue_name:str, user:str):

	# Obtain the validity result
	result = booking_system.valid_insert(year, month, day, begin_hour, begin_minute, end_hour, end_minute, venue_name, user)
	
	# Error handling: Send an error message according to the error type
	if (result != config.CONFIRM):
		title = result[0]
		description = result[1]
		response = discord.Embed(colour=config.colour_error,title=title,description=description)
		response.set_author(name=f'{interaction.user}')
		await interaction.response.send_message(embed=response)
		return

	date = get_date_string(year, month,day)
	begin = get_time_string(begin_hour, begin_minute)
	end = get_time_string(end_hour, end_minute)

	# Confirmation of adding a booking
	title = result
	description = f'```Date: {date}\nTime: {begin} - {end}\nVenue: {venue_name}\nUser: {user}```'
	response = discord.Embed(colour=config.colour_pending,title=title,description=description)
	response.set_author(name=f'{interaction.user}')
	response.set_footer(text="Please react to this message within 30 seconds.")
	view = Confirmation(interaction)
	await interaction.response.send_message(embed=response,view=view)
	await view.wait()

	# User confirms the booking: Insert the booking and tell the user the insertion is successful
	if view.value == 0:
	
		result = booking_system.insert_booking(date=date, begin=begin, end=end, venue_code=venue.name_to_code[venue_name], user=user)
	
		# Very unlikely to happen
		# result == ["Unknown error!", "Oopsie we have a serious trouble..."]
		if result == config.UNKNOWN_ERROR:
			title = result[0]
			description = result[1]
			response = discord.Embed(colour=config.colour_error,title=title,description=description)
			await interaction.edit_original_response(embed=response,view=None)
	    # Most likely to happen
		# result == ["Booking successfully added!", id]
		else:
			title = result[0]
			response = discord.Embed(colour=config.colour_success,title=title,description=description)
			response.set_author(name=f'{interaction.user}')
			response.set_footer(text=f'Booking ID: {result[1]}')
			await interaction.edit_original_response(embed=response,view=None)

	# User cancels the booking:
	# Notify the user that the booking is cancelled
	elif view.value == 1: 
		title = "Booking process cancelled."
		response = discord.Embed(colour=config.colour_cancel,title=title)
		response.set_author(name=f'{interaction.user}')
		await interaction.edit_original_response(embed=response,view=None)

	# User does not respond:
	# Send a timeout message
	else:
		title = "Timeout!"
		description = "Booking process cancelled."
		response = discord.Embed(colour=config.colour_error,title=title,description=description)
		response.set_author(name=f'{interaction.user}')
		await interaction.edit_original_response(embed=response,view=None)
  
	return

# Delete an existing booking
@commands.guild_only()
@bot.tree.command(description="Remove a booking")
@app_commands.describe(id="The booking ID")
async def remove(interaction: discord.Interaction, id:str):
	result = booking_system.valid_delete(id)
  
	if result == config.BOOKING_NOT_FOUND:
		title = result[0]
		description = result[1]
		response = discord.Embed(colour=config.colour_error,title=f'{title}',description=f'{description}')
		response.set_author(name=f'{interaction.user}')
		await interaction.response.send_message(embed=response)
		return
  
	title = "Confirmation of Booking Removal"
	description = f'```Date: {result.date}\nTime: {result.begin} - {result.end}\nVenue: {result.venue}\nUser: {result.user}```'
	response = discord.Embed(colour=config.colour_pending, title=title, description=description)
	response.set_author(name=f'{interaction.user}')
	response.set_footer(text="Please react to this message within 30 seconds.")
	view = Confirmation(interaction)
	await interaction.response.send_message(embed=response,view=view)
	await view.wait()
  
	# User confirms the booking:
	# Remove the booking and tell the user the removal is successful
	if view.value == 0:
		result = booking_system.delete_booking(id=id)
		# Very unlikely to happen
		if result == config.UNKNOWN_ERROR:
			title = result[0]
			description = result[1]
			response = discord.Embed(colour=config.colour_error, title=title, description=description)
			await interaction.edit_original_response(embed=response, view=None)
		# Most likely to happen
		else:
			title = result
			response = discord.Embed(colour=config.colour_success, title=title)
			response.set_author(name=f'{interaction.user}')
			await interaction.edit_original_response(embed=response, view=None)

	# User cancels the removal:
	# Notify the user that the removal is cancelled
	elif view.value == 1: 
		title = "Booking removal is cancelled."
		response = discord.Embed(colour=config.colour_cancel, title=title)
		response.set_author(name=f'{interaction.user}')
		await interaction.edit_original_response(embed=response, view=None)

	# User does not respond:
	# Send a timeout message
	else:
		title = "Timeout!"
		description = "Booking removal is cancelled."
		response = discord.Embed(colour=config.colour_error, title=title, description=description)
		response.set_author(name=f'{interaction.user}')
		await interaction.edit_original_response(embed=response,view=None)
	
	return

# Backup expired bookings
@commands.guild_only()
@bot.tree.command(description="Archive past bookings. Owner only.")
async def backup(interaction: discord.Interaction):
	if str(interaction.user.id) == ADMIN_ID:
		num_archived = booking_system.backup_booking()
		response = discord.Embed(
			title="Past bookings have been archived successfully.",
			description=f"{num_archived} bookings have been archived.",
			color=config.colour_success
			)
		await interaction.response.send_message(embed=response, ephemeral=False)
	else:
		response = discord.Embed(
			description="Only the owner can perform this action.",
			color=config.colour_error
			)
		await interaction.response.send_message(embed=response, ephemeral=True)

@venueinfo.autocomplete('venue_name')
@add.autocomplete('venue_name')
async def venue_name_autocomplete(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
	return [app_commands.Choice(name=name, value=name) for name in venue.venue_names if current.replace(" ", "").upper() in name.upper()][0:25]

# Syncing text command
@commands.guild_only()
@bot.command()
async def JAH(ctx):
	if str(ctx.author.id) == ADMIN_ID:
		synced = await bot.tree.sync()
		await ctx.send("RASTAFARI!")
		await ctx.send(f'(Synced `{len(synced)}` command(s))')
	else:
		await ctx.send("OH BUMBO CLAAT!")

# (text) command not found error handling
@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandNotFound):
		return
	raise error

# Launch bot
bot.run(TOKEN)
