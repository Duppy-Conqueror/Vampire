# config.py

# Embed colours
colour_error   = 0xe74c3c  # Error
colour_info    = 0x3498db  # Infos and lists
colour_pending = 0xf1c40f  # Confirmation page
colour_success = 0x059033  # After user clicks the confirm button
colour_cancel  = 0x979c9f  # After user clicks the cancel button

# Common instructions, mostly from the booking system
INVALID_DATE = ["Invalid date!", "Please make sure the input date is valid, where\n- `<year>` is in the range [1, 9999];\n- `<month>` is in the range [1, 12];\n- `<day>` is in the range [1, 28/29/30/31], depending on `<year>` and `<month>`."]
PASSED = ["You cannot add bookings to the past.", "You can't live through the past!"]
TOO_FAR_AHEAD = ["You cannot create a booking which ends in more than 2 weeks.", "You are planning too far ahead!"]
INVALID_TIME = ["Invalid time!", "Please use the 24-hour system as the time format, where:\n- `<hour>` is in the range [0, 24];\n- `<minute>` is within the range [0, 59]."]
INVALID_INTERVAL = ["Invalid time interval!", "Please make sure the begin time is at least 1 minute before the end time."]
INVALID_CODE = ["Venue not found!", "Make sure you pick the venues from the list of options!"]
TOO_LONG = ["Please keep the username within 20 characters.", "ARE U OVUVUEVUEVUE ENYETUENWUEVUE UGBEMUGBEM OSAS?"]
TIMECLASH = ["Timeclash!", "Please check the booking record on that day."]
BOOKING_NOT_FOUND = ["Booking not found!","The booking with the input ID does not exist."]
CONFIRM = "Confirmation of New Booking"
INSERT_SUCCESS = "Booking successfully added!"
DELETE_SUCCESS = "Booking successfully removed."
UNKNOWN_ERROR = ["Unknown error!","Oopsie we have a serious trouble..."]

# Timezone offset
tzoffset = 8