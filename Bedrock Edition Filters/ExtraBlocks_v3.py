# @gentlegiantJGC
# @TheWorldFoundry
from pymclevel import alphaMaterials

displayName = "ExtraBlocks_v3"

'''
Mode
	'Game fill'
		move all water blocks in the selection to the second layer and fill the first layer with the specified block
		useful for placing blocks in water without deleting the water blocks
	
	'overlay on first (water)'
		replaces air blocks in the first layer and sets the second layer where the first is not air
		when the specified block is not a fluid, fluid in the world is moved to the second block and the specified block placed on the first
		useful for flooding a region with water without removing the blocks that are there

	'Underlay on first (invisible bedrock)'
		moves the first layer to the second layer and fills the first layer with the specified block
		useful for filling a region with invisible bedrock but you want it to still look like the normal blocks

	'set second'
		sets the value of the second layer no matter what. Note this can cause issues in game where the first block is air
'''

inputs = (
		("EXTRABLOCKS", "label"),
		("Read Filter for better description", "label"),
		("Mode", ('Game fill', 'overlay on first (water)', 'Underlay on first (invisible bedrock)', 'set second')),
		("Block:", alphaMaterials.Water),
		("@gentlegiantJGC", "label"),
		("adrian@TheWorldFoundry.com", "label"),
		("http://theworldfoundry.com", "label"),
)

def perform(level, box, options):
	if level.gamePlatform != 'PE':
		raise Exception('This filter can only be used on a Bedrock world')
	def waterlog():
		materialID = options["Block:"].ID
		materialData = options["Block:"].blockData

		saveInPlace = False #if you want to save while processing set this to True. Will not be able to undo
		chunksCompleted = 0
		chunkCount = box.chunkCount

		for chunk, slices, _ in level.getChunkSlices(box):
			if options['Mode'] == 'Game fill':
				liquidMask = (8 <= chunk.Blocks[slices]) & (chunk.Blocks[slices] <= 11)
				chunk.extra_blocks[slices][liquidMask] = chunk.Blocks[slices][liquidMask][:]
				chunk.extra_blocks_data[slices][liquidMask] = chunk.Data[slices][liquidMask][:]
				chunk.Blocks[slices] = materialID
				chunk.Data[slices] = materialData
			elif options['Mode'] == 'overlay on first (water)':
				if 8<=materialID<=11:
					airMask = chunk.Blocks[slices] == 0
				else:
					liquidMask = (8 <= chunk.Blocks[slices]) & (chunk.Blocks[slices] <= 11)
					chunk.extra_blocks[slices][liquidMask] = chunk.Blocks[slices][liquidMask][:]
					chunk.extra_blocks_data[slices][liquidMask] = chunk.Data[slices][liquidMask][:]
					airMask = (chunk.Blocks[slices] == 0) & liquidMask
				chunk.extra_blocks[slices][~airMask] = materialID
				chunk.extra_blocks_data[slices][~airMask] = materialData
				chunk.Blocks[slices][airMask] = materialID
				chunk.Data[slices][airMask] = materialData
			elif options['Mode'] == 'set second':
				chunk.extra_blocks[slices] = materialID
				chunk.extra_blocks_data[slices] = materialData
			elif options['Mode'] == 'Underlay on first (invisible bedrock)':
				chunk.extra_blocks[slices] = chunk.Blocks[slices][:]
				chunk.extra_blocks_data[slices] = chunk.Data[slices][:]
				chunk.Blocks[slices] = materialID
				chunk.Data[slices] = materialData
			chunk.dirty = True
			chunksCompleted += 1
			yield chunksCompleted, chunkCount
			if saveInPlace and chunksCompleted % 5000 == 4999:
				yield 'Saving to disk and clearing memory'
				for i, _ in enumerate(level.saveInPlaceGen()):
					yield 'Saved {} of {} chunks'.format(i, 5000)
				level._loadedChunks.clear()


		yield "Waterlogging Done!"

	level.showProgress("Processing chunks:", waterlog())