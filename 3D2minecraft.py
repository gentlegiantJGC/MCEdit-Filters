#Written by gentlegiantJGC
#http://youtube.com/gentlegiantJGC
#https://twitter.com/gentlegiantJGC

#A big thanks to Ken Silverman for poly2vox which is what voxelizes the 3d model that you give it
#This script will take the file that it exports and convert it to schematic
#It also automates the process of giving the 3d model to the voxelization program

'''
READ ME
This is currently a windows only program for most of it because poly2vox is windows only
If you somehow get poly2vox working on a non-windows machine then you can select kv6 to schematic mode which will allow you to import
the kv6 file that poly2vox spits out. That part of the script should work cross platform.

SET UP
First of all you need to put this script in your Filters directory (that part should be simple)
Secondly you will need to make a folder called 'kv6' in the Filters directory and then download poly2vox from Ken Silverman's page
http://advsys.net/ken/download.htm (about half way down CTRL+F POLY2VOX.ZIP if you are having trouble)
Extract poly2vox.exe and put it in the kv6 folder that you just made

That should be everything you should need before running the filter (bar of course a 3d model to convert)

'''


'''
TODO
Sort out the colourpalletscan issue

'''


import os
import mcplatform
from pymclevel import MCSchematic
import subprocess
import binascii
import shutil
import directories

displayName = "3D-2-Minecraft"

inputs = (
	("Thanks to Ken Silverman for poly2vox", "label"),
	("A bit of setup is required. Either watch the video or read the readme at the start of the filter", "label"),
	("Mode", ("3d Model to Schematic","kv6 To Schematic", "Get Colour Pallet")),
	("3d import limits", ("Default", "Max dimension", "Scale Factor")),
	("Limit Value", -1.0),
	("Leave kv6 (for debugging)", False),
	)

def bytereverse(kv6, start, le):
	string = ''
	for l in range(le):
		string += kv6[2*(start+le-l)-2:2*(start+le-l)]
	return string
	
def maketex(kv6path, name, r, g, b):
	img = [[r, g, b, 255]]
	png.from_array(img, 'RGBA').save(kv6path+os.sep+name)
	
	# Two functions written by Adrian Brightmoore. More code further down is lifted from one of his filters
	# http://www.youtube.com/abrightmoore
# def getPixel(pixels, x, y):
	# idx = x*4
	# return (pixels[y][idx], pixels[y][idx+1], pixels[y][idx+2], pixels[y][idx+3])
	
def closestMaterial(ColourPallet, r, g, b):
	closest = 255*255*3
	best = (1, 0)
	for (mr, mg, mb, bid, dam) in ColourPallet:
		(dr, dg, db) = (r-mr, g-mg, b-mb)
		dist = dr*dr+dg*dg+db*db
		if dist < closest:
			closest = dist
			best = (bid, dam)
	return best
	
def kv62sch(level, kv6, colourpalletscan):
	if kv6[0:8].decode('hex') != 'Kvxl':
		raise Exception ("Not the correct file format")
	xdim = int(bytereverse(kv6, 4, 4), 16)
	ydim = int(bytereverse(kv6, 8, 4), 16)
	zdim = int(bytereverse(kv6, 12, 4), 16)
	count = int(bytereverse(kv6, 28, 4), 16)
	element = []
	per = 10
	pertem = 0
	for block in range(count):
		element.append([int(kv6[64+16*block:16*block+66], 16), int(kv6[66+16*block:16*block+68], 16), int(kv6[68+16*block:16*block+70], 16), int(kv6[70+16*block:16*block+72], 16), int(bytereverse(kv6, 8*block+36, 2), 16)])
		pertem += (1.0/count)*100.0
		if pertem > per:
			print str(per)+'% read'
			per += 10
	if count > 10000000:
		print 'NOTE: If you are importing a large file there may be a small wait before writing'
	xlist = []
	for block in range(xdim):
		xlist.append(int(bytereverse(kv6, 32+8*count+4*block, 4), 16))
	xylist = []
	for block in range(ydim*xdim):
		xylist.append(int(bytereverse(kv6, 32+8*count+4*xdim+2*block, 2), 16))
	
	tempids = []
	for id in colourpalletscan:
		tempids.append([id[3],id[4]])
	ColourPallet = colourpalletscan
	for id in DefaultColourPallet:
		if [id[3],id[4]] not in tempids:
			ColourPallet.append(id)
	
	# import inspect
	# try:
		# editor
	# except:
		# editor = inspect.stack()[1][0].f_locals.get('self', None).editor
		
	schematic = MCSchematic((xdim, zdim, ydim), mats=level.materials)
	
	per = 10
	pertem = 0
	
	x=0
	y=0
	elementno = 0
	xslice = xlist[x]
	for xy in xylist:
		if y == ydim:
			x += 1
			xslice = xlist[x]
			y = 0
		for elmnt in range(xy):
			(block, damage) = closestMaterial(ColourPallet, element[elementno][2], element[elementno][1], element[elementno][0])
			schematic.setBlockAt(x, zdim - element[elementno][4]-1, y, block)
			schematic.setBlockDataAt(x, zdim - element[elementno][4]-1, y, damage)
			
			pertem += (1.0/count)*100.0
			if pertem > per:
				print str(per)+'% written'
				per += 10
			
			elementno += 1
			xslice -= 1
		y+=1
			
	editor.addCopiedSchematic(schematic)
	
