"""Helpers for choosing YouTube formats without exceeding a requested height."""


class NoCompatibleFormatError(ValueError):
    """Raised when a requested maximum height has no playable video format."""


def compatible_video_formats(formats, max_height):
    return [
        fmt for fmt in formats
        if fmt.get("height") and fmt.get("height") <= max_height
        and fmt.get("vcodec") not in (None, "none")
    ]


def available_video_heights(formats):
    """Return actual video heights for building a menu without phantom tiers."""
    return sorted({
        fmt["height"] for fmt in formats
        if fmt.get("height") and fmt.get("vcodec") not in (None, "none")
    })


def youtube_format_for_height(formats, max_height, can_merge=True):
    """Build an ordered yt-dlp selector; every video branch obeys the cap."""
    videos = compatible_video_formats(formats, max_height)
    if not videos:
        raise NoCompatibleFormatError(
            f"No video format is available at or below {max_height}p."
        )

    progressive = [fmt for fmt in videos if fmt.get("acodec") not in (None, "none")]
    if not can_merge:
        if not progressive:
            raise NoCompatibleFormatError(
                f"No progressive video is available at or below {max_height}p, "
                "and separate streams cannot be merged because FFmpeg is unavailable."
            )
        return f"best[height<={max_height}]"

    # Follow ytdlbot's MP4/M4A-first strategy, then relax codec/container
    # preferences while retaining the requested ceiling, and finally try a
    # progressive (video+audio) format under that same ceiling.
    return (
        f"bestvideo[ext=mp4][height<={max_height}]+bestaudio[ext=m4a]/"
        f"bestvideo[height<={max_height}]+bestaudio/"
        f"best[height<={max_height}]"
    )


def selected_video_height(info):
    """Return the downloaded video's height, including merged format metadata."""
    requested = info.get("requested_formats") or []
    heights = [f.get("height") for f in requested if f.get("vcodec") not in (None, "none")]
    if heights:
        return max(heights)
    return info.get("height")
