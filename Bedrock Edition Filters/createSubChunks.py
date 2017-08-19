#Written by gentlegiantJGC
#http://youtube.com/gentlegiantJGC
#https://twitter.com/gentlegiantJGC

# if you are going to use the code in this filter please give credit

# Note PE/Windows 10... (Bedrock Edition) only
# This filter was written to create sub-chunks in MCedit that have not been created by the game
# MCedit will allow you to paste/clone/fill in sub-chunks that have not been created but they will
# not get written to disk because the sub-chunk was technically never created in MCedit

import json

displayName = "Create Sub-Chunks"

inputs = (
	("Unmodified sub-chunks are not saved", "label"),
	("to disk. This filter will create", "label"),
	("sub-chunks in and below the selection", "label"),
	("Generate whole chunk without terrain", (False)),
	("The above option WILL NOT generate normal terrain", "label"),
	("Use flatworld settings to generate", (False)),
	)
	
def perform(level, box, options):
	if level.gameVersion != 'PE':
		raise Exception('Must be a PE/Win10... world')
	emptyChunks = False
	y = (box.maxy-1)/16
	if options["Generate whole chunk without terrain"] and options["Use flatworld settings to generate"]:
		try:
			with level.worldFile.world_db() as db:
				rop = level.worldFile.readOptions
				flatworldLayers = json.loads(db.Get(rop, 'game_flatworldlayers'))
		except:
			print '========================================'
			print 'Issue getting flatworldlayers key. Might not be a flatworld'
			print '========================================'
			flatworldLayers = []
			
	# iterating through every chunk in the box
	for cx, cz in box.chunkPositions:
		try:
			generateChunk(level, options["Generate whole chunk without terrain"], cx, cz, y, flatworldLayers)
		except:
			if not emptyChunks:
				emptyChunks = True
				print '========================================'
			print 'issue loading chunk ('+str(cx)+', '+str(cz)+').'
			continue

	if emptyChunks:
		print '========================================'
		print 'The chunks above could not be processed because terrain has not been generated'
		print 'Go near them in game to genearate terrain or enable the "Generate whole chunk" checkbox'
		print '========================================'
		print ''
		raise Exception('Some chunks could not be generated. Check the console for locations')
		
def generateChunk(level, generateBase, cx, cz, y, flatworldIDs=[]):
	try:
		# get the chunk object
		chunk = level.getChunk(cx, cz)
	except:		
		if generateBase:
			level.createChunk(cx,cz)
			chunk = level.getChunk(cx, cz)
		
		else:
			raise Exception()

	# terrain tag in the format (version x1, blocks (air) x4096, block data x4096*0.5, sky light x4096*0.5, block light x4096*0.5)

	# for every chunk up to the top of the selection box
	for i in range(y+1):
		# if the sub-chunk does not already exist
		if i not in chunk.subchunks:
			if type(flatworldIDs) is not list:
				raise Exception('flatworldIDs must be a list of block ids')
			if len(flatworldIDs) < i*16+1:
				blockIDsChunk = [0]*16
			elif len(flatworldIDs) > (i+1)*16:
				blockIDsChunk = flatworldIDs[i*16:(i+1)*16]
			else:
				blockIDsChunk = flatworldIDs[i*16:] + [0] * (16 - (len(flatworldIDs) - i*16))
				
			if len(blockIDsChunk) != 16:
				raise Exception('blockIDsChunk not the right size')
			blocks = ''.join([chr(block) for block in blockIDsChunk])
			terrain = chunk.version
			for _ in range(256):
				terrain += blocks
			terrain += '\x00'*2048+'\x00'*2048+'\x00'*2048
			# create it with the terrain value created earlier
			chunk.add_data(terrain=terrain, subchunk=i)
	# tell MCedit the chunk has changed
	chunk.dirty = True