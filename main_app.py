from gui import DownloaderApp
import sys
import io
import os
import multiprocessing

# Fix the --noconsole stream crashes
if sys.stdout is None or isinstance(sys.stdout, io.StringIO) is False:
    sys.stdout = io.StringIO()
if sys.stderr is None or isinstance(sys.stderr, io.StringIO) is False:
    sys.stderr = io.StringIO()

def main():
    app = DownloaderApp()
    app.mainloop()

# FORCE static-ffmpeg paths into the OS Environment Context
def check_ffmpeg_path():
    try:
        import static_ffmpeg
        # This locates or caches the internal binaries
        static_ffmpeg.add_paths() 
        
        # Pull the exact binary directory paths from static-ffmpeg
        from static_ffmpeg import run
        ffmpeg_dir = run.get_platform_executable_directory()
        
        if ffmpeg_dir and os.path.exists( ffmpeg_dir ):
            # Inject it into the current running process's PATH variables
            # yt-dlp will now immediately see ffmpeg without checking the Windows registry
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    except Exception as e:
        pass # Fallback gracefully if paths aren't initialized yet

if __name__ == "__main__":
    multiprocessing.freeze_support()
    check_ffmpeg_path()
    main()