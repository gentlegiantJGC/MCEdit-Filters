# Made by gentlegiantJGC
# https://www.youtube.com/gentlegiantJGC

# You need to import the TAG types so that MCedit can understand them
# This needs to go before the inputs section

from pymclevel import TAG_Compound, TAG_Int, TAG_Short, TAG_Byte, TAG_String, TAG_Float, TAG_Double, TAG_List, TileEntity

def perform(level, box, options):
	for (chunk, slices, point) in level.getChunkSlices(box):	# This is the slice method of accessing the world (See part 2)
		for t in chunk.TileEntities:	# This will iterate for every tile entity in the chunk
			x = t["x"].value		# t["x"].value will call the x tag from t and let x equal that value
			y = t["y"].value		# Same as above but will call the y tag
			z = t["z"].value
			if (x,y,z) in box:		# This will check if the tile entity is in the box because the tile entity might be in the
									# same chunk but it might not be in the specified box
		
				del t["TAG"]		# This will delete the tag called TAG in t
				t["z"] = TAG_Int(z)	# If the tag exists this will overwrite the existing z value with the new value. If not it will create it.
				t["SpawnData"]["Pos"][0] = TAG_Int(x)	# This is just an example but tags can be sub tags of other tags. An example is
														# spawn data in spawners. This is how to edit sub tags. (t["SpawnData"]["Pos"] would need to exist)
	
				chunk.dirty = True						# Tell MCedit that the chunk has been updated