#A mcedit filter by xafonyz
#Modified and updated by gentlegiantJGC. Now works in 1.8 and with entities
#https://www.youtube.com/gentlegiantJGC
#Give it a structure, it will create a single command block that can setblock the whole structure
#Feel free to use it for any purpose, or to reuse some pieces of code.
#If you do it, you can still quote me : xafonyz, https://www.youtube.com/xafonyzen

#In fact I also reused some code from other filters there. So thanks to Sethbling and CrushedPixel, two awesome youtubers and coders.

from pymclevel import nbt, TAG_Compound, TAG_List, TAG_Int_Array, TAG_Byte_Array, TAG_String, TAG_Long, TAG_Int, TAG_Short, TAG_Byte, TAG_Double, TAG_Float
from pymclevel import Entity
from pymclevel import MCSchematic
from pymclevel import TileEntity
from pymclevel import ChunkNotPresent

from pymclevel import MCSchematic			# This was taken from a texelelf filter. I don't understand it but I understand what it does
import inspect								# ditto

displayName = "one-command structure spawner" 

inputs = [
(("Command block positioning", ("Absolute", "Relative")),
("Include air", False),
("Include blocks", True),
("Include entities", True),
("Relative position", ("South-West", "South-East", "North-West", "North-East")),
("command block height (relative only)", 0),
("Main", "title"),),

(("Remove Irrelevant tags", "label"),
("LastOutput", True),
("UUID", True),
("AbsorptionAmount", True),
("Air", True),
("Attributes", True),
("DeathTime", True),
("Dimension", True),
("Fire", True),
("HurtByTimestamp", True),
("PortalCooldown", True),
("Data tags", "title"),),
]


