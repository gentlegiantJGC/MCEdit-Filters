#An MCedit filter mostly written by gentlegiantJGC
#https://www.youtube.com/gentlegiantJGC
#Originally written by xafonyz
#https://www.youtube.com/xafonyzen
#Select a structure and it will create one or more command blocks that will set block the structure in. Note it will be as compact as it can be
#Feel free to use it for any purpose, or to reuse some pieces of code.
#If you do, please quote us : xafonyz, https://www.youtube.com/xafonyzen and gentlegiantJGC, https://www.youtube.com/gentlegiantJGC

#There is a function written by texelelf taken from his NBTeditor filter but modified ever so slightly to work with this filter
# His filters
#	 http://elemanser.com/filters.html
# His youtube
#	 https://www.youtube.com/texelelf
# His twitter
#	 https://twitter.com/TexelElf

from pymclevel import nbt, TAG_Compound, TAG_List, TAG_Int_Array, TAG_Byte_Array, TAG_String, TAG_Long, TAG_Int, TAG_Short, TAG_Byte, TAG_Double, TAG_Float
from pymclevel import BoundingBox
from pymclevel.box import Vector

from pymclevel import MCSchematic

import numpy

import urllib2

import copy

displayName = "Selection to Command 3.1"

inputs = [
(("Previously know as the One Command Structure Spawner", "label"),
("Command block positioning", ("Relative", "Absolute")),
("Include air", False),
("Include blocks", True),
("Include entities", True),
("Relative position", ("South-West", "South-East", "North-West", "North-East")),
("Optimisation", ("Semi-Optimal", "Semi-Optimal 2", "None")),
("command block height (relative only)", 0),
("Absolute Y in relative mode", False),
("Main", "title"),),

(("Remove Irrelevant tags", "label"),
("LastOutput", True),
("SuccessCount", True),
("TrackOutput", True),
("AbsorptionAmount", True),
("Air", True),
("Attributes", True),
("DeathTime", True),
("Dimension", True),
("Fire", True),
("HurtByTimestamp", True),
("PortalCooldown", True),
("Motion", True),
("FallDistance", True),
("OnGround", True),
("Equipment", False),
("HandItems", False),
("ArmorItems", False),
("DropChances", False),
("HealF", False),
("Health", False),
("CustomName", False),
("Small", False),
("ShowArms", False),
("Rotation", False),
("HurtTime", False),
("NoBasePlate", False),
("Marker", False),
("Invulnerable", False),
("DisabledSlots", False),
("CustomNameVisible", False),
("Data tags", "title"),)

]


