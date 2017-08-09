#Written by gentlegiantJGC
#http://youtube.com/gentlegiantJGC
#https://twitter.com/gentlegiantJGC

# if you are going to use the code in this filter please give credit

# Note PE/Windows 10... (Bedrock Edition) only
# This filter was written to create sub-chunks in MCedit that have not been created by the game
# MCedit will allow you to paste/clone/fill in sub-chunks that have not been created but they will
# not get written to disk because the sub-chunk was technically never created in MCedit

displayName = "Create Sub-Chunks"

inputs = (
	("Unmodified sub-chunks are not saved", "label"),
	("to disk. This filter will create", "label"),
	("sub-chunks in and below the selection", "label"),
	)
	
def perform(level, box, options):
	emptyChunks = False
	if level.gameVersion != 'PE':
		raise Exception('Must be a PE/Win10... world')
	# iterating through every chunk in the box
	for cx, cz in box.chunkPositions:
		try:
			# get the chunk object
			chunk = level.getChunk(cx, cz)
		except:
			# if the whole chunk does not exist then continue to the next one
			# the chunk probably could be generated within MCedit but it wouldn't contain any terrain
			# and I don't know how the game would deal with it.
			# It may regerate the chunk since it is empty or might leave it as it is
			if not emptyChunks:
				print '========================================'
			print 'issue loading chunk ('+str(cx)+', '+str(cz)+'). Go near it in game to genearate terrain'
			emptyChunks = True
			continue
		# terrain tag in the format (version x1, blocks (air) x4096, block data x4096*0.5, sky light x4096*0.5, block light x4096*0.5) 
		terrain = chunk.version+'\x00'*4096+'\x00'*2048+'\x00'*2048+'\x00'*2048
		# for every chunk up to the top of the selection box
		for i in range(max(1,1+(box.maxy-1)/16)):
			# if the sub-chunk does not already exist
			if i not in chunk.subchunks:
				# create it with the terrain value created earlier
				chunk.add_data(terrain=terrain, subchunk=i)
		# tell MCedit the chunk has changed
		chunk.dirty = True
	if emptyChunks:
		print '========================================'
		print 'The chunks above could not be processed because terrain has not been generated'
		print '========================================'
		print ''
		raise Exception('Some chunks could not be generated. Check the console for locations')