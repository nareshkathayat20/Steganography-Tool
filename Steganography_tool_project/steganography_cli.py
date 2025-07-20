import os
from image_steganography import ImageSteganography
from audio_steganography import AudioSteganography
from video_steganography import VideoSteganography

def main():
    while True:
        print("\n Choose the option of your Steganography:")
        print("1. If you want Image Steganography")
        print("2. If you want  Audio Steganography")
        print("3. If you want Video Steganography")
        print("4. If you want Batch Processing")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            handle_image_stego()
        elif choice == '2':
            handle_audio_stego()
        elif choice == '3':
            handle_video_stego()
        elif choice == '4':
            handle_batch_processing()
        elif choice == '5':
            print("Exiting the program...")
            break
        else:
            print("Invalid choice. Please select between 1 and 5.")

def handle_image_stego():
    print("\nImage Steganography")
    print("1. Encode")
    print("2. Decode")
    action = input("Choose an action (1 or 2): ")

    if action == '1':
        input_file = input("Enter input image file path: ")
        output_file = input("Enter output image file path: ")
        message = input("Enter the message to encode: ")
        key = input("Enter encryption key (optional, 16/24/32 characters): ")

        '''while key and len(key) not in [16, 24, 32]:
            print("Error: AES key must be 16, 24, or 32 characters long.")
            key = input("Enter a valid encryption key: ")'''

        ImageSteganography.encode(input_file, message, output_file, key)
        print(f"Message encoded successfully in {output_file}")
    
    elif action == '2':
        input_file = input("Enter input image file path: ")
        key = input("Enter decryption key (optional): ")
        decoded_message = ImageSteganography.decode(input_file, key)
        print(f"Decoded message: {decoded_message}")

def handle_audio_stego():
    print("\nAudio Steganography")
    print("1. Encode")
    print("2. Decode")
    action = input("Choose an action (1 or 2): ")

    if action == '1':
        input_file = input("Enter input audio file path: ")
        output_file = input("Enter output audio file path: ")
        message = input("Enter the message to encode: ")
        key = input("Enter encryption key (optional): ")
        AudioSteganography.encode(input_file, message, output_file, key)
        print(f"Message encoded successfully in {output_file}")

    elif action == '2':
        input_file = input("Enter input audio file path: ")
        key = input("Enter decryption key (optional): ")
        decoded_message = AudioSteganography.decode(input_file, key)
        print(f"Decoded message: {decoded_message}")

def handle_video_stego():
    print("\nVideo Steganography")
    print("1. Encode")
    print("2. Decode")
    action = input("Choose an action (1 or 2): ")

    if action == '1':
        input_file = input("Enter input video file path: ")
        output_file = input("Enter output video file path: ")
        message = input("Enter the message to encode: ")
        key = input("Enter encryption key (optional): ")
        VideoSteganography.encode(input_file, message, output_file, key)
        print(f"Message encoded successfully in {output_file}")

    elif action == '2':
        input_file = input("Enter input video file path: ")
        key = input("Enter decryption key (optional): ")
        decoded_message = VideoSteganography.decode(input_file, key)
        print(f"Decoded message: {decoded_message}")

def handle_batch_processing():
    print("\nBatch Processing")
    print("1. Encode")
    print("2. Decode")
    action = input("Choose an action (1 or 2): ")

    if action == '1':
        input_files = input("Enter input file paths (comma-separated): ").split(',')
        output_files = input("Enter output file paths (comma-separated): ").split(',')
        message = input("Enter the message to encode: ")
        key = input("Enter encryption key (optional): ")

        for input_file, output_file in zip(input_files, output_files):
            if input_file.endswith(('.png', '.bmp', '.jpg', '.jpeg')):
                ImageSteganography.encode(input_file, message, output_file, key)
            elif input_file.endswith(('.wav', '.mp3')):
                AudioSteganography.encode(input_file, message, output_file, key)
            elif input_file.endswith(('.avi', '.mp4')):
                VideoSteganography.encode(input_file, message, output_file, key)
            print(f"Message encoded successfully in {output_file}")

    elif action == '2':
        input_files = input("Enter input file paths (comma-separated): ").split(',')
        key = input("Enter decryption key (optional): ")

        for input_file in input_files:
            if input_file.endswith(('.png', '.bmp', '.jpg', '.jpeg')):
                decoded_message = ImageSteganography.decode(input_file, key)
            elif input_file.endswith(('.wav', '.mp3')):
                decoded_message = AudioSteganography.decode(input_file, key)
            elif input_file.endswith(('.avi', '.mp4')):
                decoded_message = VideoSteganography.decode(input_file, key)
            print(f"Decoded message from {input_file}: {decoded_message}")

if __name__ == "__main__":
    main()