def perform(level, box, options):
	answer = None
	try:
		filter_version = '3.1.0'
		update_data = urllib2.urlopen('https://raw.githubusercontent.com/gentlegiantJGC/Updates/master/selection_to_command.txt').read().split(';')
		if filter_version != update_data[0]:
			#this part I found in the MCedit source code so credit to the MCedit team
			import albow
			answer = albow.ask(
				('Version {} is available').format(update_data[0]),
				[
					'Download',
					'Ignore'
				],
				default=0,
				cancel=1
			)
	except:
		print 'Tried checking if there was an update however there was an issue'
		
	if answer == "Download":
		from mcplatform import platform_open
		platform_open(update_data[1])
		raise Exception(update_data[2].replace('\\n', '\n\n'))
	
	temp = level.extractSchematic(box)
	tempbox = BoundingBox(Vector(0, 0, 0,), Vector(box.width, box.height, box.length,))
	
	#if you would like to add some commands that will get run at the end you can add them here
	#for example the line below will write hi and then hello in chat
	# bonuscommands = ['say hi', 'say hello']
	#I recommend using tellraw commands because they don't have the [@] before and you can do colours
	bonuscommands = []
	#Uncomment the below (and comment the line above) to create a bedrock box around the selection (note you will need to leave a layer of air on every side in your selection box
	# bonuscommands = ['fill ~'+str(tempbox.minx+2)+' ~'+str(tempbox.miny-2)+' ~'+str(-tempbox.minz-2)+' ~'+str(tempbox.maxx+1)+' ~'+str(tempbox.maxy-3)+' ~'+str(-tempbox.maxz-1)+' bedrock 0 outline']
	
	defaultremove = ["UUIDMost", "UUIDLeast", "Dimension" "inData", "inGround", "life", "inTile", "shake", "wasOnGround", "xTile", "yTile", "zTile"]
	for option in options:
		if options[option] and option not in ["Command block positioning", "Include air", "Include blocks", "Include entities", "Relative position", "Optimisation", "command block height (relative only)", "Absolute Y in relative mode"]:
			defaultremove.append(option)
	
	for (chunk, slices, point) in temp.getChunkSlices(tempbox):
		if options["Include blocks"]:
			for t in chunk.TileEntities:
				x = t["x"].value
				y = t["y"].value
				z = t["z"].value
				if (x,y,z) in tempbox:
					for option in defaultremove:
						if option in t:
							del t[option]
		if options["Include entities"]:
			for e in chunk.Entities:
				x = e["Pos"][0].value
				y = e["Pos"][1].value
				z = e["Pos"][2].value
				if (x,y,z) in tempbox:
					for option in defaultremove:
						if option in e:
							del e[option]
					
					#stripping out default tags
					delete = []
					for tag in e:
						if tag in defaultnbt:
							if type(e[tag]) in (TAG_Compound, TAG_List):
								if NBT2Command(e[tag]) in defaultnbt[tag]:
									delete.append(tag)
							else:
								if str(e[tag].value) in defaultnbt[tag]:
									delete.append(tag)
						
					for tag in delete:
						del e[tag]
						
	#Getting inputs
	global includeAir
	includeAir = options["Include air"]
	global includeBlocks
	includeBlocks = options["Include blocks"]
	global cmdBlockHeight
	cmdBlockHeight = options["command block height (relative only)"]
	global relativePos
	relativePos = options["Relative position"]
	global cmdBlockPosing
	cmdBlockPosing = options["Command block positioning"]
	global absy
	absy = options["Absolute Y in relative mode"]
	# editor = inspect.stack()[1][0].f_locals.get('self', None).editor
	
	commandlist = []
	bracketsToClosetemp = 0
	global popOffBlocks
	popOffBlocks = [6,8,9,10,11,12,13,27,28,31,32,36,37,38,39,40,50,51,55,59,63,64,65,66,68,69,70,71,72,75,76,77,78,81,83,90,92,93,94,96,104,105,106,111,115,119,122,127,131,140,141,142,143,147,148,149,150,157,167,171,175,176,177,193,194,195,196,197]
	global popoffcommands
	popoffcommands = []
	global redstoneblockcommands
	redstoneblockcommands = []
	global solidcommands
	solidcommands = []
	entitiescommand = []
	bonus = []
	bonuscommands.reverse()
	for command in bonuscommands:
		compcmd = (command.encode("unicode-escape")).replace(r'"',r'\"')
		bonus.append('{id:MinecartCommandBlock,Command:\"'+compcmd+'\",Riding:')
	bonus = ''.join(bonus)

	if includeAir or includeBlocks:
		if options["Optimisation"] == "None":
			for y in reversed(xrange(tempbox.miny,tempbox.maxy)):
				for x in xrange(tempbox.minx,tempbox.maxx):
					for z in xrange(tempbox.minz,tempbox.maxz):
						testbox = BoundingBox(Vector(x, y, z,), Vector(1, 1, 1,))
						maxvolume = [testbox.volume, testbox, [temp.blockAt(x, y, z), temp.blockDataAt(x, y, z)], temp.tileEntityAt(x, y, z)]
						region2command(maxvolume, box)
						delbox(temp, maxvolume[1])
		
		elif options["Optimisation"] in ["Semi-Optimal", "Semi-Optimal 2"]:
			if not includeAir or not includeBlocks:
				for (chunk, slices, point) in temp.getChunkSlices(tempbox):
					blocks = chunk.Blocks[slices]
					data = chunk.Data[slices]
					if not includeAir:
						blocks[blocks == 0] = 65530
						data[blocks == 65530] = 250
					if not includeBlocks:
						blocks[blocks != 0] = 65530
						data[blocks == 65530] = 250
						
			#remove tile entities
			for y in xrange(tempbox.miny,tempbox.maxy):
				for x in xrange(tempbox.minx,tempbox.maxx):
					for z in xrange(tempbox.minz,tempbox.maxz):
						te = temp.tileEntityAt(x, y, z)
						if te != None and temp.blockAt(x, y, z) != 65530:
							testbox = BoundingBox(Vector(x, y, z,), Vector(1, 1, 1,))
							maxvolume = [testbox.volume, testbox, [temp.blockAt(x, y, z), temp.blockDataAt(x, y, z)], te]
							region2command(maxvolume, box)
							delbox(temp, maxvolume[1])
		
			if options["Optimisation"] == "Semi-Optimal":

				for x in xrange(0, tempbox.maxx):
					print str(x-tempbox.minx)+' / '+str(tempbox.width)
					for y in xrange(0, tempbox.maxy):
						for z in xrange(0, tempbox.maxz):
							blocktype = temp.blockAt(x, y, z)
							if blocktype != 65530:
								maxvolume = [0, BoundingBox(Vector(x, y, z,), Vector(1, 1, 1,)), [0, 0], None]
								
								maxvolume = maxbox(temp, tempbox, maxvolume)
								
								region2command(maxvolume, box)
								
								delbox(temp, maxvolume[1])
		
			elif options["Optimisation"] == "Semi-Optimal 2":
				# ''''''
				# import albow
				# answer = albow.ask(
					# ('Dev Mode Activate'),
					# [
						# 'Continue',
						# 'Cancel'
					# ],
					# default=1,
					# cancel=1
				# )
				# if answer == "Cancel":
					# raise Exception('Good choice. This method is still in development')
				# ''''''
				
				temptemp = temp.extractSchematic(tempbox)
				originaltemp = temp.extractSchematic(tempbox)
				tempvolumelist = []
				for x in xrange(0, tempbox.maxx):
					print str(x-tempbox.minx)+' / '+str(tempbox.width)
					for y in xrange(0, tempbox.maxy):
						for z in xrange(0, tempbox.maxz):
							if temptemp.blockAt(x, y, z) != 65530:
								blocktype = temp.blockAt(x, y, z)
								if blocktype not in [65530, 65529]:
									maxvolume = [0, BoundingBox(Vector(x, y, z,), Vector(1, 1, 1,)), [0, 0], None]
									
									maxvolume = maxbox(temp, tempbox, maxvolume)
									delbox(temptemp, maxvolume[1])
									tempvolumelist.append(maxvolume)
			
				volumelist = []
				while tempvolumelist != []:
					minvolume = min(tempvolumelist)[0]
					print minvolume
					for item in tempvolumelist[:]:
						if item[0] == minvolume:
							if item[2][0] != 65530:
								volumelist.append(item)
							tempvolumelist.remove(item)
							delbox2(temp, item[1])
					tempvolumelist2 = []
					for item in tempvolumelist:
						maxvolume = maxbox2(temp, tempbox, item)
						if maxvolume not in tempvolumelist2:
							tempvolumelist2.append(maxvolume)
					tempvolumelist = tempvolumelist2
				
				'''
				for item in volumelist[:]:
					volumelist2 = copy.deepcopy(volumelist)
					volumelist2.remove(item)
					delbox(temptemp, tempbox)
					for maxvolume in reversed(volumelist2):
						fillbox(temptemp, maxvolume[1], maxvolume[2])
					
					if box1eqbox2(temptemp, originaltemp, tempbox):
						volumelist.remove(item)
						print 'removed '+str(item)
				'''
				# exept = 0
				
				for i in range(2):
					# print '1'
					# print volumelist
					for item in list(enumerate(volumelist))[:]:
						volumelist2 = copy.deepcopy(volumelist)
						# try:
						volumelist2.remove(item[1])
						# except:
							# print '2'
							# print item[1]
							# print '3'
							# print volumelist
							# print '4'
							# print volumelist2
							# exept = 1
						# if exept == 1:
							# raise Exception('nope')
						itemold = [item[0], list(item[1])]
						item = [item[0], list(item[1])]
						
						while pull('+y', item[1], volumelist2, originaltemp):
							item[1][1] = BoundingBox(Vector(item[1][1].minx, item[1][1].miny, item[1][1].minz,), Vector(item[1][1].width, item[1][1].height-1, item[1][1].length,))
							
						while pull('-y', item[1], volumelist2, originaltemp):
							item[1][1] = BoundingBox(Vector(item[1][1].minx, item[1][1].miny+1, item[1][1].minz,), Vector(item[1][1].width, item[1][1].height-1, item[1][1].length,))
							
						while pull('+x', item[1], volumelist2, originaltemp):
							item[1][1] = BoundingBox(Vector(item[1][1].minx, item[1][1].miny, item[1][1].minz,), Vector(item[1][1].width-1, item[1][1].height, item[1][1].length,))
							
						while pull('-x', item[1], volumelist2, originaltemp):
							item[1][1] = BoundingBox(Vector(item[1][1].minx+1, item[1][1].miny, item[1][1].minz,), Vector(item[1][1].width-1, item[1][1].height, item[1][1].length,))
							
						while pull('+z', item[1], volumelist2, originaltemp):
							item[1][1] = BoundingBox(Vector(item[1][1].minx, item[1][1].miny, item[1][1].minz,), Vector(item[1][1].width, item[1][1].height, item[1][1].length-1,))
							
						while pull('-z', item[1], volumelist2, originaltemp):
							item[1][1] = BoundingBox(Vector(item[1][1].minx, item[1][1].miny, item[1][1].minz+1,), Vector(item[1][1].width, item[1][1].height, item[1][1].length-1,))
						
						if item[1][1].width == 0 or item[1][1].height == 0 or item[1][1].length == 0:
							# volumelist.remove(itemold[1])
							volumelist[item[0]] = [0, BoundingBox(Vector(0, 0, 0,), Vector(0, 0, 0,)), [0, 0], None]
							print 'removed '+str(itemold[1])
							continue
						
						if item[1][0] != item[1][1].volume:
							item[1][0] = item[1][1].volume
						
						if item[1] != volumelist[item[0]]:
							volumelist[item[0]] = item[1]
					
					if [0, BoundingBox(Vector(0, 0, 0,), Vector(0, 0, 0,)), [0, 0], None] in volumelist:
						volumelist.remove([0, BoundingBox(Vector(0, 0, 0,), Vector(0, 0, 0,)), [0, 0], None])
							
				for maxvolume in volumelist:
					region2command(maxvolume, box)
								
				
	if options["Include entities"]:
		for (chunk, slices, point) in temp.getChunkSlices(tempbox):
			for e in chunk.Entities:
				ex = e["Pos"][0].value
				ey = e["Pos"][1].value
				ez = e["Pos"][2].value
				
				if (ex,ey,ez) in tempbox:
					del e["Pos"]
					if cmdBlockPosing=="Absolute":
						entityX = ex + box.minx
						entityY = ey + box.miny
						entityZ = ez + box.minz
				
					elif cmdBlockPosing=="Relative":
						if absy:
							entityY = ey + box.miny
						else:
							entityY=ey-cmdBlockHeight-2.05
						if relativePos=="North-West":
							entityX=ex+1.5
							entityZ=ez+1.794
						if relativePos=="South-West":
							entityX=ex+1.5
							entityZ=ez-1.206-box.length
						if relativePos=="North-East":
							entityX=ex-1.5-box.width
							entityZ=ez+1.794
						if relativePos=="South-East":
							entityX=ex-1.5-box.width
							entityZ=ez-1.206-box.length
					else :
						raise Exception ("WTF?")

					cmdtemp = "{id:MinecartCommandBlock,Command:\"summon "+str(e["id"].value)+" "+ {True: "~", False: ""}[cmdBlockPosing=="Relative"]+str(entityX)+{True: " ", False:{True: " ~", False: " "}[cmdBlockPosing=="Relative"]}[options["Absolute Y in relative mode"] == True]+str(+entityY)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(entityZ)+" {"+NBT2Command(e)+"}\",Riding:"
					
					entitiescommand.append([cmdtemp, 1])

	if cmdBlockPosing=="Absolute":
		cmd="/summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"+bonus+"{id:MinecartCommandBlock,Command:tellraw @a [{\"text\":\"Thanks to gentlegiantJGC and xafonyz for making the MCedit filter that made this one-click command\",\"color\":\"gold\"},{\"text\":\"\\nwww.youtube.com/gentlegiantJGC\\nwww.youtube.com/xafonyzen\",\"color\":\"white\"}],Riding:"
		bracketsToClose=1
		bracketsToClose += len(bonuscommands)
		if entitiescommand != []:
			for c in entitiescommand:
				if len(cmd) + len(c[0]) + bracketsToClose + c[1] + 195 > 32760:
					cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="/summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += c[0]
				bracketsToClose += c[1]
				
			if 	popoffcommands != [] or redstoneblockcommands != [] or solidcommands != []:
				if len(cmd) + 51 + bracketsToClose + 195 > 32760:
					cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="/summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += '{id:MinecartCommandBlock,Command:buffer,Riding:{id:MinecartCommandBlock,Command:buffer,Riding:'
				bracketsToClose += 2
		
		if popoffcommands != []:
			for c in popoffcommands:
				if len(cmd) + len(c[0]) + bracketsToClose + c[1] + 195 > 32760:
					cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="/summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += c[0]
				bracketsToClose += c[1]
				
			if redstoneblockcommands != [] or solidcommands != []:
				if len(cmd) + 51 + bracketsToClose + 195 > 32760:
					cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="/summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += '{id:MinecartCommandBlock,Command:buffer,Riding:{id:MinecartCommandBlock,Command:buffer,Riding:'
				bracketsToClose += 2
				
		if redstoneblockcommands != []:
			for c in redstoneblockcommands:
				if len(cmd) + len(c[0]) + bracketsToClose + c[1] + 195 > 32760:
					cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="/summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += c[0]
				bracketsToClose += c[1]
				
			if solidcommands != []:
				if len(cmd) + 51 + bracketsToClose + 195 > 32760:
					cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="/summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += '{id:MinecartCommandBlock,Command:buffer,Riding:{id:MinecartCommandBlock,Command:buffer,Riding:'
				bracketsToClose += 2
		
		if solidcommands != []:
			for c in solidcommands:
				if len(cmd) + len(c[0]) + bracketsToClose + c[1] + 195 > 32760:
					cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="/summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += c[0]
				bracketsToClose += c[1]
				
		cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
		while bracketsToClose > 0:
			cmd += "}"
			bracketsToClose -= 1
		commandlist.append(cmd)
		schematic = MCSchematic((len(commandlist)*2-1, 1, 1), mats=level.materials)
		cx = 0
		for command in commandlist:
			schematic.setBlockAt(cx, 0, 0, 137)
			schematic.setBlockDataAt(cx, 0, 0, 0)
			control = TAG_Compound()
			control["id"] = TAG_String(u'Control')
			control["CustomName"] = TAG_String(u"builder")
			control["z"] = TAG_Int(0)
			control["y"] = TAG_Int(0)
			control["x"] = TAG_Int(cx)
			control["Command"] = TAG_String(command)
			schematic.TileEntities.append(control)
			cx += 2
		editor.addCopiedSchematic(schematic)
					
	if cmdBlockPosing=="Relative":
		cmd="summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"+bonus+"{id:MinecartCommandBlock,Command:tellraw @a [{\"text\":\"Thanks to gentlegiantJGC and xafonyz for making the MCedit filter that made this one-click command\",\"color\":\"gold\"},{\"text\":\"\\nwww.youtube.com/gentlegiantJGC\\nwww.youtube.com/xafonyzen\",\"color\":\"white\"}],Riding:"
		bracketsToClose=1
		bracketsToClose += len(bonuscommands)
		if entitiescommand != []:
			for c in entitiescommand:
				if len(cmd) + len(c[0]) + bracketsToClose + c[1] + 195 > 32710:
					cmd = "/execute @e[name=OCSSMarker,type=ArmorStand] ~ ~ ~ "+cmd+"{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += c[0]
				bracketsToClose += c[1]
				
			if 	popoffcommands != [] or redstoneblockcommands != [] or solidcommands != []:
				if len(cmd) + 51 + bracketsToClose + 195 > 32710:
					cmd = "/execute @e[name=OCSSMarker,type=ArmorStand] ~ ~ ~ "+cmd+"{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += '{id:MinecartCommandBlock,Command:buffer,Riding:{id:MinecartCommandBlock,Command:buffer,Riding:'
				bracketsToClose += 2
		
		if popoffcommands != []:
			for c in popoffcommands:
				if len(cmd) + len(c[0]) + bracketsToClose + c[1] + 195 > 32710:
					cmd="/execute @e[name=OCSSMarker,type=ArmorStand] ~ ~ ~ "+cmd+"{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += c[0]
				bracketsToClose += c[1]
				
			if redstoneblockcommands != [] or solidcommands != []:
				if len(cmd) + 51 + bracketsToClose + 195 > 32710:
					cmd="/execute @e[name=OCSSMarker,type=ArmorStand] ~ ~ ~ "+cmd+"{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += '{id:MinecartCommandBlock,Command:buffer,Riding:{id:MinecartCommandBlock,Command:buffer,Riding:'
				bracketsToClose += 2
				
		if redstoneblockcommands != []:
			for c in redstoneblockcommands:
				if len(cmd) + len(c[0]) + bracketsToClose + c[1] + 195 > 32710:
					cmd = "/execute @e[name=OCSSMarker,type=ArmorStand] ~ ~ ~ "+cmd+"{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += c[0]
				bracketsToClose += c[1]
				
			if solidcommands != []:
				if len(cmd) + 51 + bracketsToClose + 195 > 32710:
					cmd = "/execute @e[name=OCSSMarker,type=ArmorStand] ~ ~ ~ "+cmd+"{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += '{id:MinecartCommandBlock,Command:buffer,Riding:{id:MinecartCommandBlock,Command:buffer,Riding:'
				bracketsToClose += 2
		
		if solidcommands != []:
			for c in solidcommands:
				if len(cmd) + len(c[0]) + bracketsToClose + c[1] + 195 > 32710:
					cmd = "/execute @e[name=OCSSMarker,type=ArmorStand] ~ ~ ~ "+cmd+"{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				cmd += c[0]
				bracketsToClose += c[1]
				
		cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
		while bracketsToClose > 0:
			cmd += "}"
			bracketsToClose -= 1
		if len(commandlist) > 0:
			cmd = "/execute @e[name=OCSSMarker,type=ArmorStand] ~ ~ ~ "+cmd
		commandlist.append(cmd)
		
		if len(commandlist) == 1:
			schematic = MCSchematic((1, 1, 1), mats=level.materials)
			for command in commandlist:
				schematic.setBlockAt(0, 0, 0, 137)
				schematic.setBlockDataAt(0, 0, 0, 0)
				control = TAG_Compound()
				control["id"] = TAG_String(u'Control')
				control["CustomName"] = TAG_String(u"builder")
				control["z"] = TAG_Int(0)
				control["y"] = TAG_Int(0)
				control["x"] = TAG_Int(0)
				control["Command"] = TAG_String(command)
				schematic.TileEntities.append(control)
				
			editor.addCopiedSchematic(schematic)
			
		else:
			schematic = MCSchematic((len(commandlist)*2+1, 1, 1), mats=level.materials)
			cx = 2
			for command in commandlist:
				schematic.setBlockAt(cx, 0, 0, 137)
				schematic.setBlockDataAt(cx, 0, 0, 0)
				control = TAG_Compound()
				control["id"] = TAG_String(u'Control')
				control["CustomName"] = TAG_String(u"builder")
				control["z"] = TAG_Int(0)
				control["y"] = TAG_Int(0)
				control["x"] = TAG_Int(cx)
				control["Command"] = TAG_String(command)
				schematic.TileEntities.append(control)
				cx += 2
				
			schematic.setBlockAt(0, 0, 0, 137)
			schematic.setBlockDataAt(0, 0, 0, 0)
			control = TAG_Compound()
			control["id"] = TAG_String(u'Control')
			control["CustomName"] = TAG_String(u"builder")
			control["z"] = TAG_Int(0)
			control["y"] = TAG_Int(0)
			control["x"] = TAG_Int(0)
			control["Command"] = TAG_String('/summon FallingSand ~ ~+4 ~ {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:{id:MinecartCommandBlock,Command:"/summon ArmorStand ~ ~-1.05 ~0.3125 {CustomName:OCSSMarker,NoGravity:1}",Riding:{id:MinecartCommandBlock,Command:"setblock ~ ~-2 ~ stone",Riding:{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}}}')
			schematic.TileEntities.append(control)
				
			editor.addCopiedSchematic(schematic)
			
			
			
