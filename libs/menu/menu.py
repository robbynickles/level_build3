from kivy.uix.gridlayout import GridLayout

from kivy.lang import Builder
Builder.load_file( 'libs/menu/menu.kv' )

class Menu(GridLayout):

    def __init__(self, play_game, *args, **kwargs):
        super(type(self), self).__init__( *args, **kwargs )
        self.play_game = play_game

    def play_callback( self ):
        self.play_game()
