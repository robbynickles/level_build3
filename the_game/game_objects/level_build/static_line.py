from _env import *

class PreStaticLine(GameObject):
    width = 1

    def store_relative( self, (ox,oy), (xdim,ydim), (x1,y1), (x2,y2) ):
        # Store the points (in percentages, not absolute postions) and color for later use.
        self.relative_points = (x1-ox)/xdim, (y1-oy)/ydim, (x2-ox)/xdim, (y2-oy)/ydim

    def __init__( self, physics_interface, (x1,y1), (x2,y2) ):
        GameObject.__init__( self )
        ox, oy      = physics_interface.pos
        xdim, ydim  = physics_interface.size
        self.store_relative( (ox,oy), (xdim, ydim), (x1,y1), (x2,y2) )
        self.color  = 1,0,0,1

        # Represent the object on the level-builder screen.
        self.load_into_physics_interface( physics_interface )

    def adjust_coordinates( self, pos, size ):
        ox, oy         = pos
        xdim, ydim     = size
        x1, y1, x2, y2 = self.relative_points

        # Find absolute postion based on the passed-in pos and size.
        x1, y1, x2, y2 = x1*xdim+ox, y1*ydim+oy, x2*xdim+ox, y2*ydim+oy
        self.points = x1, y1, x2, y2

    ##### Delayed execution of body building and canvas instruction building:
    def build_phys_obj( self, space ):
        x1, y1, x2, y2 = self.points
        seg = cy.Segment(space.static_body, Vec2d(x1,y1), Vec2d(x2,y2), self.width)
        #seg.friction = 0.99
        seg.elasticity = 0.7
        self.shapes += [ seg ]

    def build_render_obj( self ):
        color = Color( *self.color )
        line  = Line( points=self.points, width=self.width )
        self.render_obj = color, line