def region2command(region, box):
	cmdtemp = ''
	if region[0] == 1:
		if cmdBlockPosing == "Absolute":
			blockX = str(region[1].minx + box.minx)
			blockY = str(region[1].miny + box.miny)
			blockZ = str(region[1].minz + box.minz)
		
		elif cmdBlockPosing == "Relative":
			if absy:
				blockY = str(region[1].miny + box.miny)
			else:
				blockY = '~'+str(region[1].miny-cmdBlockHeight-2)
			if relativePos == "North-West":
				blockX = '~'+str(region[1].minx + 2)
				blockZ = '~'+str(region[1].minz + 2)
			elif relativePos == "South-West":
				blockX = '~'+str(region[1].minx + 2)
				blockZ = '~'+str(region[1].minz - 1 - box.length)
			elif relativePos == "North-East":
				blockX = '~'+str(region[1].minx - 1 - box.width)
				blockZ = '~'+str(region[1].minz + 2)
			elif relativePos == "South-East":
				blockX = '~'+str(region[1].minx - 1 - box.width)
				blockZ = '~'+str(region[1].minz - 1 - box.length)
		else :
			raise Exception ("WTF?")
			
		if includeBlocks and region[2][0] != 0:
			if region[3] == None:
				cmdtemp = '{id:MinecartCommandBlock,Command:"setblock '+ blockX +' '+ blockY +' '+ blockZ+' '+IDsToName[region[2][0]]+{True: ' '+str(region[2][1])+' destroy', False: {True:'', False: ' '+str(region[2][1])}[region[2][1] == 0]}[region[2][0]==152]+'",Riding:'

			else:
				cmdtemp = '{id:MinecartCommandBlock,Command:"setblock '+ blockX +' '+ blockY +' '+ blockZ+' '+IDsToName[region[2][0]]+' '+str(region[2][1])+{True: ' destroy', False: ' replace'}[region[2][0]==152]+' {'+NBT2Command(region[3])+'}",Riding:'
				
		elif includeAir and region[2][0] == 0:
			if region[3] == None:
				cmdtemp = '{id:MinecartCommandBlock,Command:"setblock '+ blockX +' '+ blockY +' '+ blockZ+' '+IDsToName[region[2][0]]+{True:'', False: ' '+str(region[2][1])}[region[2][1] == 0]+'",Riding:'

			else:
				cmdtemp = '{id:MinecartCommandBlock,Command:"setblock '+ blockX +' '+ blockY +' '+ blockZ+' '+IDsToName[region[2][0]]+' '+str(region[2][1])+' replace {'+NBT2Command(region[3])+'}",Riding:'
		
		if cmdtemp != '':
			if region[2][0] in popOffBlocks:
				popoffcommands.append([cmdtemp, 1])
			
			elif region[2][0] == 152:
				redstoneblockcommands.append([cmdtemp, 1])
				solidcommands.append([cmdtemp, 1])
			else:
				solidcommands.append([cmdtemp, 1])
				
	if region[0] >= 2:
		if cmdBlockPosing == "Absolute":
			blockX = str(region[1].minx + box.minx)
			blockdx = str(region[1].maxx + box.minx-1)
			blockY = str(region[1].miny + box.miny)
			blockdy = str(region[1].maxy + box.miny-1)
			blockZ = str(region[1].minz + box.minz)
			blockdz = str(region[1].maxz + box.minz-1)
		
		elif cmdBlockPosing == "Relative":
			if absy:
				blockY = str(region[1].miny + box.miny)
				blockdy = str(region[1].maxy + box.miny-1)
			else:
				blockY = '~'+str(region[1].miny-cmdBlockHeight-2)
				blockdy = '~'+str(region[1].maxy - cmdBlockHeight - 2 -1)
			if relativePos == "North-West":
				blockX = '~'+str(region[1].minx + 2)
				blockdx = '~'+str(region[1].maxx + 2-1)
				blockZ = '~'+str(region[1].minz + 2)
				blockdz = '~'+str(region[1].maxz + 2-1)
			elif relativePos == "South-West":
				blockX = '~'+str(region[1].minx + 2)
				blockdx = '~'+str(region[1].maxx + 2-1)
				blockZ = '~'+str(region[1].minz - 1 - box.length)
				blockdz = '~'+str(region[1].maxz - 1 - box.length-1)
			elif relativePos == "North-East":
				blockX = '~'+str(region[1].minx - 1 - box.width)
				blockdx = '~'+str(region[1].maxx - 1 - box.width-1)
				blockZ = '~'+str(region[1].minz + 2)
				blockdz = '~'+str(region[1].maxz + 2-1)
			elif relativePos == "South-East":
				blockX = '~'+str(region[1].minx - 1 - box.width)
				blockdx = '~'+str(region[1].maxx - 1 - box.width-1)
				blockZ = '~'+str(region[1].minz - 1 - box.length)
				blockdz = '~'+str(region[1].maxz - 1 - box.length-1)
		else :
			raise Exception ("WTF?")
			
		if includeBlocks and region[2][0] != 0:
			if region[3] == None:
				cmdtemp = '{id:MinecartCommandBlock,Command:"fill '+ blockX +' '+ blockY +' '+ blockZ+' '+blockdx +' '+ blockdy +' '+ blockdz+' '+IDsToName[region[2][0]]+{True: ' '+str(region[2][1])+' destroy', False: {True:'', False: ' '+str(region[2][1])}[region[2][1] == 0]}[region[2][0]==152]+'",Riding:'

			else:
				cmdtemp = '{id:MinecartCommandBlock,Command:"fill '+ blockX +' '+ blockY +' '+ blockZ+' '+blockdx +' '+ blockdy +' '+ blockdz+' '+IDsToName[region[2][0]]+' '+str(region[2][1])+{True: " destroy", False: " replace"}[region[2][0]==152]+' {'+NBT2Command(region[3])+'}",Riding:'
				
		elif includeAir and region[2][0] == 0:
			if region[3] == None:
				cmdtemp = '{id:MinecartCommandBlock,Command:"fill '+ blockX +' '+ blockY +' '+ blockZ+' '+blockdx +' '+ blockdy +' '+ blockdz+' '+IDsToName[region[2][0]]+{True:'', False: ' '+str(region[2][1])}[region[2][1] == 0]+'",Riding:'

			else:
				cmdtemp = '{id:MinecartCommandBlock,Command:"fill '+ blockX +' '+ blockY +' '+ blockZ+' '+blockdx +' '+ blockdy +' '+ blockdz+' '+IDsToName[region[2][0]]+' '+str(region[2][1])+' replace {'+NBT2Command(region[3])+'}",Riding:'
		
		if cmdtemp != '':
			if region[2][0] in popOffBlocks:
				popoffcommands.append([cmdtemp, 1])
			
			elif region[2][0] == 152:
				redstoneblockcommands.append([cmdtemp, 1])
				solidcommands.append([cmdtemp, 1])
			else:
				solidcommands.append([cmdtemp, 1])

		
