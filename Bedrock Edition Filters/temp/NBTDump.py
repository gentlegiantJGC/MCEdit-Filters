import json
import os
from pymclevel.leveldbpocket import loadNBTCompoundList
from PIL import Image
import binascii

inputFolder = r"C:\Users\james_000\Desktop\DB Dump\hex"

for fileName in os.listdir(inputFolder):
	if fileName.endswith('.json'):
		continue
	f = open(inputFolder+os.sep+fileName, 'rb').read()
	if f == '':
		continue
	try:
		nbtdata = loadNBTCompoundList(f)
	except:
		continue

	fOut = open(inputFolder+os.sep+fileName+".json", 'w')
	for key in nbtdata:
		fOut.write(str(key))
		fOut.write('\n')
		if fileName.startswith(binascii.hexlify('map_')):
			imgOut = Image.new("RGBA", (128,128))
			pixels = key["colors"].value
			for x in range(128):
				for y in range(128):
					# print pixels[256*y+x]
					imgOut.putpixel((x,y), (int(pixels[(128*y+x)*4]), int(pixels[(128*y+x)*4+1]), int(pixels[(128*y+x)*4+2]), int(pixels[(128*y+x)*4+3])))
			imgOut.save(inputFolder+os.sep+binascii.unhexlify(fileName)+".png","PNG")
	fOut.close()
		
		
