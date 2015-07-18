from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
Builder.load_file( 'libs/level_selector/level_selector.kv' )

from level_button import LevelButton
import utils

class LevelSelector(GridLayout):
    def __init__(self, forward, back, *args, **kwargs):
        super(LevelSelector, self).__init__( *args, **kwargs )

        # Functions called to navigate from the level_selector screen.
        self.forward = forward
        self.back    = back

    def connect_to_game( self, gamelayout ):
        # Populate a Gridlayout G with level-thumbnail buttons.
        G = GridLayout( cols=3, 
                        spacing=20, 
                        padding=70, 
                        col_default_width=96+48+10, 
                        row_default_height=96+48+24+10 )

        # gamelayout.LEVELS is a list of level names.
        for suffix in gamelayout.LEVELS:
            G.add_widget( LevelButton( gamelayout, self.forward, suffix ) )

        self.add_widget( G )

        # Store a reference to the set of level thumbnails.
        self.level_buttons       = G

        # Set references to these items to know what levels have been completed by the user and what are her scores.
        self.get_unlocked_levels = gamelayout.get_unlocked_levels
        self.get_level_scores    = gamelayout.get_level_scores

    def load( self ):
        # 'load' is called when navigating to the level_selection screen. It keeps the level_selection screen updated with the user's progress.
        # Lock or Unlock all buttons so that their state reflects the current game completion state.
        current_state  = self.get_unlocked_levels()
        current_scores = self.get_level_scores()
        for b in self.level_buttons.children:
            b.unlock( True, None )

    def back_callback( self ):
        self.back()

    def get_back_texture( self ):
        return utils.load_texture( 'Resources/back.png' )
    def get_levels_texture( self ):
        return utils.load_texture( 'Resources/levels.png' )