def perform(level, box, options):
	for (chunk, slices, point) in level.getChunkSlices(box):
		if options["Include blocks"] == True:
			for t in chunk.TileEntities:
				x = t["x"].value
				y = t["y"].value
				z = t["z"].value
				if (x,y,z) in box:
					if options["LastOutput"] == True:
						if "LastOutput" in t:
							del t["LastOutput"]
		if options["Include entities"] == True:
			for e in chunk.Entities:
				x = e["Pos"][0].value
				y = e["Pos"][1].value
				z = e["Pos"][2].value
				if (x,y,z) in box:
					if options["LastOutput"] == True and "LastOutput" in e:
						del e["LastOutput"]
					if options["UUID"] == True:
						if "UUIDMost" in e:
							del e["UUIDMost"]	
						if "UUIDLeast" in e:
							del e["UUIDLeast"]
					if options["AbsorptionAmount"] == True:
						if "AbsorptionAmount" in e:
							del e["AbsorptionAmount"]
					if options["Air"] == True:
						if "Air" in e:
							del e["Air"]
					if options["Attributes"] == True:
						if "Attributes" in e:
							del e["Attributes"]
					if options["DeathTime"] == True:
						if "DeathTime" in e:
							del e["DeathTime"]
					if options["Dimension"] == True:
						if "Dimension" in e:
							del e["Dimension"]
					if options["Fire"] == True:
						if "Fire" in e:
							del e["Fire"]
					if options["HurtByTimestamp"] == True:
						if "HurtByTimestamp" in e:
							del e["HurtByTimestamp"]
					if options["PortalCooldown"] == True:
						if "PortalCooldown" in e:
							del e["PortalCooldown"]
				
	
	#Getting inputs
	includeAir = options["Include air"]
	includeBlocks = options["Include blocks"]
	cmdBlockHeight = options["command block height (relative only)"]
	relativePos = options["Relative position"]
	cmdBlockPosing = options["Command block positioning"]
	editor = inspect.stack()[1][0].f_locals.get('self', None).editor
	
	commandlist = []
	cmdtemp = ''
	bracketsToClosetemp = 0
	popOffBlocks = [6,8,9,10,11,12,13,27,28,31,32,36,37,38,39,40,50,51,55,59,63,64,65,66,68,69,70,71,72,75,76,77,78,81,83,90,92,93,94,96,104,105,106,111,115,119,122,127,131,140,141,142,143,147,148,149,150,157,167,171,175,176,177,193,194,195,196,197]
	solids = []
	
	#Initialising command
	cmd="/summon FallingSand ~ ~+4 ~-0.1 {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
	bracketsToClose=0

	#Finding redstone/doors/etc. ...
	if options["Include blocks"] == True:
		for y in xrange(box.miny,box.maxy):
			
			for x in xrange(box.minx,box.maxx):
				
				
				for z in xrange(box.minz,box.maxz):
					
					if level.blockAt(x,y,z) in popOffBlocks:
						if cmdBlockPosing=="Absolute":
							blockX = x
							blockY = y
							blockZ = z
						
						elif cmdBlockPosing=="Relative":
							blockY=y-box.miny-cmdBlockHeight-2
							if relativePos=="North-West":
								blockX=x-box.minx+2
								blockZ=z-box.minz+2
							if relativePos=="South-West":
								blockX=x-box.minx+2
								blockZ=z-box.maxz-1
							if relativePos=="North-East":
								blockX=x-box.maxx-1
								blockZ=z-box.minz+2
							if relativePos=="South-East":
								blockX=x-box.maxx-1
								blockZ=z-box.maxz-1
						else :
							raise Exception ("WTF?")
							
						if(includeBlocks==True and level.blockAt(x,y,z)!=0):
							bracketsToClosetemp = 1
							if level.tileEntityAt(x,y,z)==None:
								cmdtemp='{id:MinecartCommandBlock,Command:"setblock'+ {True: " ~", False: " "}[cmdBlockPosing=="Relative"] +str(blockX)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockY)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockZ)+' '+IDsToName[str(level.blockAt(x,y,z))]+' '+str(level.blockDataAt(x,y,z))+' replace",Riding:'

							if level.tileEntityAt(x,y,z) !=None:
								cmdtemp= '{id:MinecartCommandBlock,Command:"setblock'+ {True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockX)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(+blockY)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockZ)+' '+IDsToName[str(level.blockAt(x,y,z))]+' '+str(level.blockDataAt(x,y,z))+' replace {'+NBT2Command(level.tileEntityAt(x,y,z))+'}",Riding:'
								
						if includeAir==True and level.blockAt(x,y,z)==0:
							bracketsToClosetemp = 1
							if level.tileEntityAt(x,y,z)==None:
								cmdtemp='{id:MinecartCommandBlock,Command:"setblock'+ {True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockX)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockY)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockZ)+' '+IDsToName[str(level.blockAt(x,y,z))]+' '+str(level.blockDataAt(x,y,z))+' replace",Riding:'

							if level.tileEntityAt(x,y,z) != None:
								cmdtemp='{id:MinecartCommandBlock,Command:"setblock'+ {True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockX)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockY)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockZ)+' '+IDsToName[str(level.blockAt(x,y,z))]+' '+str(level.blockDataAt(x,y,z))+' replace {'+NBT2Command(level.tileEntityAt(x,y,z))+'}",Riding:'
						
						if cmdtemp != '':
							if len(cmd) + len(cmdtemp) + bracketsToClose + 195 > 32760 and cmdBlockPosing=="Absolute":
								cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
								while bracketsToClose > 0:
									cmd += "}"
									bracketsToClose -= 1
								commandlist.append(cmd)

								cmd="/summon FallingSand ~ ~+4 ~-0.1 {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
								bracketsToClose=0
							
							cmd += cmdtemp
							cmdtemp = ''
							bracketsToClose += bracketsToClosetemp
							bracketsToClosetemp = 0
					
					else:
						solids.append([x,y,z])
						

		if len(cmd) + 94 + bracketsToClose + 195 > 32760 and cmdBlockPosing=="Absolute":
			cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
			while bracketsToClose > 0:
				cmd += "}"
				bracketsToClose -= 1
			commandlist.append(cmd)

			cmd="/summon FallingSand ~ ~+4 ~-0.1 {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
			bracketsToClose=0
		
		else:
			cmd += '{id:MinecartCommandBlock,Command:buffer,Riding:{id:MinecartCommandBlock,Command:buffer,Riding:'
			bracketsToClose += 2
		
		cmdtemp = ''
		bracketsToClosetemp = 0
						
	#Building command
		for s in solids:
			x = s[0]
			y = s[1]
			z = s[2]
			if cmdBlockPosing=="Absolute":
				blockX = x
				blockY = y
				blockZ = z
			
			elif cmdBlockPosing=="Relative":
				blockY=y-box.miny-cmdBlockHeight-2
				if relativePos=="North-West":
					blockX=x-box.minx+2
					blockZ=z-box.minz+2
				if relativePos=="South-West":
					blockX=x-box.minx+2
					blockZ=z-box.maxz-1
				if relativePos=="North-East":
					blockX=x-box.maxx-1
					blockZ=z-box.minz+2
				if relativePos=="South-East":
					blockX=x-box.maxx-1
					blockZ=z-box.maxz-1
			else :
				raise Exception ("WTF?")
				
			if(includeBlocks==True and level.blockAt(x,y,z)!=0):
				bracketsToClosetemp = 1
				if level.tileEntityAt(x,y,z)==None:
					cmdtemp='{id:MinecartCommandBlock,Command:"setblock'+ {True: " ~", False: " "}[cmdBlockPosing=="Relative"] +str(blockX)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockY)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockZ)+' '+IDsToName[str(level.blockAt(x,y,z))]+' '+str(level.blockDataAt(x,y,z))+' replace",Riding:'

				if level.tileEntityAt(x,y,z) !=None:
					cmdtemp= '{id:MinecartCommandBlock,Command:"setblock'+ {True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockX)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(+blockY)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockZ)+' '+IDsToName[str(level.blockAt(x,y,z))]+' '+str(level.blockDataAt(x,y,z))+' replace {'+NBT2Command(level.tileEntityAt(x,y,z))+'}",Riding:'
					
			if includeAir==True and level.blockAt(x,y,z)==0:
				bracketsToClosetemp = 1
				if level.tileEntityAt(x,y,z)==None:
					cmdtemp='{id:MinecartCommandBlock,Command:"setblock'+ {True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockX)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockY)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockZ)+' '+IDsToName[str(level.blockAt(x,y,z))]+' '+str(level.blockDataAt(x,y,z))+' replace",Riding:'

				if level.tileEntityAt(x,y,z) != None:
					cmdtemp='{id:MinecartCommandBlock,Command:"setblock'+ {True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockX)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockY)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(blockZ)+' '+IDsToName[str(level.blockAt(x,y,z))]+' '+str(level.blockDataAt(x,y,z))+' replace {'+NBT2Command(level.tileEntityAt(x,y,z))+'}",Riding:'
			
			if cmdtemp != '':
				if len(cmd) + len(cmdtemp) + bracketsToClose + 195 > 32760 and cmdBlockPosing=="Absolute":
					cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
					while bracketsToClose > 0:
						cmd += "}"
						bracketsToClose -= 1
					commandlist.append(cmd)

					cmd="/summon FallingSand ~ ~+4 ~-0.1 {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
					bracketsToClose=0
				
				cmd += cmdtemp
				cmdtemp = ''
				bracketsToClose += bracketsToClosetemp
				bracketsToClosetemp = 0
				
	if options["Include entities"] == True:
		for (chunk, slices, point) in level.getChunkSlices(box):
			for e in chunk.Entities:
				ex = e["Pos"][0].value
				ey = e["Pos"][1].value
				ez = e["Pos"][2].value
				if (ex,ey,ez) in box:
					if cmdBlockPosing=="Absolute":
						entityX = ex
						entityY = ey
						entityZ = ez
				
					elif cmdBlockPosing=="Relative":
						entityY=ey-box.miny-cmdBlockHeight-2.05
						if relativePos=="North-West":
							entityX=ex-box.minx+1.5
							entityZ=ez-box.minz+1.7
						if relativePos=="South-West":
							entityX=ex-box.minx+1.5
							entityZ=ez-box.maxz-1.3
						if relativePos=="North-East":
							entityX=ex-box.maxx-1.5
							entityZ=ez-box.minz+1.7
						if relativePos=="South-East":
							entityX=ex-box.maxx-1.5
							entityZ=ez-box.maxz-1.3
					else :
						raise Exception ("WTF?")

					cmdtemp= "{id:MinecartCommandBlock,Command:\"summon "+str(e["id"].value)+" "+ {True: "~", False: ""}[cmdBlockPosing=="Relative"]+str(entityX)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(+entityY)+{True: " ~", False: " "}[cmdBlockPosing=="Relative"]+str(entityZ)+" {"+NBT2Command(e)+"}\",Riding:"
					if len(cmd) + len(cmdtemp) + bracketsToClose + 195 > 32760 and cmdBlockPosing=="Absolute":
						cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
						while bracketsToClose > 0:
							cmd += "}"
							bracketsToClose -= 1
						commandlist.append(cmd)

						cmd="/summon FallingSand ~ ~+4 ~-0.1 {Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:fill ~ ~1 ~-1 ~ ~-5 ~ air},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:FallingSand,Time:1,Block:minecraft:command_block,TileEntityData:{Command:kill @e[type=MinecartCommandBlock,r=4]},Riding:{id:FallingSand,Time:1,Data:0,TileID:1,Riding:{id:MinecartCommandBlock,Command:setblock ~ ~ ~ air,Riding:{id:MinecartCommandBlock,Command:/kill @e[type=Item,r=4],Riding:"
						bracketsToClose=0
					cmd += cmdtemp
					bracketsToClose += 1
					
	
	#Closing command's brackets
	if cmdBlockPosing=="Relative":
		#Ending command
		cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
		while bracketsToClose > 0:
			cmd += "}"
			bracketsToClose -= 1
		if len(cmd) > 32767:
			raise Exception ("Command too long by "+str(len(cmd)-32767)+" characters")
		
		#Finding control command block's place and placing it
		if relativePos=="North-West":
			level.setBlockAt(box.minx-2,box.miny+cmdBlockHeight,box.minz-2,137)
			setCmd(box.minx-2,box.miny+cmdBlockHeight,box.minz-2,cmd,level)
		if relativePos=="South-West":
			level.setBlockAt(box.minx-2,box.miny+cmdBlockHeight,box.maxz+1,137)
			setCmd(box.minx-2,box.miny+cmdBlockHeight,box.maxz+1,cmd,level)
		if relativePos=="North-East":
			level.setBlockAt(box.maxx+1,box.miny+cmdBlockHeight,box.minz-2,137)
			setCmd(box.maxx+1,box.miny+cmdBlockHeight,box.minz-2,cmd,level)
		if relativePos=="South-East":
			level.setBlockAt(box.maxx+1,box.miny+cmdBlockHeight,box.maxz+1,137)
			setCmd(box.maxx+1,box.miny+cmdBlockHeight,box.maxz+1,cmd,level)
			
			
			
	if cmdBlockPosing=="Absolute":
		cmd+="{id:MinecartCommandBlock,Command:buffer,Riding:{id:FallingSand,Time:1,Data:0,TileID:157,Riding:{id:FallingSand,Time:1,Data:0,TileID:152,Riding:{id:Item,Age:5996,Motion:[0.0,0.0,-0.1]}}}}}}}}}}}}"
		while bracketsToClose > 0:
			cmd += "}"
			bracketsToClose -= 1
		commandlist.append(cmd)
		schematic = MCSchematic((len(commandlist)*2, 1, 1), mats=level.materials)
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
					command += r"\""
					command += ((str.replace(nbtData[tag].value.encode("unicode-escape"), r'"',r'\"')).encode("unicode-escape")).replace(r'"',r'\"')
					command += r"\""
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
			command += r"\""
			command += ((str.replace(nbtData[tag].value.encode("unicode-escape"), r'"',r'\"')).encode("unicode-escape")).replace(r'"',r'\"')
			command += r"\""
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
		
	#Sets a command on a block
