# confirmation.py
import discord

class Confirmation(discord.ui.View):
	def __init__(self, interaction: discord.Interaction):
		self.interaction = interaction
		self.value = None
		super().__init__(timeout=30)

	async def interaction_check(self, interaction: discord.Interaction) -> bool:
		if interaction.user == self.interaction.user:
			return True
		else:
			emb = discord.Embed(
			description="Only the user of this command can perform this action.",
			color=discord.Colour.red()
			)
			await interaction.response.send_message(embed=emb, ephemeral=True)
			return False

	@discord.ui.button(label="Confirm", disabled=False, style=discord.ButtonStyle.green)
	async def confirm(self, interaction: discord.Interaction, button: discord.Button):
		self.value = 0
		self.stop()

	@discord.ui.button(label="Cancel", disabled=False, style=discord.ButtonStyle.red)
	async def cancel(self, interaction: discord.Interaction, button: discord.Button):
		self.value = 1
		self.stop()

	async def on_timeout(self):
		# Remove buttons on timeout
		message = await self.interaction.original_response()
		await message.edit(view=None)