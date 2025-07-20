import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_steganography import VideoSteganography
import unittest

class TestVideoSteganography(unittest.TestCase):
    def setUp(self):
        self.test_video = "medias/test.avi"  # Ensure this file exists
        self.encoded_video = "medias/encoded.avi"
        self.message = "Secret Message"

    def test_encode_decode(self):
        VideoSteganography.encode(self.test_video, self.message, self.encoded_video)
        decoded_message = VideoSteganography.decode(self.encoded_video)
        self.assertEqual(self.message, decoded_message)

    def test_append_data(self):
        existing_message = "Existing Message"
        # First encode without appending
        VideoSteganography.encode(self.test_video, existing_message, self.encoded_video)
        # Append new message
        VideoSteganography.encode(self.encoded_video, self.message, self.encoded_video, append=True)
        decoded_message = VideoSteganography.decode(self.encoded_video)
        self.assertEqual(f"{existing_message}\n{self.message}", decoded_message)

    def test_replace_data(self):
        VideoSteganography.encode(self.test_video, self.message, self.encoded_video)
        # Replace message (default behavior)
        VideoSteganography.encode(self.encoded_video, self.message, self.encoded_video)
        decoded_message = VideoSteganography.decode(self.encoded_video)
        self.assertEqual(self.message, decoded_message)

    def tearDown(self):
        if os.path.exists(self.encoded_video):
            os.remove(self.encoded_video)

if __name__ == "__main__":
    unittest.main()