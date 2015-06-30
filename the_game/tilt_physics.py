from libs.game.physics_interface.physics_interface import PhysicsInterface

from game_objects.static_line import UserStaticLine
from game_objects.static_curve import UserStaticCurve
from game_objects.falling_ball import Ball

from math import sin, cos

class TiltPhysics( PhysicsInterface ):
    user_lines = []


    ##### Acceleromter ---> Tilt mapping helpers.
    def normalize( self, x ):
        "Normalize x (get the direction of the vector)."
        return abs(x) / x

    def combine( self, a, b ):
        "Combine a and b to form a Pythagorean diagonal."
        return ( a**2 + b**2 ) ** .5
        
    def transfer_acceleration( self, z_acc ):
        "Return a function that adds z-axis acceleration to an axis."
        A = 1 - z_acc**2
        def add_z( acc ):
            return self.normalize( acc ) * self.combine( acc, (acc**2/A)*abs(z_acc) )
        return add_z

        
    ##### Acceleromter ---> Tilt mapping 
    def gravity_transformation( self ):
        # Map the real-world gravity vector to the game's gravity vector.
        # The mathematical limitations are such that if x_acc and y_acc are close to zero,
        # it's not known how to tilt gravity. Probably want to pause the game and inform the player
        # that whenever the phone goes perfectly flat, the game will pause. (Modern take on the buzzer
        # when you shake the pinball machine.)
        x_acc, y_acc, z_acc = self.accelerometer.acceleration[:3]
        try:
            add_z              = self.transfer_acceleration( z_acc )
            self.space.gravity = ( add_z( x_acc ) * self.world_gravity, 
                                   add_z( y_acc ) * self.world_gravity )
        except:
            # Probably a ZeroDivision error because either the device-motion updates haven't started,
            # or the phone is flat (z^2 = 1 ====> A = 0 ====> x^2/A ====> undefined )
            pass


    ##### Start/Stop level
    # Drop a ball at the top-left corner.
    def start_level( self ):
        self.add_circle(self.parent.x+50, self.parent.y+self.parent.height-20, 15)

    # Destroy the ball.
    def stop_level( self ):
        for obj in self.get_game_objects():
            if isinstance( obj, Ball ):
                try:
                    obj.remove()
                except:
                    pass


    ##### Helper (used in scoring function)
    # Return the total length of line that the user has drawn.
    def length_of_user_lines( self ):

        # Adjust self.user_lines so that it reflects the current set of gameobjects.
        current_objects = self.get_game_objects()
        current_lines   = []
        for l in self.user_lines:
            if l in current_objects:
                current_lines += [ l ]

        self.user_lines = current_lines

        return sum( [ l.length() for l in self.user_lines ] )


    ##### Methods that add game objects
    def add_circle(self, x, y, radius):
        Ball( self, x, y, radius )

    def add_user_static_line( self, (x1,y1), (x2,y2) ):
        self.user_lines += [ UserStaticLine( self, (x1, y1), (x2, y2) ) ]

    def add_user_static_curve( self, (x1,y1), (x2,y2), thirdpt=None ):
        self.user_lines += [ UserStaticCurve( self, (x1, y1), (x2, y2), thirdpt=thirdpt ) ]

