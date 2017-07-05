# Made by gentlegiantJGC
# https://www.youtube.com/gentlegiantJGC

# You need to import the TAG types so that MCedit can understand them
# This needs to go before the inputs section

# only the TAG types used actually need importing
from pymclevel import TAG_Compound, TAG_Int, TAG_Short, TAG_Byte, TAG_String, TAG_Float, TAG_Double, TAG_List, TileEntity
import math

	cmd = TAG_Compound()				# to create a tile entity you first of all need to make a TAG_compound
	cmd["id"] = TAG_String("command_block")	# You can then specify values in the compound
	cmd["x"] = TAG_Int(x)				# The part on the left is the name of the tag in the compound
	cmd["y"] = TAG_Int(y)				# The right part is the data type and the new value
	cmd["z"] = TAG_Int(z)				# For a string or a fixed value the value needs to be in quotes
										# otherwise it will try and call the stored value with that name
										# The data type must be correct. The correct type can be found on the chunk format wiki page
										# http://minecraft.gamepedia.com/Chunk_format

	chunk = level.getChunk(math.floor(x/16.0), math.floor(z/16.0))  # Chunk is not difined yet to this difines it

	chunk.TileEntities.append(cmd)		# You then need to append the compound tag to the world
	chunk.dirty = True					# And tell MCedit that the chunk has been updated