def perform(level, box, options):
	global colourpalletscan
	try:
		colourpalletscan
	except:
		colourpalletscan = []
		

	if options["Mode"] == "3d Model to Schematic":
		file = mcplatform.askOpenFile(title="Select the 3D Model", schematics=False)
		if file == None:
			raise Exception('No Model File Specified')
		model = file.split(os.sep)[-1]
		oripath = os.sep.join(file.split(os.sep)[0:-1])
		kv6path = directories.getFiltersDir()
		
		#checking all the required files exist and errors if they don't
		if not os.path.isdir(os.sep.join(kv6path.split(os.sep)[0:-1])):
			print 'FILE PATH'
			print os.sep.join(kv6path.split(os.sep)[0:-1])
			raise Exception ('Hmm it seems you do not have a filter directory in the location I expected')
		if not os.path.isdir(kv6path):
			print 'FILE PATH'
			print kv6path
			print 'You must make a folder within your main filter directory called kv6'
			print 'In there you must put the poly2vox exe'
			print 'If you believe you have a folder located there and the file path points to a different place send me a message with the path and I will see what I can do'
			raise Exception ('Check the console. There is an error there')
		if not os.path.isfile(str(kv6path+os.sep)+'poly2vox.exe'):
			print 'FILE PATH'
			print str(kv6path+os.sep)+'poly2vox.exe'
			print 'The folder must exist in the correct location but poly2vox cannot be found'
			raise Exception ('poly2vox not found. Please read the readme. If the path printed in the console is poiting somewhere else let me know')
		
		if model[-4:].lower() in ['.obj', '.asc', '.3ds', '.md2', '.md3', '.stl']:
			shutil.copyfile(kv6path+os.sep+'poly2vox.exe', oripath+os.sep+'poly2vox.exe')
		else:
			raise Exception ('file format selected not supported')
		
		if options["3d import limits"] == "Default":
			argument = str(model)+' kv6.kv6'
		elif options["3d import limits"] == "Max dimension":
			argument = str(model)+' kv6.kv6 /v'+str(int(options["Limit Value"]))
		elif options["3d import limits"] == "Scale Factor":
			argument = str(model)+' kv6.kv6 /s'+str(options["Limit Value"])
		
		defaultdir = os.getcwd()
		os.chdir(oripath)
		#being super cautious here because I have changed the working directory which is probably a dirty thing
		#to do but textures won't get noticed if poly2vox is run from a different folder. It was either change the
		#working directory to keep everything together or put everything in the main mcedit directory which would
		#make a mess and be very difficult to clean up. If any step in the conversion process fails the working
		#directory needs to be changed back to default otherwise it will mess up MCedit and a restart of the program
		#would be required.
		print 'poly2vox '+str(argument)
		try:
			os.system('poly2vox '+str(argument))
		except:
			os.chdir(defaultdir)
			raise Exception ("Failure at Voxelization.")
			
		os.chdir(defaultdir)
			
		try:
			kv6 = binascii.hexlify(open(oripath+os.sep+'kv6.kv6', "rb").read())
		except:
			raise Exception ("Failure to read kv6 file.")
		
		try:
			kv62sch(level, kv6, colourpalletscan)
		except:
			raise Exception ("Failure to convert to schematic.")
			
		try:
			os.remove(oripath+os.sep+'poly2vox.exe')
		except:
			print 'Unable to remove poly2vox.exe in '+oripath+'. You will have to have a look why it could not be removed'
		
		if not options["Leave kv6 (for debugging)"]:
			try:
				os.remove(oripath+os.sep+'kv6.kv6')
			except:
				print 'Unable to remove kv6.kv6 in '+oripath+'. You will have to have a look why it could not be removed'
			
		raise Exception('Conversion Finished')
		
	if options["Mode"] == "kv6 To Schematic":
		file = mcplatform.askOpenFile(title="Select the kv6 file", schematics=False, suffixes=['kv6'])
		if file == None:
			raise Exception ('No File Selected')
		kv6 = binascii.hexlify(open(file, "rb").read())
		kv62sch(level, kv6, colourpalletscan)
		
		raise Exception('Conversion Finished')
		
		
	elif options["Mode"] == "Get Colour Pallet":
		from PIL import Image
		colourpalletscan = []
		file = mcplatform.askOpenFile(title="Select an image within the folder", schematics=False)
		if file == None:
			raise Exception('No File Specified')
		filepath = os.sep.join(file.split(os.sep)[0:-1])
		imgno = 0
		imgcomp = Image.new('RGBA', (32, 16*len(Name2ID)))
		for blockname in Name2ID:
			if os.path.isfile(filepath+os.sep+blockname+'.png'):
				img = Image.open(filepath+os.sep+blockname+'.png')
				(width, height) = img.size
				rtot = 0
				gtot = 0
				btot = 0
				pixelcount = 0
				for y in range(height):
					for x in range(width):
						if len(img.getpixel((x, y))) == 3:
							(r, g, b) = img.getpixel((x, y))
							a = 255
						elif len(img.getpixel((x, y))) == 4:
							(r, g, b, a) = img.getpixel((x, y))
						else:
							raise exception("soooo ... erm ... I don't quite know what this texture is")
						if a > 128:
							rtot += r
							gtot += g
							btot += b
							pixelcount+=1
				ravg = rtot/pixelcount
				gavg = gtot/pixelcount
				bavg = btot/pixelcount
				idmg = Name2ID[blockname]
				imgcomp.paste(img, (0, 16*imgno))
				imgcomp.paste((ravg, gavg, bavg, 255), (16, 16*imgno, 32, 16*imgno + 16))
				imgno += 1
				print [ravg, gavg, bavg, idmg[0], idmg[1]]
				colourpalletscan.append([ravg, gavg, bavg, idmg[0], idmg[1]])
		imgcomp.save(filepath+os.sep+'imgcomp.png', 'PNG')

