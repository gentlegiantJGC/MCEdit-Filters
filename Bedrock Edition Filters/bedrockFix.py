#V1.1
#Written by gentlegiantJGC
#http://youtube.com/gentlegiantJGC
#https://twitter.com/gentlegiantJGC

'''
Copyright Notice
I hereby give the user full rights to use this program as provided with the condition that it is only used for non-commercial projects. If the user would like to use this program for commercial projects an alternative can be provided without this limitation for a fee. If interested, please contact me via direct message on twitter (link above) or by other means.
This program can be modified however this copyright notice and the creator information (lines 2-10) must remain unchanged and unmoved. This program must also not be redistributed or rehosted in any way.
'''

from pymclevel import TAG_Int, TAG_String, TAG_Compound
import numpy as np
import random, os, sys, directories, urllib2

displayName = "Bedrock Fix"

inputs = (
	("Log Errors", (True)),
	("Log File", ("file-save", ["*.txt"])),
	("Fix Errors", (True)),
	("Chest Contents", (False)),
	("Chest Loot Table", ("string", "value=loot_tables/chests/woodland_mansion.json")),
	("Percentage of chests to populate", (100, 0, 100)),
	("Spawner Entity", (False)),
)
	
'''
TODO list
log to file rather than console
option to make shulkers point either upwards or into an air gap or leave as is (will point down if no te to start with)
detect if bed is valid
fix pistons
do these two need tile entities?
	end portal
	end gateway
'''
	
	
def perform(level, box, options):
	filterVersion = '#V1.1'
	breakForUpdate = False
	try:
		newFilter = urllib2.urlopen('https://raw.githubusercontent.com/gentlegiantJGC/MCEdit-Filters/master/Bedrock%20Edition%20Filters/bedrockFix.py').read()
		newVersion = newFilter.replace('\r','').split('\n')[0]
		if filterVersion != newVersion:
			f = open('{}/bedrockFix.py'.format(directories.getFiltersDir()),'w')
			f.write(newFilter)
			f.close()
			breakForUpdate = True

	except Exception as e:
		print 'error checking or updating filter : "{}"'.format(e)
	if breakForUpdate:
		raise Exception('Updated Filter To Version {}\nRestart Filter Tool To See Changes'.format(newVersion[1:]))

	logFile = ''
	def logFileFun(logFile, msg):
		print msg
		if logFile == '':
			return msg
		else:
			return '{}\n{}'.format(logFile,msg)
	if level.gamePlatform != 'PE':
		raise Exception('Must be a PE/Win10... world')
		
	chestProb = [True]*options["Percentage of chests to populate"] + [False] * (100-options["Percentage of chests to populate"])
	blocksSupported = {
		23 : "Dispenser",
		25 : "Music",
		26 : "Bed",
		29 : "PistonArm",
		33 : "PistonArm",
		52 : "MobSpawner",
		54 : "Chest",
		61 : "Furnace",
		62 : "Furnace",
		63 : "Sign",
		68 : "Sign",
		84 : "Jukebox",
		116 : "EnchantTable",
		117 : "BrewingStand",
		118 : "Cauldron",
		125 : "Dropper",
		137 : "CommandBlock",
		130 : "EnderChest",
		138 : "Beacon",
		140 : "FlowerPot",
		144 : "Skull",
		146 : "Chest",
		149 : "Comparator",
		150 : "Comparator",
		151 : "DaylightDetector",
		154 : "Hopper",
		176 : "Banner",
		177 : "Banner",
		178 : "DaylightDetector",
		188 : "CommandBlock",
		189 : "CommandBlock",
		199 : "ItemFrame",
		205 : "ShulkerBox",
		218 : "ShulkerBox",
		247 : "NetherReactor",
		252 : "StructureBlock"
	}


	for cx, cz in box.chunkPositions:
		try:
			chunk = level.getChunk(cx, cz)
		except:
			continue
		chunkBlockList = np.unique(chunk.Blocks)
		for block in chunkBlockList:
			if block not in blocksSupported:
				continue
			for coord in np.argwhere(chunk.Blocks == block):
				x,z,y = coord
				x += cx * 16
				z += cz * 16
				if (x,y,z) not in box:
					continue
				# get the tile entity
				te = level.tileEntityAt(x,y,z)
				createTileEntity = False
				if te is None:
					createTileEntity = True
					#create tile entitiy
					te = TAG_Compound()
					te['x'] = TAG_Int(x)
					te['y'] = TAG_Int(y)
					te['z'] = TAG_Int(z)
					
					
				if options["Log Errors"]:
					if 'id' in te:
						if te['id'].value != blocksSupported[block]:
							logFile = logFileFun(logFile, 'Block at {} is type "{}" but set as type "{}"'.format((x,y,z), blocksSupported[block], te['id'].value))
					else:
						if createTileEntity:
							logFile = logFileFun(logFile, 'Block at {} is type "{}" but has no tile entity'.format((x,y,z), blocksSupported[block]))
						else:
							logFile = logFileFun(logFile, 'Block at {} is type "{}" but has no "id" key'.format((x,y,z), blocksSupported[block]))
					if blocksSupported[block] == 'Bed':
						if level.blockDataAt(x,y,z) == 0 and level.blockAt(x,y,z+1) == 26 and level.blockDataAt(x,y,z+1) == 8:
							pass
						elif level.blockDataAt(x,y,z) == 8 and level.blockAt(x,y,z-1) == 26 and level.blockDataAt(x,y,z-1) == 0:
							pass
						elif level.blockDataAt(x,y,z) == 10 and level.blockAt(x,y,z+1) == 26 and level.blockDataAt(x,y,z+1) == 2:
							pass
						elif level.blockDataAt(x,y,z) == 2 and level.blockAt(x,y,z-1) == 26 and level.blockDataAt(x,y,z-1) == 10:
							pass
						elif level.blockDataAt(x,y,z) == 3 and level.blockAt(x+1,y,z) == 26 and level.blockDataAt(x+1,y,z) == 11:
							pass
						elif level.blockDataAt(x,y,z) == 11 and level.blockAt(x-1,y,z) == 26 and level.blockDataAt(x-1,y,z) == 3:
							pass
						elif level.blockDataAt(x,y,z) == 9 and level.blockAt(x+1,y,z) == 26 and level.blockDataAt(x+1,y,z) == 1:
							pass
						elif level.blockDataAt(x,y,z) == 1 and level.blockAt(x-1,y,z) == 26 and level.blockDataAt(x-1,y,z) == 9:
							pass
						else:
							logFile = logFileFun(logFile, 'Block at {} is an invalid bed'.format((x,y,z)))
					
				if options["Fix Errors"]:
					te['id'] = TAG_String(blocksSupported[block])
					
					if blocksSupported[block] == "MobSpawner":
						if options["Spawner Entity"]:
							if 'EntityId' not in te or ('EntityId' in te and te['EntityId'].value == 1):
									te['EntityId'] = TAG_Int(random.choice([32,33,34,35]))
					elif blocksSupported[block] == 'Chest':
						if 'Items' in te and len(te['Items']) > 0:
							pass
						elif 'LootTable' not in te and options["Chest Contents"] and random.choice(chestProb):
							te['LootTable'] = TAG_String(options["Chest Loot Table"])
					
					if createTileEntity:
						chunk.TileEntities.append(te)
		if options["Fix Errors"]:
			chunk.chunkChanged()
	if options["Log Errors"] and options["Log File"] is not None:
		f = open(options["Log File"],'w')
		f.write(logFile)
		f.close()
		os.startfile(options["Log File"])