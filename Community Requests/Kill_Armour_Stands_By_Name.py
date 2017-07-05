#made by gentlegiantJGC for The8BitMonkey

import albow

displayName = "Kill Armour Stands 2"

def perform(level, box, options):
	destroy = []
	keep = []
	for (chunk, slices, point) in level.getChunkSlices(box):
		entities = []
		for e in chunk.Entities:
			x = e["Pos"][0].value
			y = e["Pos"][1].value
			z = e["Pos"][2].value
			if (x, y, z) in box:
				if e["id"].value == "ArmorStand":
					try:
						if e["CustomName"].value not in destroy and e["CustomName"].value not in keep:
							answer = albow.ask(
								e["CustomName"].value,
								[
									'Destroy',
									'Keep'
								],
								default=0,
								cancel=1
							)
							if answer == 'Destroy':
								destroy.append(e["CustomName"].value)
							elif answer == 'Keep':
								keep.append(e["CustomName"].value)
						if e["CustomName"].value in destroy:
							continue
						elif e["CustomName"].value in keep:
							entities.append(e)
					except:
						entities.append(e)
				else:
					entities.append(e)
			else:
				entities.append(e)
		chunk.Entities.value[:] = entities
		chunk.dirty = True