#Taken from Texelelf's NBTeditor filter
#Modified slightly by gentlegiantJGC to work with this filter
#https://www.youtube.com/texelelf
#http://elemanser.com/filters.html
def NBT2Command(nbtData):
	command = ""
	if type(nbtData) is TAG_List:
		list = True
	else:
		list = False

	if type(nbtData) in (TAG_Compound, TAG_List):
		for tag in range(0,len(nbtData)) if list else nbtData.keys():
			if type(nbtData[tag]) is TAG_Compound:
				if not list:
					if tag != "":
						command += tag+":"
				command += "{"
				command += NBT2Command(nbtData[tag])
				command += "}"
			elif type(nbtData[tag]) is TAG_List:
				if not list:
					if tag != "":
						command += tag+":"
				command += "["
				command += NBT2Command(nbtData[tag])
				command += "]"
			else:
				if not list:
					if tag != "":
						command += tag+":"
				if type(nbtData[tag]) is TAG_String:
					if '"' in nbtData[tag].value or '\\' in nbtData[tag].value:
						command += r"\""
						command += ((str.replace(nbtData[tag].value.encode("unicode-escape"), r'"',r'\"')).encode("unicode-escape")).replace(r'"',r'\"')
						command += r"\""
					else:
						command += nbtData[tag].value
				else:
					if type(nbtData[tag]) == TAG_Byte_Array:
						command += "["+",".join(["%sb" % num for num in nbtData[tag].value.astype("str")])+"]"
					elif type(nbtData[tag]) == TAG_Int_Array:
						command += "["+",".join(nbtData[tag].value.astype("str"))+"]"
					else:
						command += nbtData[tag].value.encode("unicode-escape") if isinstance(nbtData[tag].value, unicode) else str(nbtData[tag].value)
						if type(nbtData[tag]) is TAG_Byte:
							command += "b"
						elif type(nbtData[tag]) is TAG_Short:
							command += "s"
						elif type(nbtData[tag]) is TAG_Long:
							command += "l"
						elif type(nbtData[tag]) is TAG_Float:
							command += "f"
						elif type(nbtData[tag]) is TAG_Double:
							command += "d"			
				
			command += ","
		else:
			if command != "":
				if command[-1] == ",":
					command = command[:-1]
	else:
		if nbtData.name != "":
			command += nbtData.name+":"
		if type(nbtData) is TAG_String:
			if '"' in nbtData.value or '\\' in nbtData.value:
				command += r"\""
				command += ((str.replace(nbtData.value.encode("unicode-escape"), r'"',r'\"')).encode("unicode-escape")).replace(r'"',r'\"')
				command += r"\""
			else:
				command += nbtData.value
		else:
			if type(nbtData) == TAG_Byte_Array:
				command += "["+",".join(["%sb" % num for num in nbtData.value.astype("str")])+"]"
			elif type(nbtData) == TAG_Int_Array:
				command += "["+",".join(nbtData.value.astype("str"))+"]"
			else:
				command += nbtData.value.encode("unicode-escape") if isinstance(nbtData.value, unicode) else str(nbtData.value)
				if type(nbtData) is TAG_Byte:
					command += "b"
				elif type(nbtData) is TAG_Short:
					command += "s"
				elif type(nbtData) is TAG_Long:
					command += "l"
				elif type(nbtData) is TAG_Float:
					command += "f"
				elif type(nbtData) is TAG_Double:
					command += "d"			

	return command

	#optimisation functions
