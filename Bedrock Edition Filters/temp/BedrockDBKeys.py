#Written by gentlegiantJGC
#http://youtube.com/gentlegiantJGC
#https://twitter.com/gentlegiantJGC

# if you are going to use the code in this filter please give credit

import binascii
import os

import json

displayName = "Bedrock DB Keys"

inputs = (
	)
	
def perform(level, box, options):
	with level.worldFile.world_db() as db:
		wop = level.worldFile.writeOptions
		db.Put(wop, 'game_flatworldlayers', json.dumps([7,3,3,2]))
	
	
	
	
		# for n in db.Keys():
			# rop = level.worldFile.readOptions
			# val = db.Get(rop, n)
			# f = open(r"C:\Users\james_000\Desktop\DB Dump\repr"+os.sep+binascii.hexlify(n), 'w')
			# f.write(repr(val))
			# f.close()
			# f = open(r"C:\Users\james_000\Desktop\DB Dump\hex"+os.sep+binascii.hexlify(n), 'wb')
			# f.write(val)
			# f.close()