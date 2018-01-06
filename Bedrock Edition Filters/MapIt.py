import os
from copy import deepcopy
from pymclevel.materials import alphaMaterials
from pymclevel import nbt, TAG_Compound, TAG_List, TAG_Int, TAG_Byte_Array, TAG_Short, TAG_Byte, TAG_String, TAG_Double, TAG_Float, TAG_Long
from pymclevel import BoundingBox, saveFileDir
from pymclevel.leveldbpocket import loadNBTCompoundList
import mcplatform
import pygame
import numpy
import math

displayName = "Map It!"

inputs = (
	("Thanks go to gentlegiantJGC (https://twitter.com/gentlegiantJGC) for an updated color palette!","label"),
	("Item Frames are facing:",("Westwards (+X to -X)","Eastwards (-X to +X)","Northwards (+Z to -Z)","Southwards (-Z to +Z)")),
	("If selection is too small for image size:",("Cancel Image Processing","Create Chests Filled with Maps","Scale to selection")),
	("Item Frame backing block (replaces air blocks only):",alphaMaterials.Stone),
	("Item Frames are invulnerable:",True),
	("Transparency Mode:",("None","Use Default Color (#FF00FF)","User-Specified Color Below")),
	("Transparency Color:",("string","value=#FF00FF")),
	("Use Nearest-Color Transparency (recommended for lossy image formats):",False),
	("Image path:",("string","value=None")),
	)
	
map_palette = {
	(88,124,39):4,(108,151,47):5,(125,176,55):6,(66,93,29):7,(172,162,114):8,(210,199,138):9,(244,230,161):10,
	(128,122,85):11,(138,138,138):12,(169,169,169):13,(197,197,197):14,(104,104,104):15,(178,0,0):16,(217,0,0):17,
	(252,0,0):18,(133,0,0):19,(111,111,178):20,(136,136,217):21,(158,158,252):22,(83,83,133):23,(116,116,116):24,
	(142,142,142):25,(165,165,165):26,(87,87,87):27,(0,86,0):28,(0,105,0):29,(0,123,0):30,(0,64,0):31,(178,178,178):32,
	(217,217,217):33,(252,252,252):34,(133,133,133):35,(114,117,127):36,(139,142,156):37,(162,166,182):38,(85,87,96):39,
	(105,75,53):40,(128,93,65):41,(149,108,76):42,(78,56,39):43,(78,78,78):44,(95,95,95):45,(111,111,111):46,(58,58,58):47,
	(44,44,178):48,(54,54,217):49,(63,63,252):50,(33,33,133):51,(99,83,49):52,(122,101,61):53,(141,118,71):54,(74,62,38):55,
	(178,175,170):56,(217,214,208):57,(252,249,242):58,(133,131,127):59,(150,88,36):60,(184,108,43):61,(213,125,50):62,
	(113,66,27):63,(124,52,150):64,(151,64,184):65,(176,75,213):66,(93,39,113):67,(71,107,150):68,(87,130,184):69,(101,151,213):70,
	(53,80,113):71,(159,159,36):72,(195,195,43):73,(226,226,50):74,(120,120,27):75,(88,142,17):76,(108,174,21):77,(125,202,25):78,
	(66,107,13):79,(168,88,115):80,(206,108,140):81,(239,125,163):82,(126,66,86):83,(52,52,52):84,(64,64,64):85,(75,75,75):86,
	(39,39,39):87,(107,107,107):88,(130,130,130):89,(151,151,151):90,(80,80,80):91,(52,88,107):92,(64,108,130):93,(75,125,151):94,
	(39,66,80):95,(88,43,124):96,(108,53,151):97,(125,62,176):98,(66,33,93):99,(36,52,124):100,(43,64,151):101,(50,75,176):102,
	(27,39,93):103,(71,52,36):104,(87,64,43):105,(101,75,50):106,(53,39,27):107,(71,88,36):108,(87,108,43):109,(101,125,50):110,
	(53,66,27):111,(107,36,36):112,(130,43,43):113,(151,50,50):114,(80,27,27):115,(17,17,17):116,(21,21,21):117,(25,25,25):118,
	(13,13,13):119,(174,166,53):120,(212,203,65):121,(247,235,76):122,(130,125,39):123,(63,152,148):124,(78,186,181):125,
	(91,216,210):126,(47,114,111):127,(51,89,178):128,(62,109,217):129,(73,129,252):130,(39,66,133):131,(0,151,39):132,(0,185,49):133,
	(0,214,57):134,(0,113,30):135,(90,59,34):136,(110,73,41):137,(127,85,48):138,(67,44,25):139,(78,1,0):140,(95,1,0):141,(111,2,0):142,(58,1,0):143,
	}