def all(selection, testbox):
	blocklist = numpy.array([]).astype(int)
	datalist = numpy.array([]).astype(int)
	for (chunk, slices, point) in selection.getChunkSlices(testbox):
		blocklist = numpy.append(blocklist, chunk.Blocks[slices])
		datalist = numpy.append(datalist, chunk.Data[slices])
	if len(numpy.unique(blocklist)) == 1 and len(numpy.unique(datalist)) == 1:
		return [numpy.unique(blocklist)[0], numpy.unique(datalist)[0]]
	else:
		return [-1, -1]
		
def delbox(selection, testbox):
	for (chunk, slices, point) in selection.getChunkSlices(testbox):
		blocks = chunk.Blocks[slices]
		blocks[blocks != 65530] = 65530
		data = chunk.Data[slices]
		data[data != 250] = 250
		
def fillbox(selection, testbox, idmg):
	for (chunk, slices, point) in selection.getChunkSlices(testbox):
		blocks = chunk.Blocks[slices]
		blocks[blocks != idmg[0]] = idmg[0]
		data = chunk.Data[slices]
		data[data != idmg[1]] = idmg[1]
		
def box1eqbox2(box1, box2, tempbox):
	#note box here is a schematic rather than a bounding box
	box1blocks = []
	box1data = []
	box2blocks = []
	box2data = []
	for (chunk, slices, point) in box1.getChunkSlices(tempbox):
		box1blocks.append(chunk.Blocks[slices])
		box1data.append(chunk.Data[slices])
	for (chunk, slices, point) in box2.getChunkSlices(tempbox):
		box2blocks.append(chunk.Blocks[slices])
		box2data.append(chunk.Data[slices])
	if len(box1blocks) == len(box2blocks) == len(box1data) == len(box2data):
		for sliceno in xrange(len(box1blocks)):
			if not numpy.array_equal(box1blocks[sliceno], box2blocks[sliceno]) or not numpy.array_equal(box1data[sliceno], box2data[sliceno]):
				return False
	else:
		raise Exception('Error')
	return True
		
