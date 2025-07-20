import os
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

class ImageSteganography:
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
    def encode(image_path: str, message: str, output_path: str, key: str = None) -> None:
        """Encodes a secret message into an image using LSB steganography."""
        if not os.path.exists(image_path):
            raise FileNotFoundError("Error: Input image file does not exist.")

        img = Image.open(image_path)
        if key:
            message = ImageSteganography.encrypt_message(key, message)

               # Convert message to binary
        binary_msg = ''.join(format(ord(c), '08b') for c in message) + '00000000'  # Null terminator
        pixels = list(img.getdata())
        width, height = img.size

        if len(binary_msg) > width * height * 3:
            raise ValueError("Message too large for the image.")

        idx = 0
        for i in range(len(pixels)):
            pixel = list(pixels[i])
            for j in range(3):  # RGB channels
                if idx < len(binary_msg):
                    pixel[j] = (pixel[j] & ~1) | int(binary_msg[idx])
                    idx += 1
            pixels[i] = tuple(pixel)

        encoded_img = Image.new(img.mode, img.size)
        encoded_img.putdata(pixels)
        encoded_img.save(output_path)
        print(f"Message successfully encoded into {output_path}")

    @staticmethod
    def decode(image_path: str, key: str = None) -> str:
        """Decodes a secret message from an image using LSB steganography."""
        img = Image.open(image_path)
        pixels = list(img.getdata())
        binary_msg = ""
        for pixel in pixels:
            for value in pixel[:3]:  # RGB channels
                binary_msg += str(value & 1)

        # Extract message up to null terminator
        message = ""
        for i in range(0, len(binary_msg), 8):
            byte = binary_msg[i:i+8]
            if byte == '00000000':
                break
            message += chr(int(byte, 2))

        if key:
            message = ImageSteganography.decrypt_message(key, message)
        print(f"Message successfully decoded ")
        return message