mapkeys = map_palette.keys()
cache = deepcopy(map_palette)

def FindClosestPaletteIndex(r,g,b,trans,nearest):
	if not nearest and trans != None:
		if (r,g,b) == trans:
			return 0
		
	distance = float("inf")
	pal = None
	for (pr, pg, pb) in mapkeys:
		newdist = (pr - r)**2 + (pg - g)**2 + (pb - b)**2
		if newdist <= distance:
			distance = newdist
			pal = (pr, pg, pb)
	else:
		if nearest and trans != None:
			ar, ag, ab = trans
			newdist = (ar - r)**2 + (ag - g)**2 + (ab - b)**2
			if newdist <= distance:
				cache[(r,g,b)] = 0
				return 0
		
	if pal == None:
		return 0
	ind = map_palette[pal]
	cache[(r,g,b)] = ind
	return ind

def CreateNewMapFileJava(path, number, colors):
	map = TAG_Compound()
	map["data"] = TAG_Compound()
	map["data"]["scale"] = TAG_Byte(4)
	map["data"]["dimension"] = TAG_Byte(0)
	map["data"]["height"] = TAG_Short(128)
	map["data"]["width"] = TAG_Short(128)
	map["data"]["xCenter"] = TAG_Int(2147483647)
	map["data"]["yCenter"] = TAG_Int(2147483647)
	map["data"]["colors"] = TAG_Byte_Array(colors)
	map.save(os.path.join(path,"map_"+str(number)+".dat"))
	
def CreateNewMapFilePE(level, number, colors):
	map = TAG_Compound()
	map["mapId"] = TAG_Long(number)
	map["parentMapId"] = TAG_Long(-1)
	map["decorations"] = TAG_List()
	map["dimension"] = TAG_Byte(0)
	map["fullyExplored"] = TAG_Byte(1)
	map["scale"] = TAG_Byte(4)
	map["height"] = TAG_Short(128)
	map["width"] = TAG_Short(128)
	map["xCenter"] = TAG_Int(2147483647)
	map["zCenter"] = TAG_Int(2147483647)
	map["colors"] = TAG_Byte_Array(colors)
	with level.worldFile.world_db() as db:
		wop = level.worldFile.writeOptions
		with nbt.littleEndianNBT():
			db.Put(wop, 'map_'+str(number), map.save(compressed=False))
	
def CreateItemFrameJava(x, y, z, dir, mapid, invuln):
	TileY = y
	posy = float(y) + 0.5
	if dir == 1: #westward
		direction = dir
		rotation = 90.0
		TileX = x
		TileZ = z
		posx = float(x) + 0.96875
		posz = float(z) + 0.5
	elif dir == 3: #eastward
		rotation = 270.0
		direction = dir
		TileX = x
		TileZ = z
		posx = float(x) + 0.03125
		posz = float(z) + 0.5
	elif dir == 0: #northward
		rotation = 180.0
		direction = 2
		TileZ = z
		TileX = x
		posz = float(z) + 0.96875
		posx = float(x) + 0.5
	elif dir == 2: #southward
		rotation = 0.0
		direction = 0
		TileZ = z
		TileX = x
		posz = float(z) + 0.03125
		posx = float(x) + 0.5
	iframe = TAG_Compound()
	iframe["id"] = TAG_String("item_frame")
	iframe["Pos"] = TAG_List()
	iframe["Pos"].append(TAG_Double(posx))
	iframe["Pos"].append(TAG_Double(posy))
	iframe["Pos"].append(TAG_Double(posz))
	iframe["Facing"] = TAG_Byte(direction)
	iframe["Invulnerable"] = TAG_Byte(invuln)
	iframe["Motion"] = TAG_List()
	iframe["Motion"].append(TAG_Double(0.0))
	iframe["Motion"].append(TAG_Double(0.0))
	iframe["Motion"].append(TAG_Double(0.0))
	iframe["TileX"] = TAG_Int(TileX)
	iframe["TileY"] = TAG_Int(TileY)
	iframe["TileZ"] = TAG_Int(TileZ)
	iframe["Rotation"] = TAG_List()
	iframe["Rotation"].append(TAG_Float(rotation))
	iframe["Rotation"].append(TAG_Float(0.0))
	iframe["Item"] = TAG_Compound()
	iframe["Item"]["id"] = TAG_String("minecraft:filled_map")
	iframe["Item"]["Damage"] = TAG_Short(mapid)
	iframe["Item"]["Count"] = TAG_Byte(1)
	return iframe
	
