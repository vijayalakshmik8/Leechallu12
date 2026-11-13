"""Helpers for choosing YouTube formats without exceeding a requested height."""


class NoCompatibleFormatError(ValueError):
    """Raised when a requested maximum height has no playable video format."""


SUPPORTED_VIDEO_HEIGHTS = (144, 240, 360, 480, 576, 720, 1080, 1440, 2160)


def extract_info_with_cookie_fallback(yt_dlp_module, url, options, download=False):
    """Retry metadata/download once without a cookie file if cookie auth fails."""
    try:
        with yt_dlp_module.YoutubeDL(options) as ydl:
            return ydl.extract_info(url, download=download), dict(options)
    except Exception:
        if not options.get("cookiefile"):
            raise

    public_options = dict(options)
    public_options.pop("cookiefile", None)
    with yt_dlp_module.YoutubeDL(public_options) as ydl:
        return ydl.extract_info(url, download=download), public_options


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



def _format_size_bytes(fmt, duration):
    """Return exact/estimated bytes for one yt-dlp format, or None."""
    if fmt.get("filesize") is not None:
        return int(fmt["filesize"]), True
    if fmt.get("filesize_approx") is not None:
        return int(fmt["filesize_approx"]), False
    tbr = fmt.get("tbr")
    if tbr and duration:
        return int(float(tbr) * 1000 * float(duration) / 8), False
    return None


def estimate_quality_size(formats, max_height, duration=None, can_merge=True):
    """Estimate the size selected by our height-capped video/audio selector.

    Exact source `filesize` values are preferred. If YouTube only exposes an
    approximate size or bitrate, the returned exact flag is False.
    """
    videos = compatible_video_formats(formats, max_height)
    if not videos:
        return None, False

    # Without FFmpeg, the downloader is restricted to a progressive format.
    if not can_merge:
        progressive = [f for f in videos if f.get("acodec") not in (None, "none")]
        if not progressive:
            return None, False
        return _format_size_bytes(progressive[-1], duration) or (None, False)

    # Match the selector's MP4/M4A preference, then its unrestricted fallback.
    mp4_videos = [f for f in videos if f.get("ext") == "mp4"]
    m4a_audios = [f for f in formats if f.get("vcodec") in (None, "none")
                  and f.get("acodec") not in (None, "none") and f.get("ext") == "m4a"]
    any_audios = [f for f in formats if f.get("vcodec") in (None, "none")
                  and f.get("acodec") not in (None, "none")]

    chosen_video = (mp4_videos or videos)[-1]
    chosen_audio = (m4a_audios or any_audios)
    if chosen_audio:
        chosen_audio = chosen_audio[-1]
        video_size = _format_size_bytes(chosen_video, duration)
        audio_size = _format_size_bytes(chosen_audio, duration)
        if video_size and audio_size:
            return video_size[0] + audio_size[0], video_size[1] and audio_size[1]
        if video_size and audio_size is None:
            return video_size[0], False
        if audio_size and video_size is None:
            return audio_size[0], False
        return None, False

    # Progressive video+audio fallback: choose the best compatible format
    # carrying both streams, as the final /best[height<=...] selector does.
    progressive = [f for f in videos if f.get("acodec") not in (None, "none")]
    if progressive:
        return _format_size_bytes(progressive[-1], duration) or (None, False)
    return None, False


def selected_video_height(info):
    """Return the downloaded video's height, including merged format metadata."""
    requested = info.get("requested_formats") or []
    heights = [f.get("height") for f in requested if f.get("vcodec") not in (None, "none")]
    if heights:
        return max(heights)
    return info.get("height")


def supported_quality_heights(formats):
    """Return only requested standard resolutions present in source formats."""
    available = set(available_video_heights(formats))
    return [height for height in SUPPORTED_VIDEO_HEIGHTS if height in available]
