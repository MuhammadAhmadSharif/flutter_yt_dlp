import yt_dlp
import json
import os
import logging
from io import StringIO

# Configure logging with DEBUG level for detailed output and ensure output goes to stderr
# for Flutter to capture it in release mode
logging.basicConfig(
    level=logging.DEBUG,
    format='[yt_dlp_helper] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]  # Explicitly add stderr handler
)
logger = logging.getLogger(__name__)

class LogCapture(StringIO):
    """Captures yt-dlp output for logging."""
    def write(self, message):
        if message.strip():
            logger.debug(f"yt-dlp output: {message.strip()}")

def extract_format_info(format_data):
    """Extracts format info from yt-dlp data."""
    return {
        "formatId": format_data.get("format_id", "unknown"),
        "ext": format_data.get("ext", "unknown"),
        "resolution": (
            format_data.get("resolution", "unknown")
            if format_data.get("vcodec", "none") != "none"
            else "audio only"
        ),
        "bitrate": int(format_data.get("tbr", 0) or 0),
        "size": int(
            format_data.get("filesize", 0) or format_data.get("filesize_approx", 0) or 0
        ),
        "vcodec": format_data.get("vcodec", "none"),
        "acodec": format_data.get("acodec", "none"),
    }

def get_video_info(url):
    """Fetches video metadata and formats."""
    ydl_opts = {
        "quiet": True,
        "format": "bestvideo+bestaudio/best",
        "logger": logger,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_info = {
                "title": info.get("title", "unknown_video"),
                "thumbnail": info.get("thumbnail"),
                "formats": [extract_format_info(f) for f in info.get("formats", [])],
            }
            logger.info(f"Fetched info for {url}: {len(video_info['formats'])} formats")
            return json.dumps(video_info)
    except Exception as e:
        logger.error(f"Error fetching info for {url}: {str(e)}")
        return json.dumps({"title": "unknown_video", "thumbnail": None, "formats": []})

def download_format(url, format_id, output_path, overwrite, progress_callback):
    """Downloads a specific format with progress updates."""
    log_capture = LogCapture()

    def progress_hook(d):
        status = d.get("status")
        if status == "downloading":
            downloaded = int(d.get("downloaded_bytes", 0))
            total = int(d.get("total_bytes", d.get("total_bytes_estimate", 0) or 0))
            if total > 0:
                logger.info(f"Progress for {url}: {downloaded}/{total} bytes")
                # Use a more direct approach - first try to find a method with a name pattern that would match
                # progress reporting in Flutter (release mode often uses one or two-letter method names)
                callback_called = False
                
                # Try all available methods first - this will catch obfuscated methods
                for method_name in dir(progress_callback):
                    if (not method_name.startswith('__') and  # Skip built-ins
                        callable(getattr(progress_callback, method_name, None))):
                        try:
                            logger.debug(f"Trying method: {method_name}")
                            getattr(progress_callback, method_name)(downloaded, total)
                            logger.info(f"Called method: {method_name} with {downloaded}/{total}")
                            callback_called = True
                            break
                        except Exception as e:
                            logger.debug(f"Method {method_name} failed: {str(e)}")
                            continue
                
                # If no method call worked, try directly calling the object
                if not callback_called:
                    try:
                        # Try calling the object directly if it's callable
                        progress_callback(downloaded, total)
                        logger.info(f"Called progress_callback directly with {downloaded}/{total}")
                        callback_called = True
                    except Exception as e:
                        logger.error(f"Direct call failed: {str(e)}")
                
                # If nothing worked, try the original method name
                if not callback_called:
                    try:
                        progress_callback.onProgress(downloaded, total)
                        logger.info(f"Called onProgress with {downloaded}/{total}")
                    except Exception as e:
                        logger.error(f"onProgress call failed: {str(e)}")
                        
        elif status == "finished":
            total = int(d.get("total_bytes", d.get("total_bytes_estimate", 0) or 0))
            logger.info(f"Download finished for {url}: {total} bytes")
            
            # Use the same approach for finished status
            callback_called = False
            
            # Try all methods first
            for method_name in dir(progress_callback):
                if (not method_name.startswith('__') and
                    callable(getattr(progress_callback, method_name, None))):
                    try:
                        getattr(progress_callback, method_name)(total, total)
                        logger.info(f"Finished: Called method {method_name} with {total}/{total}")
                        callback_called = True
                        break
                    except Exception:
                        continue
            
            # Try direct call
            if not callback_called:
                try:
                    progress_callback(total, total)
                    logger.info(f"Finished: Called progress_callback directly with {total}/{total}")
                    callback_called = True
                except Exception as e:
                    logger.error(f"Finished: Direct call failed: {str(e)}")
            
            # Try original method
            if not callback_called:
                try:
                    progress_callback.onProgress(total, total)
                    logger.info(f"Finished: Called onProgress with {total}/{total}")
                except Exception as e:
                    logger.error(f"Finished: onProgress call failed: {str(e)}")
                    
        elif status == "error":
            logger.error(f"Download error for {url}: {d.get('error')}")

    # Set up a more detailed logger for release mode
    logger.info(f"Setting up download for {url} with format {format_id}")
    logger.info(f"Progress callback type: {type(progress_callback).__name__}")
    logger.info(f"Available methods: {[m for m in dir(progress_callback) if not m.startswith('__') and callable(getattr(progress_callback, m, None))]}")
    
    ydl_opts = {
        "format": format_id,
        "outtmpl": output_path,
        "progress_hooks": [progress_hook],
        "force_overwrites": overwrite,
        "noprogress": False,
        "quiet": False,  # Allow yt-dlp output for debugging
        "logger": logger,
        "verbose": True,  # Enable verbose output for debugging
        "logtostderr": True,  # Ensure logs go to stderr
        "errfile": log_capture,  # Capture errors
        "outfile": log_capture,  # Capture output
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Starting download: {url} format {format_id} to {output_path}")
            ydl.download([url])
            logger.info(f"Download completed for {url}")
    except Exception as e:
        logger.error(f"Download failed for {url}: {str(e)}")
        raise