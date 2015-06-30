from PIL import Image, ImageOps, ImageDraw

def circle_mask( d ):
    " Usage: circle_mask( diameter ) "
    bottom_left = (0,0)
    size        = (d, d)
    mask        = Image.new( 'L', size, 0 )
    draw        = ImageDraw.Draw( mask )
    draw.ellipse(bottom_left + size, fill=255)
    return mask

def crop( im, d ):
    " Usage: crop( PIL_image ) "
    mask   = circle_mask( d )

    output = ImageOps.fit( im, mask.size, centering=(.5, .5) )

    output.putalpha( mask )
    return output
