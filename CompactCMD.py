from pymclevel import TAG_Compound			# Import all the necessary shenanigans from pymclevel
from pymclevel import TAG_Int
from pymclevel import TAG_Short
from pymclevel import TAG_Byte
from pymclevel import TAG_String
from pymclevel import TAG_Float
from pymclevel import TAG_Double
from pymclevel import TAG_List
from pymclevel import TileEntity

from copy import deepcopy					# Import deepcopy (will explain later)

displayName = "Compact Command Blocks"		# Name the filter

inputs = (									# User specified options
	("Process", ("Scan", "Place")),			# The method that will be used later
	("XGap", (0,100)),
	("YGap", (0,100)),						# These are the gaps between blocks in each direction
	("ZGap", (0,100)),
)

def perform(level, box, options):			# defining perform for MCedit to call
	xgap = options["XGap"]
	ygap = options["YGap"]					# Letting the gap options have easy to access names
	zgap = options["ZGap"]

	global CMD								# Make a global variable so that the value of CMD won't be forgotten while a new area is being selected
	
	if options["Process"] == "Scan":		# If the Process option is equal to "Scan" then look through the selection box and grab all the command
											# tile entities for use later
		CMD=[]															# Make a tuple called CMD
		for (chunk, slices, point) in level.getChunkSlices(box):		# Go through all the blocks in the selection box
			for t in chunk.TileEntities:			# Go through all the tile entities in the chunk
				if t["id"].value == "Control":		# If the id is Control continue with the script otherwise it will be ignored
					x = t["x"].value
					y = t["y"].value				# Find the x, y and z values for the tile entity
					z = t["z"].value
					if (x,y,z) in box:				# Check that the tile entity is in the selection box
						CMD.append(t)				# Add the tile entity to CMD
		raise NotImplementedError("Command Blocks Scanned")		# Raise an error so that MCedit does not have to change anything
	
	if options["Process"] == "Place":		# If the Process option is equal to "Place", place the command blocks in the selection area
		x = box.minx
		y = box.miny						# Let x, y and z equal the value of the minimum box coordinate
		z = box.minz
		for t in CMD[:]:					# Go through every tile entity in CMD. The [:] is there otherwise it would
											# miss half the values due to the remove line further down (line 66)

			if x >= box.maxx:				# If the x coordinate is greater than the max x box value
				x = box.minx				# Reset the value of x to the minimum box x value
				z = z + 1 + zgap			# Increase the value of z by one and the user specified zgap

			if z >= box.maxz:				# If the z coordinate is greater than the max z box value
				z = box.minz				# Reset the value of z to the minimum box z value
				y = y + 1 + ygap			# Increase the value of y by one and the user specified ygap

			if y >= box.maxy:				# If y is greater than the box y max give an error because the box is full
				raise NotImplementedError("Box not large enough. The box is filled but more are left out. Save to see changes. Run again to do the rest")

			control = deepcopy(t)					# Duplicate (using deepcopy) the t value so that you do not edit the original
			level.setBlockAt(x, y, z, 137)			# Set the block to a command block
			level.setBlockDataAt(x, y, z, 0)		# Set the data to zero
			control["x"] = TAG_Int(x)
			control["y"] = TAG_Int(y)				# Set the x, y and z value to the new location
			control["z"] = TAG_Int(z)
			
			chunk = level.getChunk(x/16, z/16)		# Find the chunk value
			chunk.TileEntities.append(control)		# Add the command block to the chunk
			
			CMD.remove(t)							# Remove the tile entity from CMD so that CMD only contains tile entities that have not been done
			
			x = x + 1 + xgap						# Increase the x value by one and the user defined xgap
			chunk.dirty = True						# Tell MCedit that the chunk has been updated
				