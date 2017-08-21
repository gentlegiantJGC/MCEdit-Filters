# Made by gentlegiantJGC based on the demo filter that MCedit comes with
# https://www.youtube.com/gentlegiantJGC

# perform() is the main entry point of a filter. Its parameters are
# an MCLevel instance, a BoundingBox, and an options dictionary.
# The options dictionary will have keys corresponding to the keys specified,
# and values reflecting the user's input.

# you get undo for free: everything within 'box' is copied to a temporary buffer
# before perform is called, and then copied back when the user asks to undo

def perform(level, box, options):
    value = options["inputname"] # options["inputname"] takes the value that the user selected in the UI
	#the rest of the script goes here
	
	
	
	
    # There are a few general ways of accessing a level's blocks
    # The first is using level.blockAt and level.setBlockAt
    # These are slower than the other two methods, but easier to start using
    for x in xrange(box.minx, box.maxx):
        for z in xrange(box.minz, box.maxz):
            for y in xrange(box.miny, box.maxy):  # nested loops can be slow
				# the code that goes here will be repeated for every value of x, y and z in the selection area

	# the three lines above are equal to the line below but the line below is more efficient than the above three
	for x, y, z in box.positions:
	
	# the below lines would need to be nested in one of the above two so that x, y and z are defined
	if level.blockAt(x, y, z) == 14: # will check if the block id that is at (x, y, z) is equal to 14. If true it will run the lines below
		level.setBlockAt(x, y, z, 46) # This will set the block at (x, y, z) to 46
	
	level.blockDataAt(x, y, z) # takes the value of the block data at (x, y, z)
	level.setBlockDataAt(x, y, z, 0) # Will set the block data at (x, y, z) to 0
				
				
				
				
    # The second is to extract the segment of interest into a contiguous array
    # using level.extractSchematic. this simplifies using numpy but at the cost
    # of the temporary buffer and the risk of a memory error on 32-bit systems.

    temp = level.extractSchematic(box)

    # remove any entities in the temp.  this is an ugly move
    # because copyBlocksFrom actually copies blocks, entities and tile entities
    temp.removeEntitiesInBox(temp.bounds)
    temp.removeTileEntitiesInBox(temp.bounds)

    # replaces gold with TNT.
    # the expression in [] creates a temporary the same size, using more memory
    temp.Blocks[temp.Blocks == 14] = 46

    level.copyBlocksFrom(temp, temp.bounds, box.origin)
		
		
		
		
    # The third method iterates over each subslice of every chunk in the area
    # using level.getChunkSlices. this method is a bit arcane, but lets you
    # visit the affected area chunk by chunk without using too much memory.

    for (chunk, slices, point) in level.getChunkSlices(box):
        # chunk is an AnvilChunk object with attributes:
        # Blocks, Data, Entities, and TileEntities
        blocks = chunk.Blocks[slices] # Blocks and Data can be indexed using slices

        # blocks now contains a "view" on the part of the chunk's blocks
        # that lie in the selection. This "view" is a numpy object that
        # accesses only a subsection of the original array, without copying

        # once again, gold into TNT
        blocks[blocks == 14] = 46

        # notify the world that the chunk changed
        # this gives finer control over which chunks are dirtied
        # you can call chunk.chunkChanged(False) if you want to dirty it
        # but not run the lighting calculation later.

        chunk.chunkChanged()

    # You can also access the level any way you want
    # Beware though, you only get to undo the area within the specified box