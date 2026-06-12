# Define options for yt-dlp accepted formats
class YtdlpFormat:
    # static list for gui dropdown list
    OPTIONS = [
        "Best Quality",
        "1080p",
        "720p",
        "MP3 Audio only",
        "FLAC Audio only"
    ]

    # private map as to know with value = which format
    _FORMAT_MAP = {
        "Best Quality": "bestvideo+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best",
        "720p": "bestvideo[height<=720]+bestaudio/best",
        "MP3 Audio only": "bestaudio/best",
        "FLAC Audio only": "bestaudio/best"
    }

    # Get mapping value from displayed value
    @classmethod
    def get_ytdlp_format( cls, dropdown_item ):
        return cls._FORMAT_MAP.get( dropdown_item, "bestvideo+bestaudio/best" )