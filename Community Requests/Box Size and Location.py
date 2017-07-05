displayName = "Box Size and Location"

def perform(level, box, options):
    print str(box.minx)+ " " +str(box.miny)+ " " +str(box.minz)+ " " +str(box.maxx-1)+ " " +str(box.maxy-1)+ " " +str(box.maxz-1)
	print "[x=" +str(box.minx)+ ",y=" +str(box.miny)+ ",z=" +str(box.minz)+ ",dx=" +str(box.maxx-box.minx-1)+ ",dy=" +str(box.maxy-box.miny-1)+ ",dz=" +str(box.maxz-box.minz-1)+ "]"