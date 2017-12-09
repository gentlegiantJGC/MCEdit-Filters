#Written by gentlegiantJGC
#http://youtube.com/gentlegiantJGC
#https://twitter.com/gentlegiantJGC

# if you are going to use the code in this filter please give credit

from pymclevel import TAG_Int, TAG_String, TAG_Compound
import numpy as np
import random

displayName = "Bedrock Fix"

inputs = ()
	
def perform(level, box, options):
	if level.gamePlatform != 'PE':
		raise Exception('Must be a PE/Win10... world')


	for cx, cz in box.chunkPositions:
		try:
			chunk = level.getChunk(cx, cz)
		except:
			continue
		chunkBlockList = np.unique(chunk.Blocks)
		for block in chunkBlockList:
			if block not in [52,54,116,118]:
				continue
			for coord in np.argwhere(chunk.Blocks == block):
				x,z,y = coord
				x += cx * 16
				z += cz * 16
				# get the tile entity
				te = level.tileEntityAt(x,y,z)
				if te is None:
					#create tile entitiy
					te = TAG_Compound()
					te['x'] = TAG_Int(x)
					te['y'] = TAG_Int(y)
					te['z'] = TAG_Int(z)
					if block == 52:
						te['id'] = TAG_String("MobSpawner")
						te['EntityId'] = TAG_Int(random.choice([32,33,34,35]))
						# need to randomly choose between a few
					elif block == 54:
						te['id'] = TAG_String("Chest")
						te['LootTable'] = TAG_String("loot_tables/chests/woodland_mansion.json")
					elif block == 116:
						te['id'] = TAG_String("EnchantTable")
					elif block == 118:
						te['id'] = TAG_String("Cauldron")
					chunk.TileEntities.append(te)
				else:
					if block == 52:
						te['id'] = TAG_String("MobSpawner")
						if 'EntityId' not in te or ('EntityId' in te and te['EntityId'].value == 1):
							te['EntityId'] = TAG_Int(random.choice([32,33,34,35]))
					elif block == 54:
						te['id'] = TAG_String("Chest")
						if 'Items' in te and len(te['Items']) > 0:
							pass
						elif 'LootTable' not in te:
							te['LootTable'] = TAG_String("loot_tables/chests/woodland_mansion.json")
					elif block == 116:
						te['id'] = TAG_String("EnchantTable")
					elif block == 118:
						te['id'] = TAG_String("Cauldron")
					
		chunk.chunkChanged()


# 52
# {
	# EntityId: 35,
	# id: "MobSpawner",
# }


# 54
# {
	# id: "Chest"
	# LootTable: "loot_tables/chests/woodland_mansion.json"
# }


# 116
# {
	# id: "EnchantTable",
# }


# 118
# {
	# id: "Cauldron"
# }