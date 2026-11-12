"""Helpers for choosing YouTube formats without exceeding a requested height."""


class NoCompatibleFormatError(ValueError):
    """Raised when a requested maximum height has no playable video format."""


def compatible_video_formats(formats, max_height):
    return [
        fmt for fmt in formats
        if fmt.get("height") and fmt.get("height") <= max_height
        and fmt.get("vcodec") not in (None, "none")
    ]


def youtube_format_for_height(formats, max_height):
    """Build yt-dlp's best muxed-or-merged selector under a strict height cap."""
    if not compatible_video_formats(formats, max_height):
        raise NoCompatibleFormatError(
            f"No video format is available at or below {max_height}p."
        )
    # Prefer bestvideo+bestaudio. The fallback is progressive (audio+video) and
    # retains the same ceiling; there is deliberately no unrestricted fallback.
    return f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]"


def selected_video_height(info):
    """Return the downloaded video's height, including merged format metadata."""
    requested = info.get("requested_formats") or []
    heights = [f.get("height") for f in requested if f.get("vcodec") not in (None, "none")]
    if heights:
        return max(heights)
    return info.get("height")
