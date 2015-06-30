from PIL import Image

from math import log

def zoom( name, (x,y), s ):
    "Usage: zoom( image_name, zoom_center, zoom_scale )"
    im           = Image.open( name )

    xdim, ydim   = im.size
    y            = ydim - y # invert y

    scale_factor = 1. / ( 8 - ( log( s ) + 3 ) )

    ox, oy       = x-(.5*xdim), y-(.5*ydim)
    xdiff, ydiff = xdim * scale_factor, ydim * scale_factor

    x0,y0        = ox+xdiff           , oy+ydiff
    x1,y1        = ox+(xdim-xdiff)    , oy+(ydim-ydiff)

    return im.transform( im.size, Image.EXTENT, (x0,y0,x1,y1) )