'''
Name2ID = {
	"stone" : [1,0],
		"stone_granite" : [1,1],
		"stone_granite_smooth" : [1,2],
		"stone_diorite" : [1,3],
		"stone_diorite_smooth" : [1,4],
		"stone_andesite" : [1,5],
		"stone_andesite_smooth" : [1,6],
	"coarse_dirt" : [3,1],
	"cobblestone" : [4,0],
	"planks_oak" : [5,0],
		"planks_spruce" : [5,1],
		"planks_birch" : [5,2],
		"planks_jungle" : [5,3],
		"planks_acacia" : [5,4],
		"planks_big_oak" : [5,5],
	"bedrock" : [7,0],
	
  #	These seemed like they could cause some issues so I have commented
  #	them to remove them from the list. If you wish to enable them just
  #	remove the hash symbol from before that line but be aware that they
  #	may potentially cause issues so use your own judgement.
#	"water_still" : [9,0],
#	"lava_still" : [11,0],
#	"sand" : [12,0],
#		"red_sand" : [12,1],
#	"gravel" : [13,0],

  #	These ones just look a little ugly due to the variying texture.
  #	Feel free to enable but they could make the build look a little odd.
#	"gold_ore" : [14,0],
#	"iron_ore" : [15,0],
#	"coal_ore" : [16,0],
	
	"log_oak" : [17,12],
		"log_spruce" : [17,13],
		"log_birch" : [17,14],
		"log_jungle" : [17,15],
		
  #	Biome issues and textures being grayscale
#	"leaves_oak" : [18,4],
#		"leaves_spruce" : [18,5],
#		"leaves_birch" : [18,6],
#		"leaves_jungle" : [18,7],
	
	"sponge" : [19,0],
		"sponge_wet" : [19,1],
		
#	"glass" : [20,0],
#	"lapis_ore" : [21,0],
	
	"lapis_block" : [22,0],
	
	"noteblock" : [25,0],
	
	"wool_colored_white" : [35,0],
		"wool_colored_orange" : [35,1],
		"wool_colored_magenta" : [35,2],
		"wool_colored_light_blue" : [35,3],
		"wool_colored_yellow" : [35,4],
		"wool_colored_lime" : [35,5],
		"wool_colored_pink" : [35,6],
		"wool_colored_gray" : [35,7],
		"wool_colored_silver" : [35,8],
		"wool_colored_cyan" : [35,9],
		"wool_colored_purple" : [35,10],
		"wool_colored_blue" : [35,11],
		"wool_colored_brown" : [35,12],
		"wool_colored_green" : [35,13],
		"wool_colored_red" : [35,14],
		"wool_colored_black" : [35,15],
	"gold_block" : [41,0],
	"iron_block" : [42,0],
	
	"stone_slab_top" : [43, 8],
	"sandstone_top" : [43,9],
	"quartz_block_top" : [43,15],
	"brick" : [45,0],
	"cobblestone_mossy" : [48,0],
	"obsidian" : [49,0],
	
#	"diamond_ore" : [56,0],
	"diamond_block" : [57,0],
#	"redstone_ore" : [73,0],
#	"ice" : [79,0],
	"snow" : [80,0],
	"clay" : [82,0],
#	"pumpkin_side" : [86,4],
	"netherrack" : [87,0],
	"soul_sand" : [88,0],
	"glowstone" : [89,0],
#	"glass_white" : [95,0],
#		if you want the other glass variants put them here
#		since it is transparent it kind of seems pointless including it
	
	"stonebrick" : [98,0],
	"stonebrick_mossy" : [98,1],
	"stonebrick_cracked" : [98,2],
	"stonebrick_carved" : [98,3],
	"mushroom_block_inside" : [99,0],
	"mushroom_block_skin_brown" : [99,14],
	"mushroom_block_skin_stem" : [99,15],
	"mushroom_block_skin_red" : [100,14],
	
#	"melon_side" : [103,0],
	
	"nether_brick" : [112,0],
	"end_stone" : [121,0],
#	"redstone_lamp_off" : [123,0],
  #	Lighting and powering issues	
#	"redstone_lamp_on" : [124,0],

	"emerald_block" : [133,0],
	"redstone_block" : [152,0],
#	"quartz_ore" : [153,0],
	"quartz_block_chiseled" : [155,1],
	
	"hardened_clay_stained_white" : [159,0],
		"hardened_clay_stained_orange" : [159,1],
		"hardened_clay_stained_magenta" : [159,2],
		"hardened_clay_stained_light_blue" : [159,3],
		"hardened_clay_stained_yellow" : [159,4],
		"hardened_clay_stained_lime" : [159,5],
		"hardened_clay_stained_pink" : [159,6],
		"hardened_clay_stained_gray" : [159,7],
		"hardened_clay_stained_silver" : [159,8],
		"hardened_clay_stained_cyan" : [159,9],
		"hardened_clay_stained_purple" : [159,10],
		"hardened_clay_stained_blue" : [159,11],
		"hardened_clay_stained_brown" : [159,12],
		"hardened_clay_stained_green" : [159,13],
		"hardened_clay_stained_red" : [159,14],
		"hardened_clay_stained_black" : [159,15],
		
	"log_acacia" : [162,12],
	"log_big_oak" : [162,13],
	
	"prismarine_rough" : [168,0],
	"prismarine_dark" : [168, 2],
	
	"hardened_clay" : [172,0],
	"coal_block" : [173,0],
	"ice_packed" : [174,0],
	
	"red_sandstone_top" : [181,8]
	
	
	}
'''

