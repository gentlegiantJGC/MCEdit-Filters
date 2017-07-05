# Made by gentlegiantJGC
# https://www.youtube.com/gentlegiantJGC

# Select a region with coloured wool and it will make command blocks with commands in them to spawn firework entities at the location
# where the wool was with the colour of the wool block
# On the second tab there is the option for the user to change the colour codes if desired

from pymclevel import TAG_Compound
from pymclevel import TAG_Int
from pymclevel import TAG_Short
from pymclevel import TAG_Byte
from pymclevel import TAG_String
from pymclevel import TAG_Float
from pymclevel import TAG_Double
from pymclevel import TAG_List
from pymclevel import TileEntity

displayName = "Firework Shapes"

inputs = [
	(("Main", "title"),
	("Game Version", ("1.11", "1.10 and lower")),
	("Mode", ("Absolute", "Relative")),
	("Create fireworks", True),
	("Create barrier blocks", True),
	("Explosion Type", ("Small","Large")),
	("Optional Relative Prefix", ("string", "value=")),),
	
	(("Colours 1", "title"),
	("Leave these as they are if you", "label"),
	("don't know what you are doing", "label"),
	("White Wool",-1),
	("Orange Wool",-23296),
	("Magenta Wool",-65281),
	("Light Blue Wool",-16715777),
	("Yellow Wool",-256),
	("Lime Wool",-16711936),),
	
	(("Colours 2", "title"),
	("Pink Wool",-65408),
	("Grey Wool",-8355712),
	("Light Grey Wool",-2894893),
	("Cyan Wool",-16711681),
	("Purple Wool",-8388480),
	("Blue Wool",-16776961),
	("Brown Wool",-5952982),
	("Green Wool",-16744448),
	("Red Wool",-65536),
	("Black Wool",-16777216),),
	]

def perform(level, box, options):
	for x in xrange(box.minx, box.maxx):
		print str(100 * (x - box.minx)/(box.maxx - box.minx))+"%"
		for y in xrange(box.miny, box.maxy):
			for z in xrange(box.minz, box.maxz):
				if level.blockAt(x, y, z) == 35:
					if options["Create fireworks"] == True:
						if level.blockDataAt(x, y, z) == 0:
							cmdblock(level, box, options, x, y, z, options["White Wool"])
						if level.blockDataAt(x, y, z) == 1:
							cmdblock(level, box, options, x, y, z, options["Orange Wool"])
						if level.blockDataAt(x, y, z) == 2:
							cmdblock(level, box, options, x, y, z, options["Magenta Wool"])
						if level.blockDataAt(x, y, z) == 3:
							cmdblock(level, box, options, x, y, z, options["Light Blue Wool"])
						if level.blockDataAt(x, y, z) == 4:
							cmdblock(level, box, options, x, y, z, options["Yellow Wool"])
						if level.blockDataAt(x, y, z) == 5:
							cmdblock(level, box, options, x, y, z, options["Lime Wool"])
						if level.blockDataAt(x, y, z) == 6:
							cmdblock(level, box, options, x, y, z, options["Pink Wool"])
						if level.blockDataAt(x, y, z) == 7:
							cmdblock(level, box, options, x, y, z, options["Grey Wool"])
						if level.blockDataAt(x, y, z) == 8:
							cmdblock(level, box, options, x, y, z, options["Light Grey Wool"])
						if level.blockDataAt(x, y, z) == 9:
							cmdblock(level, box, options, x, y, z, options["Cyan Wool"])
						if level.blockDataAt(x, y, z) == 10:
							cmdblock(level, box, options, x, y, z, options["Purple Wool"])
						if level.blockDataAt(x, y, z) == 11:
							cmdblock(level, box, options, x, y, z, options["Blue Wool"])
						if level.blockDataAt(x, y, z) == 12:
							cmdblock(level, box, options, x, y, z, options["Brown Wool"])
						if level.blockDataAt(x, y, z) == 13:
							cmdblock(level, box, options, x, y, z, options["Green Wool"])
						if level.blockDataAt(x, y, z) == 14:
							cmdblock(level, box, options, x, y, z, options["Red Wool"])
						if level.blockDataAt(x, y, z) == 15:
							cmdblock(level, box, options, x, y, z, options["Black Wool"])
				
				if level.blockAt(x, y, z) == 1 or level.blockAt(x, y, z) == 137:
					if options["Create barrier blocks"] == True:
						if level.blockAt(x-1, y, z) == 0:
							level.setBlockAt(x-1, y, z, 166)
							level.setBlockDataAt(x-1, y, z, 0)
							
						if level.blockAt(x+1, y, z) == 0:
							level.setBlockAt(x+1, y, z, 166)
							level.setBlockDataAt(x+1, y, z, 0)
							
						if level.blockAt(x, y-1, z) == 0:
							level.setBlockAt(x, y-1, z, 166)
							level.setBlockDataAt(x, y-1, z, 0)
							
						if level.blockAt(x, y+1, z) == 0:
							level.setBlockAt(x, y+1, z, 166)
							level.setBlockDataAt(x, y+1, z, 0)
							
						if level.blockAt(x, y, z-1) == 0:
							level.setBlockAt(x, y, z-1, 166)
							level.setBlockDataAt(x, y, z-1, 0)
							
						if level.blockAt(x, y, z+1) == 0:
							level.setBlockAt(x, y, z+1, 166)
							level.setBlockDataAt(x, y, z+1, 0)

							
	level.markDirtyBox(box)

def cmdblock(level, box, options, x, y, z, colour, ):
	explosiontype = options["Explosion Type"]
	level.setBlockAt(x, y, z, 137)
	level.setBlockDataAt(x, y, z, 0)
	cmd = TAG_Compound()
	cmd["x"] = TAG_Int(x)
	cmd["y"] = TAG_Int(y)
	cmd["z"] = TAG_Int(z)
	if options["Game Version"] == "1.11":
		cmd["id"] = TAG_String("command_block")
		entityname = "fireworks_rocket"
	else:
		cmd["id"] = TAG_String("Control")
		entityname = "FireworksRocketEntity"
	if options["Mode"] == "Absolute":
		cmd["Command"] = TAG_String("summon "+entityname+" "+str(x)+" "+str(y)+" "+str(z)+" {LifeTime:0,FireworksItem:{id:fireworks,Count:1,tag:{Fireworks:{Explosions:[{Type:"+{True: "0", False: "1"}[explosiontype=="Small"]+",Flicker:0,Trail:0,Colors:["+str(colour)+"],FadeColors:["+str(colour)+"]}]}}}}")
	elif options["Mode"] == "Relative":
		cmd["Command"] = TAG_String(options["Optional Relative Prefix"]+"summon "+entityname+" ~"+str(x - box.minx)+" ~"+str(y - box.miny)+" ~"+str(z - box.minz)+" {LifeTime:0,FireworksItem:{id:fireworks,Count:1,tag:{Fireworks:{Explosions:[{Type:"+{True: "0", False: "1"}[explosiontype=="Small"]+",Flicker:0,Trail:0,Colors:["+str(colour)+"],FadeColors:["+str(colour)+"]}]}}}}")
	chunk = level.getChunk(x/16, z/16)
	chunk.TileEntities.append(cmd)
	chunk.dirty = True
	chunk.dirty = True