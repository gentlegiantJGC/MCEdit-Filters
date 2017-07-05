# This will extrude the selection box up to a roof or build limit whichever it hits first

displayName = "Wall Extruder"

inputs = (
    ("Max Height Added", 256),
    ("This will extrude the selected region until it hits a roof", "label"),
	("If no roof is found it will continue until it hits the max height or the value specified", "label"),
)

def perform(level, box, options):
	block = 0
	data = 0
	max = options["Max Height Added"] + 1
	
	for x in xrange(box.minx, box.maxx):
		for y in xrange(box.miny, box.maxy ):
			for z in xrange(box.minz, box.maxz):
				block = level.blockAt(x, y, z)
				data = level.blockDataAt(x, y, z)
				for h in xrange(1, max):
					if level.blockAt(x, y + h , z) != 0:
						break
					level.setBlockAt(x, y + h , z, block)
					level.setBlockDataAt(x, y + h, z, data)

	
	level.markDirtyBox(box)