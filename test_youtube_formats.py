import unittest

from youtube_formats import (
    NoCompatibleFormatError,
    compatible_video_formats,
    selected_video_height,
    youtube_format_for_height,
)


def video(height, acodec="none", vcodec="avc1"):
    return {"height": height, "vcodec": vcodec, "acodec": acodec}


class YoutubeFormatTests(unittest.TestCase):
    def test_720_request_excludes_higher_formats(self):
        formats = [video(480), video(720), video(1080), video(2160)]
        self.assertEqual([f["height"] for f in compatible_video_formats(formats, 720)], [480, 720])
        self.assertEqual(
            youtube_format_for_height(formats, 720),
            "bestvideo[height<=720]+bestaudio/best[height<=720]",
        )

    def test_only_lower_formats_are_compatible(self):
        formats = [video(360), video(480), video(1080)]
        self.assertEqual([f["height"] for f in compatible_video_formats(formats, 720)], [360, 480])
        self.assertIn("height<=720", youtube_format_for_height(formats, 720))

    def test_no_compatible_format_has_clear_error(self):
        with self.assertRaisesRegex(NoCompatibleFormatError, "at or below 720p"):
            youtube_format_for_height([video(1080), video(2160)], 720)

    def test_progressive_format_is_height_limited(self):
        formats = [video(720, acodec="mp4a"), video(1080, acodec="mp4a")]
        selector = youtube_format_for_height(formats, 720)
        self.assertTrue(selector.endswith("/best[height<=720]"))
        self.assertEqual(selected_video_height({"requested_formats": [video(720), {"vcodec": "none"}]}), 720)

    def test_separate_streams_use_merge_selector_with_same_cap(self):
        formats = [video(720), {"vcodec": "none", "acodec": "opus"}, video(1080)]
        self.assertEqual(
            youtube_format_for_height(formats, 720),
            "bestvideo[height<=720]+bestaudio/best[height<=720]",
        )


if __name__ == "__main__":
    unittest.main()
