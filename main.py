# main.py
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import asyncio

from help import composeHelp
from confirmation import Confirmation
from pagination import Pagination
import config
import venue
import booking_system
import list_bookings

# Fixes runtime error: asyncio.run() cannot be called from a running event loop
import nest_asyncio
nest_asyncio.apply()

# Uncomment when running on replit (1/2)
from keep_alive import keep_alive

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Load bot token amd admin's ID
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
adminID = int(os.getenv('ADMIN_ID'))

# Define bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, activity=discord.Game(name="Blood of the Nation"), help_command=None)

# Connect to server
@bot.event
async def on_ready():
	print(f'{bot.user} is trodding upon creation!')
	for guild in bot.guilds:
		print(f'{bot.user} is seeking blood in the following guild(s):\n'f'{guild.name} (id: {guild.id})')
		
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
	response = composeHelp()
	await interaction.response.send_message(embed=response)

# List all the venues (Completed)
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
	await Pagination(interaction, get_page).navegate()

# Get venue info (Completed)
@commands.guild_only()
@bot.tree.command(description="Get information of the venue")
async def venueinfo(interaction: discord.Interaction, venue_code: str):
	response = venue.compose_venue_info(venue_code)
	await interaction.response.send_message(embed=response)
	return

# List future bookings within 14 days (No input)
@commands.guild_only()
@bot.tree.command(description="List out all the bookings within 14 days")
async def showall(interaction: discord.Interaction):
	pages = list_bookings.compose_all_bookings()
	async def get_page(page: int):
		embedList = pages[page-1]
		embedList.set_author(name="Information for booking(s) on")
		n = len(pages)
		embedList.set_footer(text=f"Page {page} from {n}")
		return embedList, n
	await Pagination(interaction, get_page).navegate()

# List bookings on a specific day (input: date) (Completed)
@commands.guild_only()
@bot.tree.command(description="Show room bookings on the input date")
async def show(interaction: discord.Interaction, date:str):
	response = list_bookings.compose_bookings(date)
	if (response.colour != discord.Colour.red()):
		response.set_author(name="Information for booking(s) on")
	await interaction.response.send_message(embed=response)
	return

# Today's booking (no input) (Completed)
@commands.guild_only()
@bot.tree.command(description="Show today's booking(s)")
async def today(interaction: discord.Interaction):
	response = list_bookings.compose_today_bookings()
	response.set_author(name="Information for booking(s) on")
	await interaction.response.send_message(embed=response)
	return

# Add bookings (input: date, time, venue, user) (Completed)
@commands.guild_only()
@bot.tree.command(description="Add a booking to the record")
async def add(interaction: discord.Interaction, date:str, begin:str, end:str, venue_code:str, user:str):

	# Obtain the validity result
	result = booking_system.valid_insert(date=date,begin=begin,end=end,venue_code=venue_code,user=user)
	
	# Error handling: Send an error message according to the error type
	if (result != config.CONFIRM):
		title = result[0]
		description = result[1]
		response = discord.Embed(colour=config.colour_error,title=title,description=description)
		response.set_author(name=f'{interaction.user}')
		await interaction.response.send_message(embed=response)
		return

	# Confirmation of adding a booking
	title = result
	description = f'```Date: {date}\nTime: {begin} - {end}\nVenue: {venue.get_venue_name(venue_code)}\nUser: {user}```'
	response = discord.Embed(colour=config.colour_pending,title=title,description=description)
	response.set_author(name=f'{interaction.user}')
	response.set_footer(text="Please react to this message within 30 seconds.")
	view = Confirmation(interaction)
	await interaction.response.send_message(embed=response,view=view)
	await view.wait()

	# User confirms the booking: Insert the booking and tell the user the insertion is successful
	if view.value == 0:
	
		result = booking_system.insertBooking(date=date,begin=begin,end=end,venue_code=venue_code,user=user)
	
		# Very unlikely to happen
		if result == config.UNKNOWN_ERROR:
			title = result[0]
			description = result[1]
			response = discord.Embed(colour=config.colour_error,title=title,description=description)
			await interaction.edit_original_response(embed=response,view=None)
	    # Most likely to happen
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

# Delete bookings (input: id) (Completed)
@commands.guild_only()
@bot.tree.command(description="Remove a booking")
async def remove(interaction: discord.Interaction, id:str):
	result = booking_system.valid_delete(id=id)
  
	if result == config.BOOKING_NOT_FOUND:
		title = result[0]
		description = result[1]
		response = discord.Embed(colour=config.colour_error,title=f'{title}',description=f'{description}')
		response.set_author(name=f'{interaction.user}')
		await interaction.response.send_message(embed=response)
  
	title = "Confirmation of Booking Removal"
	description = f'```Date: {result.date}\nTime: {result.begin} - {result.end}\nVenue: {result.venue}\nUser: {result.user}```'
	response = discord.Embed(colour=config.colour_pending,title=title,description=description)
	response.set_author(name=f'{interaction.user}')
	response.set_footer(text="Please react to this message within 30 seconds.")
	view = Confirmation(interaction)
	await interaction.response.send_message(embed=response,view=view)
	await view.wait()
  
	# User confirms the booking:
	# Remove the booking and tell the user the removal is successful
	if view.value == 0:
		result = booking_system.deleteBooking(id=id)
		# Very unlikely to happen
		if result == config.UNKNOWN_ERROR:
			title = result[0]
			description = result[1]
			response = discord.Embed(colour=config.colour_error,title=title,description=description)
			await interaction.edit_original_response(embed=response,view=None)
		# Most likely to happen
		else:
			title = result
			response = discord.Embed(colour=config.colour_success,title=title)
			response.set_author(name=f'{interaction.user}')
			await interaction.edit_original_response(embed=response,view=None)

	# User cancels the removal:
	# Notify the user that the removal is cancelled
	elif view.value == 1: 
		title = "Booking removal is cancelled."
		response = discord.Embed(colour=config.colour_cancel,title=title)
		response.set_author(name=f'{interaction.user}')
		await interaction.edit_original_response(embed=response,view=None)

	# User does not respond:
	# Send a timeout message
	else:
		title = "Timeout!"
		description = "Booking removal is cancelled."
		response = discord.Embed(colour=config.colour_error,title=title,description=description)
		response.set_author(name=f'{interaction.user}')
		await interaction.edit_original_response(embed=response,view=None)
	
	return

# Testing text command
@commands.guild_only()
@bot.command()
async def JAH(ctx):
	if ctx.author.id == adminID:
		synced = await bot.tree.sync()
		await ctx.send("RASTAFARI!")
		await ctx.send(f'(Synced `{len(synced)}` command(s))')
	else:
		await ctx.send("OH BUMBO CLAAT!")

# Uncomment when running on replit (2/2)
keep_alive()

# (text) command not found error handling
@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, discord.ext.commands.CommandNotFound):
		return
	raise error

# Launch bot
async def main():
	async with bot:
		bot.run(TOKEN)

asyncio.run(main())