def setCmd(x,y,z,cmd,level):
	control = TAG_Compound()
	control["id"] = TAG_String(u'Control')
	control["CustomName"] = TAG_String(u"builder")
	control["z"] = TAG_Int(z)
	control["y"] = TAG_Int(y)
	control["x"] = TAG_Int(x)
	control["Command"] = TAG_String(cmd)
	chunk = level.getChunk((int(x/16)), (int(z/16)))
	chunk.TileEntities.append(control)
	chunk.dirty = True
	
# Fast data access (Credits to Sethbling, http://youtube.com/SethBling )
from pymclevel import ChunkNotPresent
GlobalChunkCache = {}
GlobalLevel = None

def getChunk(x, z):
	global GlobalChunkCache
	global GlobalLevel
	chunkCoords = (x>>4, z>>4)
	if chunkCoords not in GlobalChunkCache:
		try:
			GlobalChunkCache[chunkCoords] = GlobalLevel.getChunk(x>>4, z>>4)
		except ChunkNotPresent:
			return None
	
	return GlobalChunkCache[chunkCoords]

					
# Converting Numerical IDs to name IDs (modified from some code from jgierer12, awesome coder ! Find him on https://twitter.com/jgierer12 )
		
IDsToName = {"0": "minecraft:air",
		"1": "minecraft:stone",
		"2": "minecraft:grass",
		"3": "minecraft:dirt",
		"4": "minecraft:cobblestone",
		"5": "minecraft:planks",
		"6": "minecraft:sapling",
		"7": "minecraft:bedrock",
		"8": "minecraft:flowing_water",
		"9": "minecraft:water",
		"10": "minecraft:flowing_lava",
		"11": "minecraft:lava",
		"12": "minecraft:sand",
		"13": "minecraft:gravel",
		"14": "minecraft:gold_ore",
		"15": "minecraft:iron_ore",
		"16": "minecraft:coal_ore",
		"17": "minecraft:log",
		"18": "minecraft:leaves",
		"19": "minecraft:sponge",
		"20": "minecraft:glass",
		"21": "minecraft:lapis_ore",
		"22": "minecraft:lapis_block",
		"23": "minecraft:dispenser",
		"24": "minecraft:sandstone",
		"25": "minecraft:noteblock",
		"26": "minecraft:bed",
		"27": "minecraft:golden_rail",
		"28": "minecraft:detector_rail",
		"29": "minecraft:sticky_piston",
		"30": "minecraft:web",
		"31": "minecraft:tallgrass",
		"32": "minecraft:deadbush",
		"33": "minecraft:piston",
		"34": "minecraft:piston_head",
		"35": "minecraft:wool",
		"36": "minecraft:piston_extension",
		"37": "minecraft:yellow_flower",
		"38": "minecraft:red_flower",
		"39": "minecraft:brown_mushroom",
		"40": "minecraft:red_mushroom",
		"41": "minecraft:gold_block",
		"42": "minecraft:iron_block",
		"43": "minecraft:double_stone_slab",
		"44": "minecraft:stone_slab",
		"45": "minecraft:brick_block",
		"46": "minecraft:tnt",
		"47": "minecraft:bookshelf",
		"48": "minecraft:mossy_cobblestone",
		"49": "minecraft:obsidian",
		"50": "minecraft:torch",
		"51": "minecraft:fire",
		"52": "minecraft:mob_spawner",
		"53": "minecraft:oak_stairs",
		"54": "minecraft:chest",
		"55": "minecraft:redstone_wire",
		"56": "minecraft:diamond_ore",
		"57": "minecraft:diamond_block",
		"58": "minecraft:crafting_table",
		"59": "minecraft:wheat",
		"60": "minecraft:farmland",
		"61": "minecraft:furnace",
		"62": "minecraft:lit_furnace",
		"63": "minecraft:standing_sign",
		"64": "minecraft:wooden_door",
		"65": "minecraft:ladder",
		"66": "minecraft:rail",
		"67": "minecraft:stone_stairs",
		"68": "minecraft:wall_sign",
		"69": "minecraft:lever",
		"70": "minecraft:stone_pressure_plate",
		"71": "minecraft:iron_door",
		"72": "minecraft:wooden_pressure_plate",
		"73": "minecraft:redstone_ore",
		"74": "minecraft:lit_redstone_ore",
		"75": "minecraft:unlit_redstone_torch",
		"76": "minecraft:redstone_torch",
		"77": "minecraft:stone_button",
		"78": "minecraft:snow_layer",
		"79": "minecraft:ice",
		"80": "minecraft:snow",
		"81": "minecraft:cactus",
		"82": "minecraft:clay",
		"83": "minecraft:reeds",
		"84": "minecraft:jukebox",
		"85": "minecraft:fence",
		"86": "minecraft:pumpkin",
		"87": "minecraft:netherrack",
		"88": "minecraft:soul_sand",
		"89": "minecraft:glowstone",
		"90": "minecraft:portal",
		"91": "minecraft:lit_pumpkin",
		"92": "minecraft:cake",
		"93": "minecraft:unpowered_repeater",
		"94": "minecraft:powered_repeater",
		"95": "minecraft:stained_glass",
		"96": "minecraft:trapdoor",
		"97": "minecraft:monster_egg",
		"98": "minecraft:stonebrick",
		"99": "minecraft:brown_mushroom_block",
		"100": "minecraft:red_mushroom_block",
		"101": "minecraft:iron_bars",
		"102": "minecraft:glass_pane",
		"103": "minecraft:melon_block",
		"104": "minecraft:pumpkin_stem",
		"105": "minecraft:melon_stem",
		"106": "minecraft:vine",
		"107": "minecraft:fence_gate",
		"108": "minecraft:brick_stairs",
		"109": "minecraft:stone_brick_stairs",
		"110": "minecraft:mycelium",
		"111": "minecraft:waterlily",
		"112": "minecraft:nether_brick",
		"113": "minecraft:nether_brick_fence",
		"114": "minecraft:nether_brick_stairs",
		"115": "minecraft:nether_wart",
		"116": "minecraft:enchanting_table",
		"117": "minecraft:brewing_stand",
		"118": "minecraft:cauldron",
		"119": "minecraft:end_portal",
		"120": "minecraft:end_portal_frame",
		"121": "minecraft:end_stone",
		"122": "minecraft:dragon_egg",
		"123": "minecraft:redstone_lamp",
		"124": "minecraft:lit_redstone_lamp",
		"125": "minecraft:double_wooden_slab",
		"126": "minecraft:wooden_slab",
		"127": "minecraft:cocoa",
		"128": "minecraft:sandstone_stairs",
		"129": "minecraft:emerald_ore",
		"130": "minecraft:ender_chest",
		"131": "minecraft:tripwire_hook",
		"132": "minecraft:tripwire",
		"133": "minecraft:emerald_block",
		"134": "minecraft:spruce_stairs",
		"135": "minecraft:birch_stairs",
		"136": "minecraft:jungle_stairs",
		"137": "minecraft:command_block",
		"138": "minecraft:beacon",
		"139": "minecraft:cobblestone_wall",
		"140": "minecraft:flower_pot",
		"141": "minecraft:carrots",
		"142": "minecraft:potatoes",
		"143": "minecraft:wooden_button",
		"144": "minecraft:skull",
		"145": "minecraft:anvil",
		"146": "minecraft:trapped_chest",
		"147": "minecraft:light_weighted_pressure_plate",
		"148": "minecraft:heavy_weighted_pressure_plate",
		"149": "minecraft:unpowered_comparator",
		"150": "minecraft:powered_comparator",
		"151": "minecraft:daylight_detector",
		"152": "minecraft:redstone_block",
		"153": "minecraft:quartz_ore",
		"154": "minecraft:hopper",
		"155": "minecraft:quartz_block",
		"156": "minecraft:quartz_stairs",
		"157": "minecraft:activator_rail",
		"158": "minecraft:dropper",
		"159": "minecraft:stained_hardened_clay",
		"160": "minecraft:stained_glass_pane",
		"161": "minecraft:leaves2",
		"162": "minecraft:log2",
		"163": "minecraft:acacia_stairs",
		"164": "minecraft:dark_oak_stairs",
		"165": "minecraft:slime",
		"166": "minecraft:barrier",
		"167": "minecraft:iron_trapdoor",
		"168": "minecraft:prismarine",
		"169": "minecraft:sea_lantern",
		"170": "minecraft:hay_block",
		"171": "minecraft:carpet",
		"172": "minecraft:hardened_clay",
		"173": "minecraft:coal_block",
		"174": "minecraft:packed_ice",
		"175": "minecraft:double_plant",
		"176": "minecraft:standing_banner",
		"177": "minecraft:wall_banner",
		"178": "minecraft:daylight_detector_inverted",
		"179": "minecraft:red_sandstone",
		"180": "minecraft:red_sandstone_stairs",
		"181": "minecraft:double_stone_slab2",
		"182": "minecraft:stone_slab2",
		"183": "minecraft:spruce_fence_gate",
		"184": "minecraft:birch_fence_gate",
		"185": "minecraft:jungle_fence_gate",
		"186": "minecraft:dark_oak_fence_gate",
		"187": "minecraft:acacia_fence_gate",
		"188": "minecraft:spruce_fence",
		"189": "minecraft:birch_fence",
		"190": "minecraft:jungle_fence",
		"191": "minecraft:dark_oak_fence",
		"192": "minecraft:acacia_fence",
		"193": "minecraft:spruce_door",
		"194": "minecraft:birch_door",
		"195": "minecraft:jungle_door",
		"196": "minecraft:acacia_door",
		"197": "minecraft:dark_oak_door"}