def maxbox(selection, tempbox, testbox):
	testboxx = pushx(selection, tempbox, testbox[1])
	testboxy = pushy(selection, tempbox, testbox[1])
	testboxz = pushz(selection, tempbox, testbox[1])
	
	boxes = []
	
	for i in [pushz(selection, tempbox, testboxy), pushy(selection, tempbox, testboxz)]:
		boxes.append(pushx(selection, tempbox, i))
	
	for i in [pushz(selection, tempbox, testboxx), pushx(selection, tempbox, testboxz)]:
		boxes.append(pushy(selection, tempbox, i))
		
	for i in [pushy(selection, tempbox, testboxx), pushx(selection, tempbox, testboxy)]:
		boxes.append(pushz(selection, tempbox, i))
		
	for i in boxes:
		if i.volume >= testbox[1].volume:
			testbox = [i.volume, i, all(selection, i), None]
	return testbox
	
def pushx(selection, tempbox, testbox):
	testbox2 = testbox
	while all(selection, testbox2) != [-1, -1] and testbox2.maxx <= tempbox.maxx and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx, testbox.miny, testbox.minz,), Vector(testbox.width+1, testbox.height, testbox.length,))
	
	testbox2 = testbox
	while all(selection, testbox2) != [-1, -1] and testbox2.minx >= tempbox.minx and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx-1, testbox.miny, testbox.minz,), Vector(testbox.width+1, testbox.height, testbox.length,))
		
	return testbox
	
	
def pushy(selection, tempbox, testbox):
	testbox2 = testbox
	while all(selection, testbox2) != [-1, -1] and testbox2.maxy <= tempbox.maxy and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx, testbox.miny, testbox.minz,), Vector(testbox.width, testbox.height+1, testbox.length,))
	
	testbox2 = testbox
	while all(selection, testbox2) != [-1, -1] and testbox2.miny >= tempbox.miny and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx, testbox.miny-1, testbox.minz,), Vector(testbox.width, testbox.height+1, testbox.length,))
		
	return testbox
	
def pushz(selection, tempbox, testbox):
	testbox2 = testbox
	while all(selection, testbox2) != [-1, -1] and testbox2.maxz <= tempbox.maxz and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx, testbox.miny, testbox.minz,), Vector(testbox.width, testbox.height, testbox.length+1,))
	
	testbox2 = testbox
	while all(selection, testbox2) != [-1, -1] and testbox2.minz >= tempbox.minz and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx, testbox.miny, testbox.minz-1,), Vector(testbox.width, testbox.height, testbox.length+1,))
		
	return testbox
	
def nonblank(selection, selectionbox):
	blocklist = numpy.array([]).astype(int)
	for (chunk, slices, point) in selection.getChunkSlices(selectionbox):
		blocklist = numpy.append(blocklist, chunk.Blocks[slices])
	list = numpy.copy(blocklist)
	list[list == 0] = 65531
	list[list == 65530] = 0
	return numpy.count_nonzero(list)
	
def all2(selection, testbox):
	blocklist = numpy.array([]).astype(int)
	datalist = numpy.array([]).astype(int)
	for (chunk, slices, point) in selection.getChunkSlices(testbox):
		blocklist = numpy.append(blocklist, chunk.Blocks[slices])
		datalist = numpy.append(datalist, chunk.Data[slices])
	if len(numpy.unique(blocklist)) == 1 and len(numpy.unique(datalist)) == 1:
		return [numpy.unique(blocklist)[0], numpy.unique(datalist)[0]]
	elif len(numpy.unique(blocklist)) == 2 and len(numpy.unique(datalist)) == 2 and 65529 in numpy.unique(blocklist):
		bl = numpy.unique(blocklist).tolist()
		bl.remove(65529)
		dl = numpy.unique(datalist).tolist()
		dl.remove(249)
		return [bl[0], dl[0]]
	else:
		return [-1, -1]
		
def delbox2(selection, testbox):
	for (chunk, slices, point) in selection.getChunkSlices(testbox):
		blocks = chunk.Blocks[slices]
		blocks[blocks != 65529] = 65529
		data = chunk.Data[slices]
		data[data != 249] = 249
		
def maxbox2(selection, tempbox, testbox):
	testboxx = pushx2(selection, tempbox, testbox[1])
	testboxy = pushy2(selection, tempbox, testbox[1])
	testboxz = pushz2(selection, tempbox, testbox[1])
	
	boxes = []
	
	for i in [pushz2(selection, tempbox, testboxy), pushy2(selection, tempbox, testboxz)]:
		boxes.append(pushx2(selection, tempbox, i))
	
	for i in [pushz2(selection, tempbox, testboxx), pushx2(selection, tempbox, testboxz)]:
		boxes.append(pushy2(selection, tempbox, i))
		
	for i in [pushy2(selection, tempbox, testboxx), pushx2(selection, tempbox, testboxy)]:
		boxes.append(pushz2(selection, tempbox, i))
		
	for i in boxes:
		if i.volume >= testbox[1].volume:
			testbox = [i.volume, i, all2(selection, i), None]
	return testbox
	
def pushx2(selection, tempbox, testbox):
	testbox2 = testbox
	while all2(selection, testbox2) != [-1, -1] and testbox2.maxx <= tempbox.maxx and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx, testbox.miny, testbox.minz,), Vector(testbox.width+1, testbox.height, testbox.length,))
	
	testbox2 = testbox
	while all2(selection, testbox2) != [-1, -1] and testbox2.minx >= tempbox.minx and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx-1, testbox.miny, testbox.minz,), Vector(testbox.width+1, testbox.height, testbox.length,))
		
	return testbox
	
	
def pushy2(selection, tempbox, testbox):
	testbox2 = testbox
	while all2(selection, testbox2) != [-1, -1] and testbox2.maxy <= tempbox.maxy and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx, testbox.miny, testbox.minz,), Vector(testbox.width, testbox.height+1, testbox.length,))
	
	testbox2 = testbox
	while all2(selection, testbox2) != [-1, -1] and testbox2.miny >= tempbox.miny and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx, testbox.miny-1, testbox.minz,), Vector(testbox.width, testbox.height+1, testbox.length,))
		
	return testbox
	
def pushz2(selection, tempbox, testbox):
	testbox2 = testbox
	while all2(selection, testbox2) != [-1, -1] and testbox2.maxz <= tempbox.maxz and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx, testbox.miny, testbox.minz,), Vector(testbox.width, testbox.height, testbox.length+1,))
	
	testbox2 = testbox
	while all2(selection, testbox2) != [-1, -1] and testbox2.minz >= tempbox.minz and testbox2.volume <= 32768:
		testbox = testbox2
		testbox2 = BoundingBox(Vector(testbox.minx, testbox.miny, testbox.minz-1,), Vector(testbox.width, testbox.height, testbox.length+1,))
		
	return testbox
	
