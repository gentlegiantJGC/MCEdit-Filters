# This will make faces that are selected in the selection box
# This is by request of minecraftmanUSA

displayName = "Faces"

inputs = (
	("Pick a block", 1),
	("Pick a data value", 1),
    ("Top", False),
    ("Bottom", False),
    ("North (Lower Z)", False),
    ("East (Higher X)", False),
	("South (Higher Z)", False),
	("West (Lower X)", False),
)

def perform(level, box, options):
	block = options["Pick a block"]
	data = options["Pick a data value"]
	
	if options["Top"] == True:
		for x in xrange(box.minx, box.maxx):
			for y in xrange(box.maxy - 1, box.maxy ):
				for z in xrange(box.minz, box.maxz):
					level.setBlockAt(x, y, z, block)
					level.setBlockDataAt(x, y, z, data)
	if options["Bottom"] == True:
		for x in xrange(box.minx, box.maxx):
			for y in xrange(box.miny, box.miny + 1):
				for z in xrange(box.minz, box.maxz):
					level.setBlockAt(x, y, z, block)
					level.setBlockDataAt(x, y, z, data)
	if options["North (Lower Z)"] == True:
		for x in xrange(box.minx, box.maxx):
			for y in xrange(box.miny, box.maxy):
				for z in xrange(box.minz, box.minz + 1):
					level.setBlockAt(x, y, z, block)
					level.setBlockDataAt(x, y, z, data)
	if options["East (Higher X)"] == True:
		for x in xrange(box.maxx - 1, box.maxx):
			for y in xrange(box.miny, box.maxy):
				for z in xrange(box.minz, box.maxz):
					level.setBlockAt(x, y, z, block)
					level.setBlockDataAt(x, y, z, data)
	if options["South (Higher Z)"] == True:
		for x in xrange(box.minx, box.maxx):
			for y in xrange(box.miny, box.maxy):
				for z in xrange(box.maxz - 1, box.maxz):
					level.setBlockAt(x, y, z, block)
					level.setBlockDataAt(x, y, z, data)
	if options["West (Lower X)"] == True:
		for x in xrange(box.minx, box.minx + 1):
			for y in xrange(box.miny, box.maxy):
				for z in xrange(box.minz, box.maxz):
					level.setBlockAt(x, y, z, block)
					level.setBlockDataAt(x, y, z, data)

	
	level.markDirtyBox(box)