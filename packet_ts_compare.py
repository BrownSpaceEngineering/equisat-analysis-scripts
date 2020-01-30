import json
import dateutil.parser
import calendar

# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: to compare timestamp metrics of equisat packets (superceded by packet_ts_to_csv.py)
# NOTE: run fetch_transmissions.sh before running this!

json_data=open("transmissions.json").read()
transmissions = json.loads(json_data)

length = len(transmissions)

print(calendar.timegm(dateutil.parser.parse("2018-07-30T22:37:00.691Z").timetuple()))
print("test")

for i in range(1, length+1):
	t = transmissions[length-i]
	added = t["added"]
	created = t["created"]
	timestamp = t["preamble"]["timestamp"]
	addedTime = calendar.timegm(dateutil.parser.parse(added).timetuple())
	createdTime = calendar.timegm(dateutil.parser.parse(created).timetuple())
#	print(str(createdTime)+","+str(addedTime))
	corrected = 1.00762346211*createdTime - 11679142.8532502
	print("Corrected: " + str(corrected))
	print("Added: " + str(addedTime))
	#print(addedTime)
	print("Diff: " + str(corrected - addedTime))
	#print(corrected - addedTime)
	print("------------------")