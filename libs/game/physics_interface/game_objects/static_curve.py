from _env import *
from editable import Editable
from static_curve_utils import fit_curve

class UserStaticCurve( Editable ):
    color    = (1,0,1,1)
    colltype = COLLTYPE_USERCURVE
    curve    = True

    def adjust_coordinates( self, (ox,oy), (xdim,ydim) ):
        # Find absolute postion based on the passed-in pos and size.
        a, b, c     = self.get_start(), self.get_thirdpt(), self.get_end()

        # Generate a segementation that approximates the curve.
        self.points = fit_curve( [ a, b, c ] )

    def divide( self, S1, S2 ):
        # Find a point X in S1
        X    = S1[ len(S1)/2 ]

        # Find a point Y in S2
        Y    = S2[ len(S2)/2 ]        

        a, b = S1[0], S1[-1]
        c, d = S2[0], S2[-1]

        # Create a new curve, passing in the start and end of S1 and X as the thirdpt.
        self.physics_interface.add_user_static_curve( a, b, thirdpt=self.get_thirdpt() )

        # Create a new curve, passing in the start and end of S2 and Y as the thirdpt.
        self.physics_interface.add_user_static_curve( c, d, thirdpt=self.get_thirdpt() )
        
