from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.core.image import Image

import os
from os.path import dirname, join

from zoom import zoom
from crop import crop


def load_texture( pth ):
    return Image(pth,  mipmap=True).texture

def world_to_photo( (ox,oy), (x,y) ):
    return x-ox, y-oy


def clear_magnifier( self ):
    # Remove the canvas instructions corresponding to the magnifier lens.
    for instr in self.lens:
        self.canvas.after.remove( instr )
    self.lens = ()

    # Remove the magnifier lens .png file.
    if self.lens_image != None:
        os.remove( self.lens_image )
        self.lens_image = None

def magnify_touch( self, touch ):
    # Clear the magnifier.
    clear_magnifier( self )

    # Store the image of the magnifier lens to the path 'magnifier_lens.png'.
    self.lens_image = str( touch.time_update ) + '.png'
        
    # Take a screenshot of this widget and the tree rooted at this widget.
    self.export_to_png( self.lens_image )

    # Magnify (zoom and crop) the screenshot centered at touch.pos.
    zoom_scale      = 10
    crop_radius     = 512
    magnifier_image = crop( zoom( self.lens_image, world_to_photo( self.pos, touch.pos ), zoom_scale ), crop_radius )
    magnifier_image.save( self.lens_image )
        
    # Render the magnification photo and a magnifier outline to self.canvas.
    d               = 128 + 64
    OFFSET          = d/2 + 10
    self.lens       = ( Color( 1,1,1,1 ),
                        Ellipse( texture=load_texture( self.lens_image ),
                                 pos=(touch.x-d/2, touch.y-d/2 + OFFSET),
                                 size=(d,d) ),
                        Line( circle=(touch.x, touch.y + OFFSET, d/2) ) )
    for instr in self.lens:
        self.canvas.after.add( instr )