def CreateItemFramePE(x, y, z, mapid):
	iframe = TAG_Compound()
	iframe["id"] = TAG_String("ItemFrame")
	iframe["x"] = TAG_Int(x)
	iframe["y"] = TAG_Int(y)
	iframe["z"] = TAG_Int(z)
	iframe["Item"] = TAG_Compound()
	iframe["Item"]["id"] = TAG_Short(358)
	iframe["Item"]["Damage"] = TAG_Short(0)
	iframe["Item"]["Count"] = TAG_Byte(1)
	iframe["Item"]["tag"] = TAG_Compound()
	iframe["Item"]["tag"]["map_uuid"] = TAG_Long(mapid)
	return iframe

def perform(level, box, options):
	try:
		level.gamePlatform
	except:
		raise Exception('This filter requires level.gamePlatform. You will need a version of MCedit that has this')
	global idcount
	nearest = options["Use Nearest-Color Transparency (recommended for lossy image formats):"]
	tmode = options["Transparency Mode:"]
	tcolor = options["Transparency Color:"]
	if tmode == "Use Default Color (#FF00FF)":
		transparent = (255,0,255)
	elif tmode == "User-Specified Color Below":
		if tcolor[0] == "#":
			alphacolor = int(tcolor[1:7],16)
			transparent = (alphacolor>>16,(alphacolor>>8)&0xff,alphacolor&0xff)
		else:
			raise Exception("ERROR! The provided transparency color was formatted incorrectly! Colors must in hexadecimal format, in the form #RRGGBB")
			return
	else:
		transparent = None

	invulnerable = options["Item Frames are invulnerable:"]
	imgpath = options["Image path:"]
	facing = options["Item Frames are facing:"]
	backing = options["Item Frame backing block (replaces air blocks only):"]
	if backing.ID == 0:
		raise Exception("ERROR! The backing block CANNOT be air!")
		return
	toosmall = options["If selection is too small for image size:"]

	if level.gamePlatform == 'Java':
		if level.dimNo:
			datafolder = level.parentWorld.worldFolder.getFolderPath("data")	
		else:
			datafolder = level.worldFolder.getFolderPath("data")

		if not os.path.exists(datafolder):
			try:
				os.makedirs(datafolder)
			except:
				raise OSError("ERROR! Data folder does not exist and could not be created. Please create a \"data\" folder at: "+datafolder)
				return
		idcountpath = os.path.join(datafolder,"idcounts.dat")
		if os.path.exists(idcountpath):
			idcountfile = nbt.load(idcountpath)
			if "map" in idcountfile:
				idcount = idcountfile["map"].value
			else:
				idcount = 0
				idcountfile["map"] = TAG_Short(0)
		else:
			idcount = 0
			idcountfile = TAG_Compound()
			idcountfile["map"] = TAG_Short(0)
			
	elif level.gamePlatform == 'PE':
		try:
			with level.worldFile.world_db() as db:
				rop = level.worldFile.readOptions
				idcountfile = loadNBTCompoundList(db.Get(rop, 'MCeditMapIt'))[0]
			if "map" in idcountfile:
				idcount = idcountfile["map"].value
			else:
				idcount = 0
				idcountfile["map"] = TAG_Long(0)
		except:
			idcount = 0
			idcountfile = TAG_Compound()
			idcountfile["map"] = TAG_Long(0)

	if imgpath != "None":
		if os.path.exists(imgpath):
			image_path = imgpath
		else:
			image_path = mcplatform.askOpenFile(title="Select an Image", schematics=False)
	else:
		image_path = mcplatform.askOpenFile(title="Select an Image", schematics=False)

	if image_path == None:
		raise Exception("ERROR: No file provided!")
		return
	surface = pygame.image.load(image_path)

	# Adrian Brightmoore
	# Modification to allow auto-resize to selection dimensions
	sx, sy, sz = box.size
	xsize, ysize, zsize = box.size * 128

	if toosmall == "Scale to selection":
		if (facing == "Eastwards (-X to +X)" or facing == "Westwards (+X to -X)"):
			surface = pygame.transform.smoothscale(surface,(zsize,ysize))
		elif (facing == "Northwards (+Z to -Z)" or facing == "Southwards (-Z to +Z)"):
			surface = pygame.transform.smoothscale(surface,(xsize,ysize))
	(height, width) = surface.get_size()

	# End modification to allow auto-resize to selection dimensions

	loopx = int(math.ceil(float(width)/128.0))
	loopy = int(math.ceil(float(height)/128.0))
	
	if level.gamePlatform == 'Java':
		if (loopx*loopy)+idcount > 32767:
			raise Exception("\nERROR! The image size is too large or there are not enough maps left for this world.\n"
			"Only 32,767 map files are allowed per world, and there are",idcount,"maps in this world.\n"
			"The image specified requires",(loopx*loopy),"maps.\n")
			return
	# elif level.gamePlatform == 'PE':
		# could do similar code to above but the limit is 2^63 rather than 2^15 so it will never be reached ever
		

	chestorframe = "item frames"
	if ysize < width:
		if toosmall == "Cancel Image Processing":
			raise Exception("\nERROR! The selection height is too small! Your selection should be at least "+str(loopx)+"H in size.\n"
			 "\n"
			 "Cancelled image processing.")
			
		else:
			print "Creating chests instead of Item Frames" 
			chestorframe = "chests"
	if chestorframe == "item frames" and (facing == "Eastwards (-X to +X)" or facing == "Westwards (+X to -X)"):
		if zsize < height or sx < 2:
			if toosmall == "Cancel Image Processing":
				raise Exception("\nERROR! The selection size is too small; it selection should be at least\n"
				 "2W x "+str(loopy)+"L x "+str(loopx)+"H in size.\n"
				 "\n"
				 "Cancelled image processing.")
				
			else:
				print "Creating chests instead of Item Frames" 
				chestorframe = "chests"
	elif chestorframe == "item frames" and (facing == "Northwards (+Z to -Z)" or facing == "Southwards (-Z to +Z)"):
		if xsize < height or sz < 2:
			if toosmall == "Cancel Image Processing":
				raise Exception("\nERROR! The selection size is too small; it should be at least\n"
				 ""+str(loopy)+"W x 2L x "+str(loopx)+"H in size.\n"
				 "\n"
				 "Cancelled image processing.")
			else:
				print "Creating chests instead of Item Frames" 
				chestorframe = "chests"
				
	image = numpy.fromstring(pygame.image.tostring(surface, "RGB"),dtype=numpy.uint8).reshape(width,height,3)
	progresscount = 1
	progressmax = loopx * loopy
	startid = idcount + 1
	
	def processImageJava(image, loopx, loopy, width, height, cache, transparent, nearest, image_path, progresscount, progressmax):
		global idcount
		for lx in xrange(loopx):
			for ly in xrange(loopy):
				yield idcount-1, progressmax, "of image "+image_path
				progresscount += 1
				idcount += 1
				converted = numpy.zeros((128,128),dtype=numpy.uint8)
				offsetx = lx * 128
				offsety = ly * 128
				for x in xrange(128):
					for y in xrange(128):
						if (offsetx+x) >= width:
							break
						elif(offsety+y) >= height:
							break
						r,g,b = (image[offsetx+x,offsety+y,0],image[offsetx+x,offsety+y,1],image[offsetx+x,offsety+y,2])
						if (r,g,b) in cache:
							converted[x,y] = cache[(r,g,b)]
						else:
							converted[x,y] = FindClosestPaletteIndex(r,g,b,transparent,nearest)
					if(offsetx+x) >= width:
						break
				CreateNewMapFileJava(datafolder, idcount, converted)
				
	def processImagePE(image, loopx, loopy, width, height, image_path, progresscount, progressmax):
		global idcount
		for lx in xrange(loopx):
			for ly in xrange(loopy):
				yield idcount-1, progressmax, "of image "+image_path
				progresscount += 1
				idcount += 1
				print idcount
				converted = numpy.zeros((65536),dtype=numpy.uint8)
				offsetx = lx * 128
				offsety = ly * 128
				for x in xrange(128):
					for y in xrange(128):
						if (offsetx+x) >= width:
							break
						elif(offsety+y) >= height:
							break
						r,g,b = (image[offsetx+x,offsety+y,0],image[offsetx+x,offsety+y,1],image[offsetx+x,offsety+y,2])
						converted[4*(x*128+y)] = r
						converted[4*(x*128+y)+1] = g
						converted[4*(x*128+y)+2] = b
						converted[4*(x*128+y)+3] = 255
					if(offsetx+x) >= width:
						break
				CreateNewMapFilePE(level, idcount, converted)

	if level.gamePlatform == 'Java':
		level.showProgress("Processing image pieces:", processImageJava(image, loopx, loopy, width, height, cache, transparent, nearest, image_path, progresscount, progressmax))
	elif level.gamePlatform == 'PE':
		level.showProgress("Processing image pieces:", processImagePE(image, loopx, loopy, width, height, image_path, progresscount, progressmax))
	print idcount
	endid = idcount
	print endid
	if level.gamePlatform == 'Java':
		idcountfile["map"] = TAG_Short(idcount)
		idcountfile.save(idcountpath, compressed=False)
	elif level.gamePlatform == 'PE':
		idcountfile["map"] = TAG_Long(idcount)
		with level.worldFile.world_db() as db:
			wop = level.worldFile.writeOptions
			with nbt.littleEndianNBT():
				db.Put(wop, 'MCeditMapIt', idcountfile.save(compressed=False))
	print "Finished processing image "+image_path+". Creating "+chestorframe+"..."

	if chestorframe == "item frames":
		if level.gamePlatform == 'Java':
			if facing == "Northwards (+Z to -Z)" or facing == "Southwards (-Z to +Z)":
				if facing == "Northwards (+Z to -Z)":
					dir = 0
					posIncrement = False
				else:
					dir = 2
					posIncrement = True
			else:
				if facing == "Eastwards (-X to +X)":
					dir = 3
					posIncrement = True
				else:
					dir = 1
					posIncrement = False
			if facing == "Northwards (+Z to -Z)" or facing == "Southwards (-Z to +Z)":
				z = box.minz
				if posIncrement:
					z += 1
				for y in xrange(box.miny-1+loopx,box.miny-1,-1):
					for x in xrange(box.minx,box.minx+loopy) if posIncrement else xrange(box.minx-1+loopy, box.minx-1, -1):
						level.setBlockAt(x, y, z, 0)
						level.setBlockDataAt(x, y, z, 0)
						if level.blockAt(x, y, z+(-1 if posIncrement else 1)) == 0:
							level.setBlockAt(x, y, z+(-1 if posIncrement else 1), backing.ID)
							level.setBlockDataAt(x, y, z+(-1 if posIncrement else 1), backing.blockData)
						chunk = level.getChunk(x>>4,z>>4)
						chunk.Entities.append(CreateItemFrameJava(x, y, z, dir, startid, invulnerable))
						chunk.dirty = True
						startid += 1
			elif facing == "Eastwards (-X to +X)" or facing == "Westwards (+X to -X)":
				x = box.minx
				if posIncrement:
					x += 1
				for y in xrange(box.miny-1+loopx,box.miny-1,-1):
					for z in xrange(box.minz,box.minz+loopy) if not posIncrement else xrange(box.minz-1+loopy, box.minz-1, -1):
						level.setBlockAt(x, y, z, 0)
						level.setBlockDataAt(x, y, z, 0)
						if level.blockAt(x+(-1 if posIncrement else 1), y, z) == 0:
							level.setBlockAt(x+(-1 if posIncrement else 1), y, z, backing.ID)
							level.setBlockDataAt(x+(-1 if posIncrement else 1), y, z, backing.blockData)
						chunk = level.getChunk(x>>4,z>>4)
						chunk.Entities.append(CreateItemFrameJava(x, y, z, dir, startid, invulnerable))
						chunk.dirty = True
						startid += 1
						
		elif level.gamePlatform == 'PE':
			if facing == "Northwards (+Z to -Z)" or facing == "Southwards (-Z to +Z)":
				if facing == "Northwards (+Z to -Z)":
					dir = 3
					posIncrement = False
				else:
					dir = 2
					posIncrement = True
			else:
				if facing == "Eastwards (-X to +X)":
					dir = 0
					posIncrement = True
				else:
					dir = 1
					posIncrement = False
			if facing == "Northwards (+Z to -Z)" or facing == "Southwards (-Z to +Z)":
				z = box.minz
				if posIncrement:
					z += 1
				for y in xrange(box.miny-1+loopx,box.miny-1,-1):
					for x in xrange(box.minx,box.minx+loopy) if posIncrement else xrange(box.minx-1+loopy, box.minx-1, -1):
						level.setBlockAt(x, y, z, 199)
						level.setBlockDataAt(x, y, z, dir)
						if level.blockAt(x, y, z+(-1 if posIncrement else 1)) == 0:
							level.setBlockAt(x, y, z+(-1 if posIncrement else 1), backing.ID)
							level.setBlockDataAt(x, y, z+(-1 if posIncrement else 1), backing.blockData)
						chunk = level.getChunk(x>>4,z>>4)
						chunk.TileEntities.append(CreateItemFramePE(x, y, z, startid))
						chunk.dirty = True
						startid += 1
			elif facing == "Eastwards (-X to +X)" or facing == "Westwards (+X to -X)":
				x = box.minx
				if posIncrement:
					x += 1
				for y in xrange(box.miny-1+loopx,box.miny-1,-1):
					for z in xrange(box.minz,box.minz+loopy) if not posIncrement else xrange(box.minz-1+loopy, box.minz-1, -1):
						level.setBlockAt(x, y, z, 199)
						level.setBlockDataAt(x, y, z, dir)
						if level.blockAt(x+(-1 if posIncrement else 1), y, z) == 0:
							level.setBlockAt(x+(-1 if posIncrement else 1), y, z, backing.ID)
							level.setBlockDataAt(x+(-1 if posIncrement else 1), y, z, backing.blockData)
						chunk = level.getChunk(x>>4,z>>4)
						chunk.TileEntities.append(CreateItemFramePE(x, y, z, startid))
						chunk.dirty = True
						startid += 1

	else:
		if level.gamePlatform == 'Java':
			breakout = False
			entsToAdd = []
			for y in xrange(box.miny,box.maxy):
				for z in xrange(box.minz,box.maxz):
					for x in xrange(box.minx,box.maxx):
						newchest = TAG_Compound()
						newchest["id"] = TAG_String("Chest")
						newchest["x"] = TAG_Int(x)
						newchest["y"] = TAG_Int(y)
						newchest["z"] = TAG_Int(z)
						newchest["Lock"] = TAG_String()
						newchest["Items"] = TAG_List()
						mapitem = TAG_Compound()
						mapitem["id"] = TAG_String("minecraft:filled_map")
						mapitem["Count"] = TAG_Byte(1)
						mapitem["Damage"] = TAG_Short(0)
						mapitem["Slot"] = TAG_Byte(0)
						for c in xrange(27):
							newitem = deepcopy(mapitem)
							newitem["Slot"] = TAG_Byte(c)
							newitem["Damage"] = TAG_Short(startid)
							newchest["Items"].append(newitem)
							startid += 1
							if startid > endid:
								breakout = True
								break
						level.setBlockAt(x, y, z, 54)
						level.setBlockDataAt(x, y, z, 4)
						entsToAdd.append((level.getChunk(x>>4, z>>4),deepcopy(newchest)))
						if breakout:
							break
					if breakout:
						break
				if breakout:
					break
		elif level.gamePlatform == 'PE':
			breakout = False
			entsToAdd = []
			for y in xrange(box.miny,box.maxy):
				for z in xrange(box.minz,box.maxz):
					for x in xrange(box.minx,box.maxx):
						newchest = TAG_Compound()
						newchest["id"] = TAG_String("Chest")
						newchest["x"] = TAG_Int(x)
						newchest["y"] = TAG_Int(y)
						newchest["z"] = TAG_Int(z)
						newchest["Items"] = TAG_List()
						mapitem = TAG_Compound()
						mapitem["id"] = TAG_Short(358)
						mapitem["Count"] = TAG_Byte(16)
						mapitem["Damage"] = TAG_Short(0)
						mapitem["tag"] = TAG_Compound()
						for c in xrange(27):
							newitem = deepcopy(mapitem)
							newitem["Slot"] = TAG_Byte(c)
							newitem["tag"]["map_uuid"] = TAG_Long(startid)
							newchest["Items"].append(newitem)
							startid += 1
							if startid > endid:
								breakout = True
								break
						level.setBlockAt(x, y, z, 54)
						level.setBlockDataAt(x, y, z, 4)
						entsToAdd.append((level.getChunk(x>>4, z>>4),deepcopy(newchest)))
						if breakout:
							break
					if breakout:
						break
				if breakout:
					break

		for (chunk, entity) in entsToAdd:
			chunk.TileEntities.append(entity)
			chunk.dirty = True
	print "-------------------"
	print "Filtering complete."