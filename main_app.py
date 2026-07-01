from gui import DownloaderApp
import sys
import io
import multiprocessing

# Fix the --noconsole stream crashes
if sys.stdout is None or isinstance(sys.stdout, io.StringIO) is False:
    sys.stdout = io.StringIO()
if sys.stderr is None or isinstance(sys.stderr, io.StringIO) is False:
    sys.stderr = io.StringIO()

def main():
    multiprocessing.freeze_support()
    app = DownloaderApp()
    app.mainloop()

if __name__ == "__main__":
    main()