def pull(direction, item, volumelist2, originaltemp):
	if item[1].width == 0 or item[1].height == 0 or item[1].length == 0:
		return False
	if direction == '+y':
		testbox = BoundingBox(Vector(item[1].minx, item[1].maxy-1, item[1].minz,), Vector(item[1].width, 1, item[1].length,))
	elif direction == '-y':
		testbox = BoundingBox(Vector(item[1].minx, item[1].miny, item[1].minz,), Vector(item[1].width, 1, item[1].length,))
	elif direction == '+x':
		testbox = BoundingBox(Vector(item[1].maxx-1, item[1].miny, item[1].minz,), Vector(1, item[1].height, item[1].length,))
	elif direction == '-x':
		testbox = BoundingBox(Vector(item[1].minx, item[1].miny, item[1].minz,), Vector(1, item[1].height, item[1].length,))
	elif direction == '+z':
		testbox = BoundingBox(Vector(item[1].minx, item[1].miny, item[1].maxz-1,), Vector(item[1].width, item[1].height, 1,))
	elif direction == '-z':
		testbox = BoundingBox(Vector(item[1].minx, item[1].miny, item[1].minz,), Vector(item[1].width, item[1].height, 1,))
	
	# for (x, y, z) in testbox.positions:
		# if item[2] == [originaltemp.blockAt(x, y, z), originaltemp.blockDataAt(x, y, z)]:
			# return False
	# return True
	
	for (x, y, z) in testbox.positions:
		tempblock = -1
		for volume in reversed(volumelist2):
			if (x, y, z) in volume[1]:
				tempblock = volume[2]
		if tempblock != [originaltemp.blockAt(x, y, z), originaltemp.blockDataAt(x, y, z)]:
			return False
	return True
		
	
def nonblank2(selection, selectionbox):
	blocklist = numpy.array([]).astype(int)
	for (chunk, slices, point) in selection.getChunkSlices(selectionbox):
		blocklist = numpy.append(blocklist, chunk.Blocks[slices])
	list = numpy.copy(blocklist)
	list[list == 0] = 65531
	list[list == 65530] = 0
	return numpy.count_nonzero(list)
	
	
					
# Converting Numerical IDs to name IDs (modified from some code from jgierer12, awesome coder ! Find him on https://twitter.com/jgierer12 )
# heavily modified by gentlegiantJGC
		
IDsToName = {0: "air",
		1: "stone",
		2: "grass",
		3: "dirt",
		4: "cobblestone",
		5: "planks",
		6: "sapling",
		7: "bedrock",
		8: "flowing_water",
		9: "water",
		10: "flowing_lava",
		11: "lava",
		12: "sand",
		13: "gravel",
		14: "gold_ore",
		15: "iron_ore",
		16: "coal_ore",
		17: "log",
		18: "leaves",
		19: "sponge",
		20: "glass",
		21: "lapis_ore",
		22: "lapis_block",
		23: "dispenser",
		24: "sandstone",
		25: "noteblock",
		26: "bed",
		27: "golden_rail",
		28: "detector_rail",
		29: "sticky_piston",
		30: "web",
		31: "tallgrass",
		32: "deadbush",
		33: "piston",
		34: "piston_head",
		35: "wool",
		36: "piston_extension",
		37: "yellow_flower",
		38: "red_flower",
		39: "brown_mushroom",
		40: "red_mushroom",
		41: "gold_block",
		42: "iron_block",
		43: "double_stone_slab",
		44: "stone_slab",
		45: "brick_block",
		46: "tnt",
		47: "bookshelf",
		48: "mossy_cobblestone",
		49: "obsidian",
		50: "torch",
		51: "fire",
		52: "mob_spawner",
		53: "oak_stairs",
		54: "chest",
		55: "redstone_wire",
		56: "diamond_ore",
		57: "diamond_block",
		58: "crafting_table",
		59: "wheat",
		60: "farmland",
		61: "furnace",
		62: "lit_furnace",
		63: "standing_sign",
		64: "wooden_door",
		65: "ladder",
		66: "rail",
		67: "stone_stairs",
		68: "wall_sign",
		69: "lever",
		70: "stone_pressure_plate",
		71: "iron_door",
		72: "wooden_pressure_plate",
		73: "redstone_ore",
		74: "lit_redstone_ore",
		75: "unlit_redstone_torch",
		76: "redstone_torch",
		77: "stone_button",
		78: "snow_layer",
		79: "ice",
		80: "snow",
		81: "cactus",
		82: "clay",
		83: "reeds",
		84: "jukebox",
		85: "fence",
		86: "pumpkin",
		87: "netherrack",
		88: "soul_sand",
		89: "glowstone",
		90: "portal",
		91: "lit_pumpkin",
		92: "cake",
		93: "unpowered_repeater",
		94: "powered_repeater",
		95: "stained_glass",
		96: "trapdoor",
		97: "monster_egg",
		98: "stonebrick",
		99: "brown_mushroom_block",
		100: "red_mushroom_block",
		101: "iron_bars",
		102: "glass_pane",
		103: "melon_block",
		104: "pumpkin_stem",
		105: "melon_stem",
		106: "vine",
		107: "fence_gate",
		108: "brick_stairs",
		109: "stone_brick_stairs",
		110: "mycelium",
		111: "waterlily",
		112: "nether_brick",
		113: "nether_brick_fence",
		114: "nether_brick_stairs",
		115: "nether_wart",
		116: "enchanting_table",
		117: "brewing_stand",
		118: "cauldron",
		119: "end_portal",
		120: "end_portal_frame",
		121: "end_stone",
		122: "dragon_egg",
		123: "redstone_lamp",
		124: "lit_redstone_lamp",
		125: "double_wooden_slab",
		126: "wooden_slab",
		127: "cocoa",
		128: "sandstone_stairs",
		129: "emerald_ore",
		130: "ender_chest",
		131: "tripwire_hook",
		132: "tripwire",
		133: "emerald_block",
		134: "spruce_stairs",
		135: "birch_stairs",
		136: "jungle_stairs",
		137: "command_block",
		138: "beacon",
		139: "cobblestone_wall",
		140: "flower_pot",
		141: "carrots",
		142: "potatoes",
		143: "wooden_button",
		144: "skull",
		145: "anvil",
		146: "trapped_chest",
		147: "light_weighted_pressure_plate",
		148: "heavy_weighted_pressure_plate",
		149: "unpowered_comparator",
		150: "powered_comparator",
		151: "daylight_detector",
		152: "redstone_block",
		153: "quartz_ore",
		154: "hopper",
		155: "quartz_block",
		156: "quartz_stairs",
		157: "activator_rail",
		158: "dropper",
		159: "stained_hardened_clay",
		160: "stained_glass_pane",
		161: "leaves2",
		162: "log2",
		163: "acacia_stairs",
		164: "dark_oak_stairs",
		165: "slime",
		166: "barrier",
		167: "iron_trapdoor",
		168: "prismarine",
		169: "sea_lantern",
		170: "hay_block",
		171: "carpet",
		172: "hardened_clay",
		173: "coal_block",
		174: "packed_ice",
		175: "double_plant",
		176: "standing_banner",
		177: "wall_banner",
		178: "daylight_detector_inverted",
		179: "red_sandstone",
		180: "red_sandstone_stairs",
		181: "double_stone_slab2",
		182: "stone_slab2",
		183: "spruce_fence_gate",
		184: "birch_fence_gate",
		185: "jungle_fence_gate",
		186: "dark_oak_fence_gate",
		187: "acacia_fence_gate",
		188: "spruce_fence",
		189: "birch_fence",
		190: "jungle_fence",
		191: "dark_oak_fence",
		192: "acacia_fence",
		193: "spruce_door",
		194: "birch_door",
		195: "jungle_door",
		196: "acacia_door",
		197: "dark_oak_door",
		198: "end_rod",
		
		199: "chorus_plant",
		200: "chorus_flower",
		201: "purpur_block",
		202: "purpur_pillar",
		203: "purpur_stairs",
		204: "purpur_double_slab", 	
		205: "purpur_slab",
		206: "end_bricks",
		207: "beetroots",
		208: "grass_path",
		209: "end_gateway",
		210: "repeating_command_block",
		211: "chain_command_block",
		
		255: "structure_block"}
		
