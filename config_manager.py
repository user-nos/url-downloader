import os
import json
from download_engine import DownloadEngine
from format_model import YtdlpFormat

# Define Config manager class to handle all configs related things
class ConfigManager:
    def __init__( self ):
        # Set path for saving config path: ./config/config.json
        self.config_dir = os.path.join( os.path.dirname( __file__ ), "config" )
        self.config_file = os.path.join( self.config_dir, "config.json" )

        # Define defaults for configs
        self.defaults = {
            "theme": "System",
            "save_path": DownloadEngine.GetDownloadsFolderPath(),
            "preferred_mainformat": YtdlpFormat.OPTIONS[ 0 ],
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
            print( f"[CONFIG] File corrupted or unreadable. Resetting to defaults. Error: {e}" )
            return self.defaults.copy()
        
    # Update a config setting
    def set_value( self, key, value ):
        if key in self.defaults:
            self.configs[ key ] = value
            self._save_to_disk( self.configs )

    # Create file on disk or update contents of file
    def _save_to_disk( self, configs_dict ):
        try:
            os.makedirs( self.config_dir, exist_ok=True )
            with open( self.config_file, "w" ) as f:
                json.dump( configs_dict, f, indent=4 )
            
        except IOError as e:
            print( f"[ERROR] Failed to write config modifications to storage device: {e}" )