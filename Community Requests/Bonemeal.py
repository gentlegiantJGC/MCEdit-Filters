#This filter will turn the selected crops into fully grown versions
#This would not be possible without SethBling who I based the filter on
#http://youtube.com/SethBling
#Don't run this filter on large selection boxes otherwise it will take a long time

displayName = "Bonemeal"

inputs = (
	("Wheat", True),
	("Potato", True),
	("Carrot", True),
	("Cocoa Beans", True),
	("Nether Wart", True),
	("Sugar Cane", True),
)

def perform(level, box, options):
	block = 0
	data = 0

	for x in xrange(box.minx, box.maxx):
		print "x=" +str(x - box.minx)+ "/" +str(box.maxx - box.minx)+ " "
		for y in xrange(box.miny, box.maxy):
			for z in xrange(box.minz, box.maxz):
				block = level.blockAt(x, y, z)
				if options["Wheat"] == True and block == 59:
					level.setBlockDataAt(x, y, z, 7)
					continue
				if options["Potato"] == True and block == 142:
					level.setBlockDataAt(x, y, z, 7)
					continue
				if options["Carrot"] == True and block == 141:
					level.setBlockDataAt(x, y, z, 7)
					continue
				if options["Cocoa Beans"] == True and block == 127:
					if level.blockDataAt(x, y, z) == 0 or level.blockDataAt(x, y, z) == 4 or level.blockDataAt(x, y, z) == 8:
						level.setBlockDataAt(x, y, z, 8)
						continue
					if level.blockDataAt(x, y, z) == 1 or level.blockDataAt(x, y, z) == 5 or level.blockDataAt(x, y, z) == 9:
						level.setBlockDataAt(x, y, z, 9)
						continue
					if level.blockDataAt(x, y, z) == 2 or level.blockDataAt(x, y, z) == 6 or level.blockDataAt(x, y, z) == 10:
						level.setBlockDataAt(x, y, z, 10)
						continue
					if level.blockDataAt(x, y, z) == 3 or level.blockDataAt(x, y, z) == 7 or level.blockDataAt(x, y, z) == 11:
						level.setBlockDataAt(x, y, z, 11)
						continue
				if options["Nether Wart"] == True and block == 115:
					level.setBlockDataAt(x, y, z, 8)
					continue
				if options["Sugar Cane"] == True and block == 83:
					if level.blockAt(x, y - 1, z) != 83:
						if level.blockAt(x, y + 1, z) == 0:
							level.setBlockAt(x, y + 1, z, 83)
							if level.blockAt(x, y + 2, z) == 0:
								level.setBlockAt(x, y + 2, z, 83)
								continue
	level.markDirtyBox(box)