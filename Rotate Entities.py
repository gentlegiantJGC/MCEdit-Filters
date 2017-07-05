# Made by gentlegiantJGC
# https://www.youtube.com/gentlegiantJGC

from pymclevel import TAG_List
from pymclevel import TAG_Byte
from pymclevel import TAG_Int
from pymclevel import TAG_Float
from pymclevel import TAG_Short
from pymclevel import TAG_Double
from pymclevel import TAG_String
import math
import copy

displayName = "Rotate Entities"

inputs = (
	("Angle", (0.0, -180.0, 180.0)),
)

def perform(level, box, options):
	angle = math.pi*(options["Angle"] / 180.0)
	centerx = (box.maxx + box.minx) / 2.0
	centerz = (box.maxz + box.minz) / 2.0
	for (chunk, slices, point) in level.getChunkSlices(box):
		for e in chunk.Entities:
			x = e["Pos"][0].value
			y = e["Pos"][1].value
			z = e["Pos"][2].value
			if (x,y,z) in box:
				theta = math.atan2(-(x - centerx),z - centerz)
				theta += angle
				r = ((x - centerx)**2 + (z - centerz)**2)**0.5
				zn = r*math.cos(theta)
				xn = -r*math.sin(theta)
				
				e["Pos"][0] = TAG_Double(xn+centerx)
				e["Pos"][2] = TAG_Double(zn+centerz)
				if (e["Rotation"][0].value+options["Angle"]) < -180.0:
					e["Rotation"][0] = TAG_Float(e["Rotation"][0].value+options["Angle"]+360)
				elif (e["Rotation"][0].value+options["Angle"]) > 180.0:
					e["Rotation"][0] = TAG_Float(e["Rotation"][0].value+options["Angle"]-360)
				else:
					e["Rotation"][0] = TAG_Float(e["Rotation"][0].value+options["Angle"])
				chunk = level.getChunk(int(math.floor(xn+centerx))/16, int(math.floor(zn+centerz))/16)
				chunk.dirty = True
					