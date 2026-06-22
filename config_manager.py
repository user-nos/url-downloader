import os
import json
from download_engine import DownloadEngine
from format_model import YtdlpFormat

# Define Config manager class to handle all configs related things
class ConfigManager:
    def __init__( self, logCallback ):
        self.log_callback = logCallback

        # Set path for saving config path: ./config/config.json
        self.config_dir = os.path.join( os.path.dirname( __file__ ), "config" )
        self.config_file = os.path.join( self.config_dir, "config.json" )

        # Define defaults for configs
        self.defaults = {
            "theme": "Dark",
            "color_theme": "dark-blue",
            "save_path": DownloadEngine.GetDownloadsFolderPath(),
            "preferred_ytdlpformat": YtdlpFormat.OPTIONS[ 0 ],
            "open_folder_on_completion": False
        }

        # Activate configs to be held in app RAM
        self.configs = self.load_config()

    # Read configs or create default file
    def load_config( self ):
        # create config file if it does not exist yet
        if not os.path.exists( self.config_file ):
            self._save_to_disk( self.defaults )
            return self.defaults.copy()
        
        # read config from file
        try:
            with open( self.config_file, "r" ) as f:
                loaded_configs = json.load( f )

            # Merge with defaults to ensure no crashed if some values missing
            merged_configs = self.defaults.copy()
            merged_configs.update( loaded_configs )
            return merged_configs
        
        except ( json.JSONDecodeError, IOError ) as e:
            self.log_callback( f"[CONFIG] File corrupted or unreadable. Resetting to defaults. Error: {e}" )
            return self.defaults.copy()
        
    # Update a config setting
    def set_config( self, key, value ):
        if key in self.defaults:
            self.configs[ key ] = value
            self._save_to_disk( self.configs )

        self.configs = self.load_config()

    # Get a config value
    def get_config( self, key ):
        if key in self.defaults:
            return self.configs[ key ]
        else:
            self.log_callback( "[CONFIG] Config key does not exist." )
            return ""

    # Update several configs at once
    def save_configs( self, selected_theme, selected_colortheme, selected_path, selected_ytdlpformat, selected_openfolder_value ):
        self.configs[ "theme" ] = selected_theme
        self.configs[ "color_theme" ] = selected_colortheme
        self.configs[ "save_path" ] = selected_path
        self.configs[ "preferred_ytdlpformat" ] = selected_ytdlpformat
        self.configs[ "open_folder_on_completion" ] = selected_openfolder_value
        self._save_to_disk( self.configs )
        self.configs = self.load_config()

    # Create file on disk or update contents of file
    def _save_to_disk( self, configs_dict ):
        try:
            os.makedirs( self.config_dir, exist_ok=True )
            with open( self.config_file, "w" ) as f:
                json.dump( configs_dict, f, default=str, indent=4 )
            
            self.log_callback( "[CONFIG] Configurations saved." )
        except IOError as e:
            self.log_callback( f"[ERROR] Failed to write config modifications to storage device: {e}" )