import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import pygame
import cv2
from image_steganography import ImageSteganography
from audio_steganography import AudioSteganography
from video_steganography import VideoSteganography

class SteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SecureStego - Steganography Tool")
        self.root.geometry("700x600")

        # Initialize pygame mixer and video variables
        pygame.mixer.init()
        self.video_cap = None
        self.video_thread = None
        self.stop_video = threading.Event()

        self.setup_ui()
        self.setup_menu()
        self.current_file = None
        self.preview_image = None
        self.dark_mode = False

    def setup_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        # Theme menu
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        menu_bar.add_cascade(label="Theme", menu=theme_menu)
        
        self.root.config(menu=menu_bar)

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Media type selection
        media_frame = ttk.LabelFrame(main_frame, text="Select Media Type")
        media_frame.pack(fill=tk.X, pady=5)
        
        self.media_type = tk.StringVar(value="Image")
        media_options = ["Image", "Audio", "Video"]
        for option in media_options:
            ttk.Radiobutton(media_frame, text=option, variable=self.media_type,
                           value=option, command=self.update_ui).pack(side=tk.LEFT, padx=5)

        # Preview area
        self.preview_frame = ttk.LabelFrame(main_frame, text="Preview")
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(expand=True)

        # Audio control buttons for audio preview
        self.audio_controls_frame = ttk.Frame(self.preview_frame)
        self.audio_controls_frame.pack(pady=5)
        self.play_audio_btn = ttk.Button(self.audio_controls_frame, text="Play Audio", command=self.play_audio)
        self.pause_audio_btn = ttk.Button(self.audio_controls_frame, text="Pause Audio", command=self.pause_audio)
        self.play_audio_btn.pack(side=tk.LEFT, padx=5)
        self.pause_audio_btn.pack(side=tk.LEFT, padx=5)
        self.audio_controls_frame.pack_forget()  # Hide initially

        # Message input
        msg_frame = ttk.LabelFrame(main_frame, text="Secret Message")
        msg_frame.pack(fill=tk.X, pady=5)
        
        self.message_entry = scrolledtext.ScrolledText(msg_frame, height=4, wrap=tk.WORD)
        self.message_entry.pack(fill=tk.X, padx=5, pady=5)
        
        '''ttk.Button(msg_frame, text="Load Message from File", 
                  command=self.load_message_from_file).pack(side=tk.LEFT, pady=5)'''
        ttk.Button(msg_frame, text="Clear Message", 
                  command=lambda: self.message_entry.delete(1.0, tk.END)).pack(side=tk.RIGHT, pady=5)

        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Encode", command=self.encode, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Decode", command=self.decode, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side=tk.RIGHT)

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure styles
        self.root.style = ttk.Style()
        self.root.style.configure("Accent.TButton", font=('Helvetica', 10, 'bold'))
        self.root.style.map("Accent.TButton",
                          foreground=[('active', 'white'), ('!active', 'black')],
                          background=[('active', '#347083'), ('!active', '#4595b4')])

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg_color = "#2E2E2E" if self.dark_mode else "white"
        fg_color = "white" if self.dark_mode else "black"
        self.root.configure(bg=bg_color)
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=bg_color, fg=fg_color)
            except:
                pass

    def update_ui(self):
        self.clear_preview()
        self.status_bar.config(text=f"Selected media type: {self.media_type.get()}")

    def open_file(self):
        self.stop_all_media()  # Stop any playing audio/video

        media_type = self.media_type.get()
        filetypes = self.get_file_types(media_type)
        self.current_file = filedialog.askopenfilename(filetypes=filetypes)
        if self.current_file:
            self.show_preview(self.current_file)
            self.status_bar.config(text=f"Loaded: {self.current_file}")

    def save_file(self):
        media_type = self.media_type.get()
        filetypes = self.get_file_types(media_type)
        filename = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=filetypes[0][1])
        return filename

    def get_file_types(self, media_type):
        return {
            "Image": [("Image files", "*.png *.bmp *.jpg *.jpeg")],
            "Audio": [("Audio files", "*.wav *.mp3")],
            "Video": [("Video files", "*.avi *.mp4 *.mkv *.mov")]
        }.get(media_type, [("All files", "*.*")])

    def show_preview(self, file_path):
        media_type = self.media_type.get()
        try:
            if media_type == "Image":
                self.audio_controls_frame.pack_forget()
                if self.video_thread and self.video_thread.is_alive():
                    self.stop_video.set()
                    self.video_thread.join()
                    self.video_cap.release()
                    self.video_thread = None

                img = Image.open(file_path)
                img.thumbnail((400, 400))
                self.preview_image = ImageTk.PhotoImage(img)
                self.preview_label.config(image=self.preview_image, text="")
                self.preview_label.image = self.preview_image

            elif media_type == "Audio":
                # Show audio controls
                self.audio_controls_frame.pack(pady=5)
                self.preview_label.config(image='', text=f"Audio File: {os.path.basename(file_path)}")
                self.play_audio()

            elif media_type == "Video":
                self.audio_controls_frame.pack_forget()
                self.preview_label.config(text='')
                # Start video playback thread
                if self.video_thread and self.video_thread.is_alive():
                    self.stop_video.set()
                    self.video_thread.join()
                    self.video_cap.release()
                    self.video_thread = None

                self.video_cap = cv2.VideoCapture(file_path)
                if not self.video_cap.isOpened():
                    raise Exception("Failed to open video file.")

                self.stop_video.clear()
                self.video_thread = threading.Thread(target=self.play_video)
                self.video_thread.daemon = True
                self.video_thread.start()

        except Exception as e:
            messagebox.showerror("Preview Error", f"Could not load preview: {str(e)}")

    def play_video(self):
        try:
            while not self.stop_video.is_set():
                ret, frame = self.video_cap.read()
                if not ret:
                    # Loop video or stop? For now, stop at end.
                    break

                # Convert frame to RGB then to PIL Image
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)

                # Resize frame to fit preview label
                img.thumbnail((400, 400))

                imgtk = ImageTk.PhotoImage(img)

                # Update label image safely in main thread
                self.preview_label.after(0, self.update_video_frame, imgtk)

                # Delay to control video FPS
                if self.video_cap.get(cv2.CAP_PROP_FPS) > 0:
                    delay = int(1000 / self.video_cap.get(cv2.CAP_PROP_FPS))
                else:
                    delay = 33
                if self.stop_video.wait(delay / 1000):
                    break
        finally:
            if self.video_cap:
                self.video_cap.release()
            self.preview_label.after(0, lambda: self.preview_label.config(image=''))

    def update_video_frame(self, imgtk):
        self.preview_label.config(image=imgtk)
        self.preview_label.image = imgtk

    def play_audio(self):
        try:
            pygame.mixer.music.load(self.current_file)
            pygame.mixer.music.play()
            self.status_bar.config(text="Playing audio...")
        except Exception as e:
            messagebox.showerror("Audio Error", f"Could not play audio: {str(e)}")

    def pause_audio(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.status_bar.config(text="Audio paused")
        else:
            pygame.mixer.music.unpause()
            self.status_bar.config(text="Audio playing")

    def stop_all_media(self):
        # Stop audio
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        # Stop video
        if self.video_thread and self.video_thread.is_alive():
            self.stop_video.set()
            self.video_thread.join()
            if self.video_cap:
                self.video_cap.release()
            self.video_thread = None

    def clear_preview(self):
        self.stop_all_media()
        self.preview_label.config(image='', text='')
        self.preview_image = None
        self.audio_controls_frame.pack_forget()

    def load_message_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.message_entry.delete(1.0, tk.END)
                    self.message_entry.insert(tk.END, f.read())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load message: {str(e)}")

    def encode(self):
        media_type = self.media_type.get()
        message = self.message_entry.get("1.0", tk.END).strip()
        
        if not message:
            messagebox.showwarning("Input Error", "Please enter a message to encode!")
            return
            
        try:
            output_path = self.save_file()
            if not output_path:
                return
                
            self.status_bar.config(text="Encoding... Please wait")
            self.root.update_idletasks()
            
            key = None
            if self.dark_mode:
                key = "mysecretkey"  # Example key for encryption

            if media_type == "Image":
                ImageSteganography.encode(self.current_file, message, output_path, key)
            elif media_type == "Audio":
                AudioSteganography.encode(self.current_file, message, output_path, key)
            elif media_type == "Video":
                VideoSteganography.encode(self.current_file, message, output_path, key)
                
            self.status_bar.config(text=f"Encoded successfully to: {output_path}")
            messagebox.showinfo("Success", "Message encoded successfully!")
            
        except Exception as e:
            messagebox.showerror("Encoding Error", f"Failed to encode: {str(e)}")
            self.status_bar.config(text="Encoding failed")
        finally:
            self.root.update_idletasks()

    def decode(self):
        media_type = self.media_type.get()
        if not self.current_file:
            messagebox.showwarning("Input Error", "Please select a file to decode!")
            return
            
        try:
            self.status_bar.config(text="Decoding... Please wait")
            self.root.update_idletasks()
            
            key = None
            if self.dark_mode:
                key = "mysecretkey"  # Example key for decryption

            if media_type == "Image":
                message = ImageSteganography.decode(self.current_file, key)
            elif media_type == "Audio":
                message = AudioSteganography.decode(self.current_file, key)
            elif media_type == "Video":
                message = VideoSteganography.decode(self.current_file, key)

            if message:
                self.message_entry.delete(1.0, tk.END)
                self.message_entry.insert(tk.END, message)
                self.status_bar.config(text="Decoded successfully")
            else:
                messagebox.showinfo("Result", "No hidden message found!")
                self.status_bar.config(text="No message found")
        except Exception as e:
            messagebox.showerror("Decoding Error", f"Failed to decode: {str(e)}")
            self.status_bar.config(text="Decoding failed")
        finally:
            self.root.update_idletasks()

    def clear_all(self):
        self.clear_preview()
        self.message_entry.delete(1.0, tk.END)
        self.current_file = None
        self.status_bar.config(text="Cleared all")

    def show_about(self):
        messagebox.showinfo("About SecureStego",
                            "SecureStego v1.0\nAn advanced steganography tool\nDeveloped by Naresh Kathayat")

    def on_close(self):
        self.stop_all_media()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyGUI(root)
    root.mainloop()

