# Made by gentlegiantJGC
# https://www.youtube.com/gentlegiantJGC

# You need to import the TAG types so that MCedit can understand them
# This needs to go before the inputs section

from pymclevel import TAG_Compound, TAG_Int, TAG_Short, TAG_Byte, TAG_String, TAG_Float, TAG_Double, TAG_List, TileEntity


	# This is very similar to making Tile entities except the x, y and z values do not have integer values
	# and the format is slightly different for instance the position tags are sub tags of Pos in entities

	e = TAG_Compound()						# to create an entity you first of all need to make a TAG_compound
	e["id"] = TAG_String("zombie")		    # You can then specify values in the compound
    e["Pos"] = TAG_List()
	e["Pos"].append(TAG_Double(x)			# The part on the left is the name of the tag in the compound
	e["Pos"].append(TAG_Double(y)			# The right part is the data type and the new value
	e["Pos"].append(TAG_Double(z)			# For a string or a fixed value the value needs to be in quotes
											# otherwise it will try and call the stored value with that name
											# The data type must be correct. The correct type can be found on the chunk format wiki page
											# http://minecraft.gamepedia.com/Chunk_format

    chunk = level.getChunk(x/16, z/16)  # Chunk is not defined yet to this defines it

	chunk.Entities.append(e)		# You then need to append the compound tag to the world
	chunk.dirty = True				# And tell MCedit that the chunk has been updated