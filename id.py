# id.py

# FORMAT OF A BOOKING ID: Year[0:1] - Month[2:3] - Day[4:5] - Begin_time[6:9] - End_time[10:13] - Venue_code[14:]

# Generate a booking ID using the user inputs (Unique as far as I can see)
# Expected input: YYYY-mm-dd, HH:MM, HH:MM, venue_code
def generateID(date:str, begin:str, end:str, venue_code:str):
	return date[2:].replace('-','') + begin.replace(':','') + end.replace(':','') + venue_code

# Not in use
# Decode a booking ID
# Return a dictionary storing booking information
# def decode(ID: str):
#     date = str("20" + ID[0:2] + "-" + ID[2:4] + "-" + ID[4:6])
#     begin = str(ID[6:8] + ":" + ID[8:10])
#     end = str(ID[10:12] + ":" + ID[12:14])
#     venue_code = str(ID[14:])
#     return {'date':f'{date}','begin':f'{begin}','end':f'{end}','venue_code':f'{venue_code}'}