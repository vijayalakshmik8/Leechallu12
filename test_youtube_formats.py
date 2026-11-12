import unittest
from types import SimpleNamespace

from youtube_formats import (
    NoCompatibleFormatError,
    available_video_heights,
    compatible_video_formats,
    extract_info_with_cookie_fallback,
    selected_video_height,
    supported_quality_heights,
    youtube_format_for_height,
)


def video(height, acodec="none", vcodec="avc1"):
    return {"height": height, "vcodec": vcodec, "acodec": acodec}


class YoutubeFormatTests(unittest.TestCase):
    def test_cookie_failure_retries_metadata_without_cookie_file(self):
        attempts = []

        class FakeYoutubeDL:
            def __init__(self, options):
                self.options = options

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def extract_info(self, url, download=False):
                attempts.append(self.options.get("cookiefile"))
                if self.options.get("cookiefile"):
                    raise ValueError("Invalid cookie file")
                return {"formats": [video(360)]}

        info, used_options = extract_info_with_cookie_fallback(
            SimpleNamespace(YoutubeDL=FakeYoutubeDL),
            "https://youtu.be/example",
            {"cookiefile": "cookies.txt"},
        )
        self.assertEqual(attempts, ["cookies.txt", None])
        self.assertNotIn("cookiefile", used_options)
        self.assertEqual(available_video_heights(info["formats"]), [360])

    def test_menu_heights_include_only_real_video_heights(self):
        formats = [video(360), video(360), video(1080), {"height": 720, "vcodec": "none", "acodec": "opus"}]
        self.assertEqual(available_video_heights(formats), [360, 1080])

    def test_menu_only_offers_requested_standard_heights_that_exist(self):
        formats = [video(144), video(240), video(432), video(576), video(720), video(1440), video(2160)]
        self.assertEqual(supported_quality_heights(formats), [144, 240, 576, 720, 1440, 2160])

    def test_720_request_excludes_higher_formats(self):
        formats = [video(480), video(720), video(1080), video(2160)]
        self.assertEqual([f["height"] for f in compatible_video_formats(formats, 720)], [480, 720])
        self.assertEqual(
            youtube_format_for_height(formats, 720),
            "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/"
            "bestvideo[height<=720]+bestaudio/best[height<=720]",
        )

    def test_only_lower_formats_are_compatible(self):
        formats = [video(360), video(480), video(1080)]
        self.assertEqual([f["height"] for f in compatible_video_formats(formats, 720)], [360, 480])
        selector = youtube_format_for_height(formats, 720)
        self.assertIn("height<=720", selector)
        self.assertNotIn("/best", selector.rsplit("/", 1)[-1])

    def test_no_compatible_format_has_clear_error(self):
        with self.assertRaisesRegex(NoCompatibleFormatError, "at or below 720p"):
            youtube_format_for_height([video(1080), video(2160)], 720)

    def test_progressive_format_is_height_limited(self):
        formats = [video(720, acodec="mp4a"), video(1080, acodec="mp4a")]
        selector = youtube_format_for_height(formats, 720, can_merge=False)
        self.assertEqual(selector, "best[height<=720]")
        self.assertEqual(selected_video_height({"requested_formats": [video(720), {"vcodec": "none"}]}), 720)

    def test_separate_streams_use_merge_selector_with_same_cap(self):
        formats = [video(720), {"vcodec": "none", "acodec": "opus"}, video(1080)]
        self.assertEqual(
            youtube_format_for_height(formats, 720),
            "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/"
            "bestvideo[height<=720]+bestaudio/best[height<=720]",
        )

    def test_no_merge_path_errors_without_capped_progressive_format(self):
        formats = [video(720), {"vcodec": "none", "acodec": "opus"}]
        with self.assertRaisesRegex(NoCompatibleFormatError, "FFmpeg is unavailable"):
            youtube_format_for_height(formats, 720, can_merge=False)


if __name__ == "__main__":
    unittest.main()
