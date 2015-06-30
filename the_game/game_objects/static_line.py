from editable import Editable
from _env import *

def distance( a, b ): return sum ( [ (x1-x2)**2 for x1,x2 in zip( a, b ) ] ) ** .5

class UserStaticLine( Editable ):
    color         = (0,1,0,1)
    colltype      = COLLTYPE_USERPLAT

    def adjust_coordinates( self, (ox, oy), (xdim, ydim) ):
        # Find absolute postion based on the passed-in pos and size.
        self.points = self.get_start(), self.get_end()

    def divide( self, S1, S2 ):
        a, b = S1
        c, d = S2

        if distance( a, b ) > 10:
            # Create a new line, passing in the start and end of S1.
            self.physics_interface.add_user_static_line( a, b )

        if distance( c, d ) > 10:
            # Create a new line, passing in the start and end of S2.
            self.physics_interface.add_user_static_line( c, d )


        

