# booking.py
class Booking:
	def __init__(self, date:str, begin:str, end:str, venue:str, user:str, id:str):
		self.date = date
		self.begin = begin
		self.end = end
		self.venue = venue
		self.user = user
		self.id = id
  
	# Not in use. Experimental purposes only.
	def __str__(self):
		return f"{self.date}, {self.begin}, {self.end}, {self.venue}, {self.user}, {self.id}"