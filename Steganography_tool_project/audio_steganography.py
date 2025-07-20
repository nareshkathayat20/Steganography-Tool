import os
import wave
import struct
import tempfile
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from pydub import AudioSegment


class AudioSteganography:
    @staticmethod
    def encrypt_message(key: str, message: str) -> str:
        cipher = AES.new(key.encode(), AES.MODE_ECB)
        encrypted_msg = cipher.encrypt(pad(message.encode(), AES.block_size))
        return base64.b64encode(encrypted_msg).decode()

    @staticmethod
    def decrypt_message(key: str, encrypted_msg: str) -> str:
        cipher = AES.new(key.encode(), AES.MODE_ECB)
        decrypted_msg = unpad(cipher.decrypt(base64.b64decode(encrypted_msg)), AES.block_size)
        return decrypted_msg.decode()

    @staticmethod
    def encode(audio_path: str, message: str, output_path: str, key: str = None) -> None:
        # Optional encryption
        if key:
            message = AudioSteganography.encrypt_message(key, message)

        # Append null-terminator and convert to binary
        binary_msg = ''.join(format(ord(c), '08b') for c in message) + '00000000'

        # Handle MP3 input
        is_mp3 = audio_path.lower().endswith('.mp3')
        temp_wav = None

        if is_mp3:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                temp_wav = tmp.name
            audio = AudioSegment.from_mp3(audio_path)
            audio.export(temp_wav, format="wav")
            audio_path = temp_wav

        try:
            # Open WAV file
            with wave.open(audio_path, 'rb') as audio:
                params = audio.getparams()
                frames = bytearray(audio.readframes(audio.getnframes()))

            if len(binary_msg) > len(frames):
                raise ValueError("Message too large for the audio.")

            # Embed message
            for i in range(len(binary_msg)):
                frames[i] = (frames[i] & ~1) | int(binary_msg[i])

            # Save encoded file
            with wave.open(output_path, 'wb') as encoded_audio:
                encoded_audio.setparams(params)
                encoded_audio.writeframes(frames)

        finally:
            # Clean up temporary WAV file
            if is_mp3 and temp_wav and os.path.exists(temp_wav):
                os.remove(temp_wav)

    @staticmethod
    def decode(audio_path: str, key: str = None) -> str:
        # Handle MP3 input
        is_mp3 = audio_path.lower().endswith('.mp3')
        temp_wav = None

        if is_mp3:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                temp_wav = tmp.name
            audio = AudioSegment.from_mp3(audio_path)
            audio.export(temp_wav, format="wav")
            audio_path = temp_wav

        try:
            with wave.open(audio_path, 'rb') as audio:
                frames = audio.readframes(audio.getnframes())

            binary_msg = ''.join(str(byte & 1) for byte in frames)
            message = ""
            for i in range(0, len(binary_msg), 8):
                byte = binary_msg[i:i+8]
                if byte == '00000000':
                    break
                message += chr(int(byte, 2))

            if key:
                message = AudioSteganography.decrypt_message(key, message)

            return message

        finally:
            # Clean up temporary WAV file
            if is_mp3 and temp_wav and os.path.exists(temp_wav):
                os.remove(temp_wav)
