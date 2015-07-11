from cymunk import Vec2d

from kivy.uix.widget import WidgetException
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line

from kivy.lang import Builder
Builder.load_file( 'the_game/drawinggame.kv' )

from libs.game.gamelayout import GameLayout

from drawing.drawingtoolkit import DrawingToolkit
from drawing.drawing_behaviors import dispatcher

from game_objects.collision_handlers import COLLTYPE_DEFAULT, COLLTYPE_BALL, COLLTYPE_USERPLAT, COLLTYPE_USERCURVE

from tilt_physics import TiltPhysics

import pickle

class DrawingGame( GameLayout ):

    ##### Instance variables used by the magnifiying lens.
    lens       = ()
    lens_image = None

    ##### Initialization
    def __init__(self, swipebook, *args, **kwargs):
        super( DrawingGame, self ).__init__( swipebook, TiltPhysics, *args, **kwargs )

        # self.switches contains entries like ( 'mode_name', mode_button ), 
        # where mode_button is one of DrawingToolkit's toggle buttons, 
        # and mode_name is its name as it's known to the dispatcher.
        # If a mode_button B is toggled, then B.state == 'down'.
        self.switches        = {} 

        # DrawingToolkit populates self.switches with references to its toolkit panel toggle buttons. 
        # When the player toggles a button, its state is visible in self.switches. Then, the dispatcher will know
        # which drawing function to call when it recieves new touch data.
        self.drawing_toolkit = DrawingToolkit( self )
        self.drawing_enabled = False
        self.active_mode     = None

        self.touching_line   = False

        # Reference to the line being edited in 'line edit' mode.
        self.target_line     = None


        # When working on desktop, it's useful to enable scaling and translation.
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
        
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        code, key = keycode

        if key == 'p':
            self.start_animation()

        # Toggle translation on and off when the key 't' is pressed.
        if key == 't':
            if self.swipebook.do_translation == (False, False):
                self.swipebook.do_translation = True
                print "Translation on"
            else:
                self.swipebook.do_translation = False
                print "Translation off"

        # Toggle scaling on and off when the key 's' is pressed.
        if key == 's':
            if self.swipebook.do_scale == False:
                self.swipebook.do_scale = True
                print "Scaling on"
            else:
                self.swipebook.do_scale = False
                print "Scaling off"

    ##### Post-startup initialization:
    # The widget tree is fully built and now coordinates are known.
    def post_startup_init( self ):
        super( DrawingGame, self ).post_startup_init(leaf=False)
        if not self.already_post_startup_initialized:
            self.already_post_startup_initialized = True
            self.drawing_toolkit.pos = self.x+self.width/2., self.y+self.height/2.
            self.swipebook.add_widget_to_layer( self.drawing_toolkit, 'top' )
            
            # Draw a border around the game.
            with self.canvas:
                Color(1,0,0,1)
                Line(rectangle=(self.x, self.y, self.width, self.height))

    def save_level( self ):

        # Pull the level number from the text input box next to the save button.
        level_number = self.ids.level_number.text
        
        # Save a picture of the level to be used as a level_button thumbnail in the level selector.
        self.physics_interface.export_to_png( "libs/level_selector/Resources/{}.png".format(level_number) )

        # Retrieve the total list of game objects currently populating the physics interface.
        level        = self.physics_interface.get_game_objects()

        # Remove all objects from the physics interface. (Without this step, the objects won't pickle)
        for obj in level: 
            obj.remove()

        # Pickle (Serialize) the objects into a file called 'levels/levelX' where X is specified by the user.
        level_name   = "levels/level{}".format( level_number ) 
        with open(level_name, 'w') as f:
            pickle.dump(level, f)

        # Load the objects back into the physics interface.
        for obj in level: 
            obj.load_into_physics_interface( self.physics_interface )

        # When working on desktop, it's useful to enable scaling and translation.
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def text_entered(self):
        
        # When working on desktop, it's useful to enable scaling and translation.
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        


    ##### Load the current level
    def build_level( self ):
        super( DrawingGame, self ).build_level()
        self.drawing_enabled = True


    ##### Touch drawing
    # Subclass the on_touch methods to implement paint-like drawing interaction.
    def on_touch_down(self, touch):
        super(DrawingGame, self).on_touch_down( touch )
        if self.do_drawpt( touch.pos ):
            if self.engine_running: #play
                # Don't respond to any touches once 'play' has been pressed.
                pass
            else: #pause

                # Look to self.switches to set the value of self.active_mode. Then dispatch to the mode's drawing functions.
                self.search_switches()

                # See if the touch is a tap on a user-platform. If so, enter into edit-line mode.
                self.enter_edit_line_mode( touch )

                # Initiate mode behavior based on which mode (if any) is active.
                self.mode_behavior( touch, 'touch_down' )

    def on_touch_move(self, touch):
        super(DrawingGame, self).on_touch_move( touch )
        if self.engine_running: #play
            # Don't respond to any touches once 'play' has been pressed.
            pass
        else: #pause
            self.mode_behavior( touch, 'touch_move' )

    def on_touch_up(self, touch):
        super(DrawingGame, self).on_touch_up( touch )
        if self.engine_running: #play
            # Don't respond to any touches once 'play' has been pressed.
            pass
        else: #pause
            self.mode_behavior( touch, 'touch_up' )

    def mode_behavior( self, touch, touch_stage ):
        """Dispatch function: call the current mode's drawing function."""
        if self.drawing_enabled:
            dispatcher.dispatch( self, touch, touch_stage )

    def do_drawpt( self, pos ):
        # Boolean used to determine if a point is good to draw.
        # Return True if the position occurs not in the drawing panel, else False.
        return not self.drawing_toolkit.collide_point( *pos )

    def enter_edit_line_mode( self, touch ):
        # A tap on a user-platform enters into edit-line mode.
        self.touching_line = False

        if self.active_mode != 'eraser':# and self.quick_and_short( touch ):
            MAX_DIST = 40

            # Query the space for the closest user-platform within a radius of MAX_DIST from the touch position.
            shape    = self.physics_interface.space.nearest_point_query_nearest( Vec2d( *touch.pos ), 
                                                                                 MAX_DIST, 
                                                                                 COLLTYPE_USERPLAT | COLLTYPE_USERCURVE )

            if shape and (shape.collision_type == COLLTYPE_USERPLAT or shape.collision_type == COLLTYPE_USERCURVE):
                self.touching_line = True

                # A double-tap on a user-drawn line, switches a line to a curve and vice versa.
                if touch.is_double_tap:
                    self.morph_line( shape )

                else: # Enter into edit line mode.
                    # Exit edit line mode for the currently targeted line, if it exists.
                    self.exit_edit_line_mode()

                    # Find the GameObject to which the 'shape' belongs.
                    self.target_line = self.physics_interface.smap[ shape ]

                    # Set active_mode to 'edit line' mode.
                    self.active_mode = 'edit line'

                    # Prepare the target_line for editing.
                    self.target_line.setup_for_editing( self.physics_interface )

    # Exit edit-line mode.
    def exit_edit_line_mode( self ):
        self.active_mode = None

        if self.target_line:
            # Prepare target_line to be loaded back into the game normally.
            self.target_line.tear_down_from_editing()

            # Load target_line normally.
            self.target_line.load_into_physics_interface( self.physics_interface )

            # Remove the reference to it.
            self.target_line = None

    def search_switches( self ):
        # Search self.switches for any 'down' buttons. 
        # Set self.active_mode to the first encounterd 'down' button.
        self.active_mode = None
        for mode_name, mode_button in self.switches.items():
            if mode_button.state == 'down':
                self.active_mode = mode_name
                return

    def morph_line( self, shape ):
        "Switch a line to a curve, and a curve to a line."

        # Find the endpoints of the target_line.
        self.target_line = self.physics_interface.smap[ shape ]
        start, end = self.target_line.get_start(), self.target_line.get_end()

        # Switch a line to a curve
        if shape.collision_type == COLLTYPE_USERPLAT:
            self.physics_interface.add_user_static_curve( start, end )
        else: # and a curve to a line.
            self.physics_interface.add_user_static_line( start, end )

        # Remove the target_line completely.
        self.target_line.remove()
        
        # Remove the reference to the dead line, else it'll be brought back to life.
        self.target_line = None

    ##### Callbacks and helpers for the top-of-the-screen buttons ('menu', 'play', 'pause') (which are defined in gamelayout.kv).
    def reset( self ):
        super(DrawingGame, self).reset()        

        # Show the drawing toolkit.
        if not self.in_success_screen:
            self.swipebook.add_widget_to_layer( self.drawing_toolkit, 'top' )

    def start_animation( self ):
        super(DrawingGame, self).start_animation()

        # Exit edit-line mode.
        self.exit_edit_line_mode()

        try:
            # Hide the drawing toolkit.
            self.swipebook.remove_widget_from_layer( self.drawing_toolkit, 'top' )
        except WidgetException:
            # The drawingtoolkit was never added.
            pass

    def menu_callback( self, button ):
        super( DrawingGame, self ).menu_callback( button )
        if self.quick_and_short( button.last_touch ) and not self.in_success_screen:
            self.drawing_enabled = False




