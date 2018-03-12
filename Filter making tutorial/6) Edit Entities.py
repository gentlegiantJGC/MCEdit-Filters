# Made by gentlegiantJGC
# https://www.youtube.com/gentlegiantJGC

# You need to import the TAG types so that MCedit can understand them
# This needs to go before the inputs section

from pymclevel import TAG_Compound, TAG_Int, TAG_Short, TAG_Byte, TAG_String, TAG_Float, TAG_Double, TAG_List, TileEntity

def perform(level, box, options):
	for (chunk, slices, point) in level.getChunkSlices(box):	# This is the slice method of accessing the world (See part 2)
		for e in chunk.Entities:		# This will iterate for every entity in the chunk
			x = e["Pos"][0].value		# e["Pos"][0].value will call the first value in the Pos tag from e and let x equal that value
			y = e["Pos"][1].value		# Same as above but will call the second value from the Pos tag
			z = e["Pos"][2].value
			if (x,y,z) in box:			# This will check if the entity is in the box because the entity might be in the
										# same chunk but it might not be in the specified box

				# Once again here are the ways to edit the tags
				del e["TAG"]					# This will delete the tag called TAG in e
				e["id"] = TAG_String("zombie")	# This will turn the entity into a zombie
				e["Pos"][1] = TAG_Double(y)		# This will change the entity's y coordinate
				chunk.dirty = True	# And tell MCedit that the chunk has been updated