defaultnbt = {
	'Anger' : ['0'],
	'Angry' : ['0'],
	'BatFlags' : ['0'],
	'Bred' : ['0'],
	'CanBreakDoors' : ['0'],
	'CanPickUpLoot' : ['0'],
	'Career' : ['0'],
	'CareerLevel' : ['0'],
	'CatType' : ['0'],
	'ChestedHorse' : ['0'],
	'CollarColor' : ['14'],
	'Color' : ['0'],
	'Command' : [''],
	'ConversionTime' : ['-1'],
	'CustomName' : ['@'],
	'CustomNameVisible' : ['0'],
	'DeathTime' : ['0'],
	'DisabledSlots' : ['0'],
	'DropChances' : ['0.0850000008941f,0.0850000008941f,0.0850000008941f,0.0850000008941f,0.0850000008941f'],
	'EatingHaystack' : ['0'],
	'Elder' : ['0'],
	'Equipment' : ['{},{},{},{},{}'],
	'ExplosionPower' : ['1'],
	'ExplosionRadius' : ['3'],
	'Facing' : ['0'],
	'FallDistance' : ['0.0'],
	'Fire' : ['-1', '0'],
	'ForcedAge' : ['0'],
	'Fuel' : ['0'],
	'HasReproduced' : ['0'],
	'HurtBy' : [''],
	'HurtByTimestamp' : ['0'],
	'HurtTime' : ['0'],
	'InLove' : ['0'],
	'Inventory' : [''],
	'Invisible' : ['0'],
	'Invulnerable' : ['0'],
	'IsChickenJockey' : ['0'],
	'Items' : [''],
	'Leashed' : ['0'],
	'MoreCarrotTicks' : ['0'],
	'Motive' : ['Kebab'],
	'NoBasePlate' : ['0'],
	'NoGravity' : ['0'],
	'PersistenceRequired' : ['0'],
	'PlayerCreated' : ['0'],
	'PlayerSpawned' : ['0'],
	'PortalCooldown' : ['0'],
	'Pose' : [''],
	'PushX' : ['0.0'],
	'PushZ' : ['0.0'],
	'Riches' : ['0'],
	'Rotation' : ['0.0f,0.0f'],
	'Saddle' : ['0'],
	'Sheared' : ['0'],
	'ShowArms' : ['0'],
	'Sitting' : ['0'],
	'SkeletonType' : ['0'],
	'Small' : ['0'],
	'SuccessCount' : ['0'],
	'TNTFuse' : ['-1'],
	'Tame' : ['0'],
	'Temper' : ['0'],
	'TrackOutput' : ['1'],
	'TransferCooldown' : ['0'],
	'Type' : ['0'],
	'Variant' : ['256'],
	'Willing' : ['0'],
	'carried' : ['0'],
	'carriedData' : ['0'],
	'damage' : ['2.0'],
	'ignited' : ['0'],
	'ownerName' : ['']
	# 'Fuse' : ['30'],
	# 'pickup' : ['0'],
	
	
	#I may add these to the tick boxes at the top. For now that is just a possibility
	# 'Anger' : ['0'],
	# 'Angry' : ['0'],
	# 'BatFlags' : ['0'],
	# 'Bred' : ['0'],
	# 'CanBreakDoors' : ['0'],
	# 'CanPickUpLoot' : ['0'],
	# 'Career' : ['0'],
	# 'CareerLevel' : ['0'],
	# 'CatType' : ['0'],
	# 'ChestedHorse' : ['0'],
	# 'CollarColor' : ['14'],
	# 'Color' : ['0'],
	# 'ConversionTime' : ['-1'],
	# 'DeathTime' : ['0'],
	# 'DisabledSlots' : ['0'],
	# 'DropChances' : ['0.0850000008941f,0.0850000008941f,0.0850000008941f,0.0850000008941f,0.0850000008941f'],
	# 'EatingHaystack' : ['0'],
	# 'Elder' : ['0'],
	# 'Equipment' : ['{},{},{},{},{}'],
	# 'ExplosionPower' : ['1'],
	# 'ExplosionRadius' : ['3'],
	# 'FallDistance' : ['0.0'],
	# 'Fire' : ['-1', '0'],
	# 'ForcedAge' : ['0'],
	# 'Fuel' : ['0'],
	# 'HasReproduced' : ['0'],
	# 'HurtBy' : [''],
	# 'HurtByTimestamp' : ['0'],
	# 'HurtTime' : ['0'],
	# 'InLove' : ['0'],
	# 'Inventory' : [''],
	# 'Invisible' : ['0'],
	# 'Invulnerable' : ['0'],
	# 'IsChickenJockey' : ['0'],
	# 'Items' : [''],
	# 'Leashed' : ['0'],
	# 'MoreCarrotTicks' : ['0'],
	# 'Motive' : ['Kebab'],
	# 'NoBasePlate' : ['0'],
	# 'NoGravity' : ['0'],
	# 'PersistenceRequired' : ['0'],
	# 'PlayerCreated' : ['0'],
	# 'PlayerSpawned' : ['0'],
	# 'PortalCooldown' : ['0'],
	# 'Pose' : [''],
	# 'PushX' : ['0.0'],
	# 'PushZ' : ['0.0'],
	# 'Riches' : ['0'],
	# 'Rotation' : ['0.0f,0.0f'],
	# 'Saddle' : ['0'],
	# 'Sheared' : ['0'],
	# 'ShowArms' : ['0'],
	# 'Sitting' : ['0'],
	# 'Size' : ['1'],
	# 'SkeletonType' : ['0'],
	# 'Small' : ['0'],
	# 'SuccessCount' : ['0'],
	# 'TNTFuse' : ['-1'],
	# 'Tame' : ['0'],
	# 'ownerName' : [''],
	# 'ignited' : ['0'],
	# 'damage' : ['2.0'],
	# 'carriedData' : ['0'],
	# 'carried' : ['0'],
	# 'Willing' : ['0'],
	# 'Type' : ['0'],
	# 'Variant' : ['256'],
	# 'TransferCooldown' : ['0'],
	# 'TrackOutput' : ['1'],
	# 'Tame' : ['0'],
	# 'Temper' : ['0'],
	}