Name2ID = {

	"coarse_dirt" : [3,1],
	"planks_oak" : [5,0],
		"planks_spruce" : [5,1],
		"planks_birch" : [5,2],
		"planks_jungle" : [5,3],

		"planks_big_oak" : [5,5],

	
		"log_spruce" : [17,13],
		"log_jungle" : [17,15],
	
	"sponge" : [19,0],

	
	"lapis_block" : [22,0],

	
	"wool_colored_white" : [35,0],
		"wool_colored_orange" : [35,1],
		"wool_colored_magenta" : [35,2],
		"wool_colored_light_blue" : [35,3],
		"wool_colored_yellow" : [35,4],
		"wool_colored_lime" : [35,5],
		"wool_colored_pink" : [35,6],
		"wool_colored_gray" : [35,7],
		"wool_colored_silver" : [35,8],
		"wool_colored_cyan" : [35,9],
		"wool_colored_purple" : [35,10],
		"wool_colored_blue" : [35,11],
		"wool_colored_brown" : [35,12],
		"wool_colored_green" : [35,13],
		"wool_colored_red" : [35,14],
		"wool_colored_black" : [35,15],
	"gold_block" : [41,0],
	"iron_block" : [42,0],
	
	"stone_slab_top" : [43, 8],
	"sandstone_top" : [43,9],
	"quartz_block_top" : [43,15],

	"obsidian" : [49,0],

	"diamond_block" : [57,0],

	"snow" : [80,0],
	"clay" : [82,0],

	"soul_sand" : [88,0],
	# "stonebrick" : [98,0],
	"mushroom_block_inside" : [99,0],
	"mushroom_block_skin_brown" : [99,14],
	"mushroom_block_skin_stem" : [99,15],
	"mushroom_block_skin_red" : [100,14],
	
	"nether_brick" : [112,0],
	"end_stone" : [121,0],

	"emerald_block" : [133,0],
	"quartz_block_chiseled" : [155,1],
	
	"hardened_clay_stained_white" : [159,0],
		"hardened_clay_stained_orange" : [159,1],
		"hardened_clay_stained_magenta" : [159,2],
		"hardened_clay_stained_light_blue" : [159,3],
		"hardened_clay_stained_yellow" : [159,4],
		"hardened_clay_stained_lime" : [159,5],
		"hardened_clay_stained_pink" : [159,6],
		"hardened_clay_stained_gray" : [159,7],
		"hardened_clay_stained_silver" : [159,8],
		"hardened_clay_stained_cyan" : [159,9],
		"hardened_clay_stained_purple" : [159,10],
		"hardened_clay_stained_blue" : [159,11],
		"hardened_clay_stained_brown" : [159,12],
		"hardened_clay_stained_green" : [159,13],
		"hardened_clay_stained_red" : [159,14],
		"hardened_clay_stained_black" : [159,15],
		
	"log_acacia" : [162,12],
	"log_big_oak" : [162,13],
	
	"prismarine_dark" : [168, 2],
	
	"hardened_clay" : [172,0],
	"coal_block" : [173,0],
	"ice_packed" : [174,0],
	
	"red_sandstone_top" : [181,8]
	
	
	}

