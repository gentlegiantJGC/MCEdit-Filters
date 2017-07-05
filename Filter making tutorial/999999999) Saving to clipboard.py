# Before I start I should probably say that I have no idea why this works but that it does
# All the credit for this one goes to Texelelf since he was the one who discovered it
# Made by gentlegiantJGC
# https://www.youtube.com/gentlegiantJGC


from pymclevel import MCSchematic	# Both of these things need to be imported for it to work. To answer the question you probably have ... no idea
import inspect

def perform(level, box, options):
	
	schematic = MCSchematic((width, height, length), mats=level.materials)	# Create a schematic of width, height and length.
	# One thing to note is that the schematic is based around 0, 0, 0 so the next two should take this into account

	schematic.setBlockAt(x, y, z, block)		# These are the same as usual but you are doing it with the schematic rather than the level
	schematic.setBlockDataAt(x, y, z, data)
	
	
	schematic.TileEntities.append(tileent)		# Again the same but with the schematic rather than the level
	schematic.Entities.append(ent)				# see 3) and 5) respectively
	
	editor.addCopiedSchematic(schematic)		# This adds the schematic you put together to the clipboard to be coppied back in by the user