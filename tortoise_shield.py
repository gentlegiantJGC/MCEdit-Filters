#import the shenanigans for making an entitiy
from pymclevel import nbt, TAG_Compound, TAG_List, TAG_Int_Array, TAG_Byte_Array, TAG_String, TAG_Long, TAG_Int, TAG_Short, TAG_Byte, TAG_Double, TAG_Float 
#import the maths module for maths fun
import math

displayName = "Tortoise Sheild"	#define the name of the filter

#define the inputs for the filter
inputs = (
	("Radius", 5.0),
)

def perform(level, box, options):
	sw = 0.75	#width of sheild
	sh = 1.375	#height of sheild
	radius = options["Radius"]
	noy = int(math.ceil((math.pi*radius)/(2.0*sh)))	#number of shields that can be fit in the y direction
	dy = math.pi/(float(noy)*2)	#angle between each armour stand in the y direction
	ty = 0	#current y angle which starts at 0
	for y in xrange(noy):
		y = math.sin(ty) * radius + box.miny	#y position for that row of entities
		radx = radius * math.cos(ty)	#radius for that row of entities
		nox = int(math.ceil((math.pi*2.0*radx)/sw))	#number of shields that can be fit in the x direction (around the circle)
		dx = 2*math.pi/float(nox) #angle between each armour stand in the x direction
		tx = 0	#current x angle which starts at 0 (resets to 0 for each y loop
		for x in xrange(nox):
			x = -(math.sin(tx) * radx) + (box.minx + box.maxx)/2.0 	#x position for that entity
			z = math.cos(tx) * radx + (box.minz + box.maxz)/2.0		#z position for that entity
			shield(level, x, y, z, math.degrees(tx), math.degrees(ty))	#call the function below passing it those variables
			
			tx += dx	#increase the current x angle by one increment
		
		ty += dy	#increase the current y angle by one increment
	level.markDirtyBox(box)	#mark the box a dirty for good measure
	
def shield(level, x, y, z, tx, ty):	#define function
	e = TAG_Compound()	#make the entity
	
	#the rest is defining all the data that is required by the entity
	
	e["id"] = TAG_String("ArmorStand")
	
	e["Invisible"] = TAG_Byte(1)
	
	e["NoGravity"] = TAG_Byte(1)
	
	e["HandItems"] = TAG_List()
	e["HandItems"].append(TAG_Compound())
	e["HandItems"][0]["Count"] = TAG_Byte(1)
	e["HandItems"][0]["Damage"] = TAG_Short(0)
	e["HandItems"][0]["id"] = TAG_String("minecraft:stone_sword")
	e["HandItems"].append(TAG_Compound())
	e["HandItems"][1]["Count"] = TAG_Byte(1)
	e["HandItems"][1]["Damage"] = TAG_Short(0)
	e["HandItems"][1]["id"] = TAG_String("minecraft:shield")
	e["HandItems"][1]["tag"] = TAG_Compound()
	e["HandItems"][1]["tag"]["BlockEntityTag"] = TAG_Compound()
	e["HandItems"][1]["tag"]["BlockEntityTag"]["Base"] = TAG_Int(1)
	e["HandItems"][1]["tag"]["BlockEntityTag"]["Patterns"] = TAG_List()
	e["HandItems"][1]["tag"]["BlockEntityTag"]["Patterns"].append(TAG_Compound())
	e["HandItems"][1]["tag"]["BlockEntityTag"]["Patterns"][0]["Color"] = TAG_Int(11)
	e["HandItems"][1]["tag"]["BlockEntityTag"]["Patterns"][0]["Pattern"] = TAG_String("cr")
	e["HandItems"][1]["tag"]["BlockEntityTag"]["Patterns"].append(TAG_Compound())
	e["HandItems"][1]["tag"]["BlockEntityTag"]["Patterns"][1]["Color"] = TAG_Int(8)
	e["HandItems"][1]["tag"]["BlockEntityTag"]["Patterns"][1]["Pattern"] = TAG_String("mc")
	
	e["Pos"] = TAG_List()
	e["Pos"].append(TAG_Double(x))
	e["Pos"].append(TAG_Double(y-0.7))
	e["Pos"].append(TAG_Double(z))
	
	e["Pose"] = TAG_Compound()
	e["Pose"]["LeftArm"] = TAG_List()
	e["Pose"]["LeftArm"].append(TAG_Float(0.0))
	e["Pose"]["LeftArm"].append(TAG_Float(ty+90.0))
	e["Pose"]["LeftArm"].append(TAG_Float(90.0))
	e["Pose"]["RightArm"] = TAG_List()
	e["Pose"]["RightArm"].append(TAG_Float((-ty/2.5)-40.0))
	e["Pose"]["RightArm"].append(TAG_Float(ty/4))
	e["Pose"]["RightArm"].append(TAG_Float(15.0))
	
	e["Rotation"] = TAG_List()
	e["Rotation"].append(TAG_Float(tx))
	e["Rotation"].append(TAG_Float(0.0))
	
	chunk = level.getChunk(int(math.floor(x))/16, int(math.floor(z))/16)	#get the chunk that the entitiy is located at
	chunk.Entities.append(e)	#mark the entity to that chunk
	chunk.dirty = True	#tell mcedit that that chunk has been modified and needs to be saved