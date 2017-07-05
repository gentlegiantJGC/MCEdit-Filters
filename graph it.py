# This will make a graph in the format that you specify
# Select a region around the origin and then click filter
# The height of the selection box does not matter but the depth and length does
# If you are going to write your own equation then you will need to replace x with k and z with m
# Sample rate is the number of calculations that it will do per block in one direction
# If you are putting in an exponential graph then increase this number

import math

displayName = "Graph it"

inputs = (
    ("x^5", 0.0),
	("x^4", 0.0),
	("x^3", 0.0),
	("x^2", 0.0),
	("x", 0.0),
	("c", 0.0),
	("sample rate", 2),
)

def perform(level, box, options):
	block = 1
	data = 1
	y = 0
	a = options["x^5"]
	b = options["x^4"]
	c = options["x^3"]
	d = options["x^2"]
	e = options["x"]
	f = options["c"]
	sample = options["sample rate"]
	
	for x in xrange(box.minx, box.maxx):
		k = x
		print "x=" +str(x)+ " "
		for dep in xrange(1, sample):
			k = k + (1.0 / sample)
			for z in xrange(box.minz, box.maxz):
				m = z
				for len in xrange(1, sample):
					m = m + 1.0 / sample
					# this is where the magic happens. To use the functions at the bottom
					# comment out the line below and copy in a line from the bottom to use it
					y = a * k**5 + b * k**4 + c * k**3 + d * k**2 + e * k + f
					y = round(y)
					level.setBlockAt(x, y, z, block)
					level.setBlockDataAt(x, y, z, data)

	
	level.markDirtyBox(box)

# copy this to use the interface
# a * k**5 + b * k**4 + c * k**3 + d * k**2 + e * k + f

# this is a silly exponential (not very interesting)
# (math.exp(k) + math.exp(-k)) / 2

#really cool sin cos interference
# 30 * math.sin(k / 30) + 30 * math.sin(m / 30) + 90

#really cool tan interference
# 5 * math.tan(k / 30) + 5 * math.tan(m / 30) + 128

#3d exponential
# 100 / m + 100 / k

#a double modded cosine interference pattern. This one is really good
# math.fabs(math.fabs(30 * math.sin(k / 30) + 30 * math.sin(m / 30))-30)