DefaultColourPallet=[
[105, 99, 89, 162, 12],
[195, 179, 123, 5, 2],
[76, 83, 42, 159, 13],
[119, 85, 59, 3, 1],
[177, 166, 39, 35, 4],
[156, 127, 78, 5, 0],
[103, 77, 46, 5, 1],
[74, 59, 91, 159, 11],
[194, 195, 84, 19, 0],
[221, 221, 221, 35, 0],
[179, 80, 188, 35, 2],
[53, 70, 27, 35, 13],
[231, 228, 220, 155, 1],
[209, 178, 161, 159, 0],
[154, 110, 77, 5, 3],
[38, 67, 137, 22, 0],
[143, 61, 46, 159, 14],
[150, 52, 48, 35, 14],
[45, 28, 12, 17, 13],
[84, 64, 51, 88, 0],
[52, 40, 23, 162, 13],
[219, 219, 219, 42, 0],
[135, 106, 97, 159, 8],
[221, 223, 165, 121, 0],
[186, 133, 35, 159, 4],
[150, 92, 66, 172, 0],
[106, 138, 201, 35, 3],
[87, 67, 26, 17, 15],
[239, 251, 251, 80, 0],
[126, 61, 181, 35, 10],
[113, 108, 137, 159, 3],
[18, 18, 18, 173, 0],
[219, 125, 62, 35, 1],
[81, 217, 117, 133, 0],
[218, 210, 158, 43, 9],
[25, 22, 22, 35, 15],
[161, 83, 37, 159, 1],
[141, 106, 83, 99, 14],
[149, 88, 108, 159, 2],
[37, 22, 16, 159, 15],
[59, 87, 75, 168, 2],
[208, 132, 153, 35, 6],
[64, 64, 64, 35, 7],
[57, 42, 35, 159, 7],
[20, 18, 29, 49, 0],
[65, 174, 56, 35, 5],
[166, 85, 29, 181, 8],
[161, 78, 78, 159, 6],
[77, 51, 35, 159, 12],
[46, 56, 141, 35, 11],
[207, 204, 194, 99, 15],
[118, 70, 86, 159, 10],
[236, 233, 226, 43, 15],
[79, 50, 31, 35, 12],
[182, 37, 36, 100, 14],
[97, 219, 213, 57, 0],
[159, 159, 159, 43, 8],
[44, 22, 26, 112, 0],
[165, 194, 245, 174, 0],
[158, 164, 176, 82, 0],
[202, 171, 120, 99, 0],
[103, 117, 52, 159, 5],
[249, 236, 78, 41, 0],
[46, 110, 137, 35, 9],
[86, 91, 91, 159, 9],
[154, 161, 161, 35, 8],
[61, 39, 18, 5, 5]

]
