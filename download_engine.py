from format_model import YtdlpFormat
import os
import shutil
# import threading
import subprocess
from datetime import datetime
import time
import pathlib
import yt_dlp
from static_ffmpeg import run

class CancelledException( Exception ):
    pass

class DownloadEngine:
    def __init__( self ):
        self.cancel_requested = False
        self.current_subprocess = None

        self.temp_dir = os.path.join( os.path.dirname( __file__ ), "temp_workspace" )

    # Get FFMPEG location in virtual env
    @classmethod
    def GetFFMPEGPath( self ):
        # Get the path to the portable FFmpeg installed via pip
        ffmpeg_exe, _ = run.get_or_fetch_platform_executables_else_raise()
        return os.path.dirname( ffmpeg_exe )

    # Get User's Downloads folder
    @classmethod
    def GetDownloadsFolderPath( self ):
        downloads_path = pathlib.Path.home() / "Downloads"
        return downloads_path
    
    # Create temporary workspace for downloads
    def _CreateTempDir( self ):
        # checks if temp dir already exists and wipe it if it does
        if os.path.exists( self.temp_dir ):
            shutil.rmtree( self.temp_dir )
        # create new fresh temp dir
        os.makedirs( self.temp_dir, exist_ok=True )

    # Wipe temporary directory either after successful downloads or cancel
    def _CleanupTempDir( self ):
        if os.path.exists( self.temp_dir ):
            try:
                shutil.rmtree( self.temp_dir )
                print("[ENGINE] Temporary workspace wiped cleanly from drive.")
            except Exception as e:
                print(f"[ENGINE] Error cleaning temp directory: {e}")

    # Universal URL downloader logic
    def StartDownload( self, videoUrl, audioUrl = None, formatPreset = None, userOutputPath = None ):
        SUCCESS_STATUS = ""
        # Reset the cancel flag every time a new download starts
        self.cancel_requested = False
        self.current_subprocess = None
        # Get FFMPEG instance
        ffmpeg_dir = self.GetFFMPEGPath()
        ffmpeg_exe = os.path.join( ffmpeg_dir, "ffmpeg" )
        output_final_destination = os.path.normpath( userOutputPath )

        # Create temporary directory to use
        self._CreateTempDir()

        # Get equivalent yt-dlp format
        ytdlp_format = YtdlpFormat.get_ytdlp_format( formatPreset )

        # Define output file name
        temp_filename = "merged_output.mp4"
        output_filepath = pathlib.Path( temp_filename )
        # Creating timestamp to append to filename
        current_timestamp = datetime.now().strftime( "%Y%m%d_%H%M%S" )
        new_output_filename = f"{output_filepath.stem}_{current_timestamp}{output_filepath.suffix}"
        output_temp_filename = output_filepath.with_name( new_output_filename )

        # CASE 1: Two seperate URLS --> Merge into one video file
        if audioUrl:
            print(f"\n[ENGINE] Downloading & Merging separate Video and Audio links.")
            output_file = os.path.join( self.temp_dir, output_temp_filename )
            # Common desktop header to prevent basic server blocking
            headers = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n"
            
            cmd = [
                ffmpeg_exe, '-y',
                '-headers', headers, 
                '-i', videoUrl,
                '-headers', headers, 
                '-i', audioUrl,
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-c', 'copy', # Copy tracks directly without re-encoding
                output_file
            ]
            
            try:
                self.current_subprocess = subprocess.Popen( cmd )

                # Active polling loop checking for execution end or cancellation
                while self.current_subprocess.poll() is None:
                    if self.cancel_requested:
                        # kill process
                        self.current_subprocess.terminate()
                        print("[ENGINE] FFmpeg subprocess terminated via engine request.")
                        # wipe temp dir if cancelled
                        time.sleep( 0.5 )
                        self._CleanupTempDir()
                    time.sleep( 0.2 )
                
                # subprocess is done
                if self.current_subprocess.returncode == 0:
                    # move final file from temp location to final destination user chose
                    output_final_path = os.path.join( output_final_destination, output_temp_filename )
                    shutil.move( output_file, output_final_path )
                    print(f"\n[SUCCESS] Merged file saved to {output_final_path}")
                    SUCCESS_STATUS = "success"

                    # clean up temp dir after all done
                    self._CleanupTempDir()

                # cleanup even if failed naturally
                self._CleanupTempDir()

            except Exception as e:
                print(f"\n[ERROR] FFmpeg execution failed: {e}")
                SUCCESS_STATUS = "failed"
                # cleanup even if failed
                self._CleanupTempDir()

        # CASE 2: Standard URL or Singular combined m3u8 link
        else:
            print(f"\n[ENGINE] Processing via yt-dlp wrapper.")

            # inner function to trigger yt-dlp cancellation if running by triggering an exception
            def YtdlpHook( d ):
                if self.cancel_requested:
                    raise Exception( "Clicked Cancel." )

            output_file = os.path.join( self.temp_dir, "%(title)s.%(ext)s" )
            ydl_opts = {
                'format': ytdlp_format,
                'ffmpeg_location': ffmpeg_dir,      # Tells yt-dlp where our virtual env FFmpeg lives
                'outtmpl': output_file,
                'quiet': False,
                'progress_hooks': [ YtdlpHook ],
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': '*/*',
                }
            }

            # for audio only download
            # MP3 audio only
            if formatPreset == YtdlpFormat.OPTIONS[ 3 ]:
                print("[ENGINE] Audio extraction requested. Configuring postprocessors...")

                # Add yt-dlp options to get only audio and in mp3 format
                ydl_opts['postprocessors'] = [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192', # 192kbps / bitrate
                    },
                    {
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                    }
                ]

                # no need to merge into a single mp4 either
                ydl_opts['merge_output_format'] = None

            # FLAC Audio only
            elif formatPreset == YtdlpFormat.OPTIONS[ 4 ]:
                print("[ENGINE] Audio extraction requested. Configuring postprocessors...")

                # Add yt-dlp options to get only audio and in mp3 format
                ydl_opts['postprocessors'] = [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'flac',
                        'preferredquality': '0',
                    },
                    {
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                    }
                ]

                # no need to merge into a single mp4 either
                ydl_opts['merge_output_format'] = None

            # Video Download
            else:
                print(f"[ENGINE] Video download requested. Preset: {formatPreset}")

                # merge into single mkv if needed
                ydl_opts['merge_output_format'] = 'mkv'
            
            try:
                print(f"[ENGINE] Launching core downloader with format code: '{ytdlp_format}'")
                with yt_dlp.YoutubeDL( ydl_opts ) as ydl:
                    # Download video and extract metadata
                    ydl_info_dict = ydl.extract_info( videoUrl, download=True )
                    output_file = ydl.prepare_filename( ydl_info_dict )

                # Transfer files to user chosen final destination
                for file in os.listdir( self.temp_dir ):
                    output_file = os.path.join( output_final_destination, file )
                    shutil.move( os.path.join( self.temp_dir, file ), output_file )
                
                print(f"\n[SUCCESS] Download complete!\n[ENGINE]File path: {output_file}")
                print("[ENGINE] The extension may not be the right one. Check your file(s) at mentioned path above.")
                SUCCESS_STATUS = "success"

                # after done transferring, cleanup temp dir
                self._CleanupTempDir()

            except CancelledException:
                # cleanup
                self._CleanupTempDir()
                print(f"\n[ENGINE] yt-dlp download cancelled.")
            except Exception as e:
                print(f"\n[ERROR] yt-dlp download failed: {e}")
                SUCCESS_STATUS = "failed"
                # cleanup
                self._CleanupTempDir()

        # cleanup just in case
        self._CleanupTempDir()
        return SUCCESS_STATUS

    # Cancels all ongoing process called by Cancel Button of GUI
    def CancelProcess( self ):
        self.cancel_requested = True
        # Kill ffmpeg subprocess if running
        if self.current_subprocess and self.current_subprocess.poll() is None:
            self.current_subprocess.terminate()