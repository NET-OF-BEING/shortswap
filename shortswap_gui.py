#!/usr/bin/env python3
"""
ShortSwap GUI - Graphical interface for Video Face-Swap Pipeline
Supports both YouTube videos and local video files
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
from pathlib import Path

class ShortSwapGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ShortSwap - Video Face-Swap")
        self.root.geometry("700x850")
        self.root.resizable(True, True)

        # Default values
        self.script_path = "/home/panda/Documents/PythonScripts/shortswap.sh"
        self.default_output = os.path.expanduser("~/Videos/ShortSwap")
        self.source_face_path = tk.StringVar()
        self.target_person_path = tk.StringVar()
        self.output_dir = tk.StringVar(value=self.default_output)
        self.use_cuda = tk.BooleanVar(value=False)
        self.add_watermark = tk.BooleanVar(value=False)
        self.keep_frames = tk.BooleanVar(value=False)
        self.gender_filter = tk.StringVar(value="all")
        self.video_source = tk.StringVar(value="url")  # "url" or "file"
        self.local_video_path = tk.StringVar()
        self.is_processing = False
        self.current_process = None

        self.setup_ui()

    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="ShortSwap",
                               font=('Arial', 24, 'bold'),
                               foreground='#F44336')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))

        subtitle_label = ttk.Label(main_frame, text="Video Face-Swap Pipeline",
                                  font=('Arial', 10),
                                  foreground='#666')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))

        # Video Source Section
        video_frame = ttk.LabelFrame(main_frame, text="Video Source", padding="10")
        video_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        # Radio buttons for source type
        ttk.Radiobutton(video_frame, text="YouTube URL", variable=self.video_source,
                       value="url", command=self.toggle_video_source).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Radiobutton(video_frame, text="Local Video File", variable=self.video_source,
                       value="file", command=self.toggle_video_source).grid(row=0, column=1, sticky=tk.W)

        # URL Entry
        ttk.Label(video_frame, text="URL:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.url_entry = ttk.Entry(video_frame, width=50)
        self.url_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        self.url_entry.insert(0, "https://youtube.com/shorts/")

        # Local Video File Entry
        ttk.Label(video_frame, text="File:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.video_file_entry = ttk.Entry(video_frame, textvariable=self.local_video_path, width=37, state='disabled')
        self.video_file_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        self.video_browse_button = ttk.Button(video_frame, text="Browse...", command=self.browse_video_file, state='disabled')
        self.video_browse_button.grid(row=2, column=2, pady=(10, 0))

        # Source Face Section
        face_frame = ttk.LabelFrame(main_frame, text="Source Face Image", padding="10")
        face_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(face_frame, text="Image:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.face_entry = ttk.Entry(face_frame, textvariable=self.source_face_path, width=45)
        self.face_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(face_frame, text="Browse...", command=self.browse_source_face).grid(row=0, column=2)

        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(output_frame, text="Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=45)
        self.output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_dir).grid(row=0, column=2)

        # Selective Swapping Section
        selective_frame = ttk.LabelFrame(main_frame, text="Selective Swapping (Optional)", padding="10")
        selective_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        # Gender filter
        ttk.Label(selective_frame, text="Gender Filter:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        gender_combo = ttk.Combobox(selective_frame, textvariable=self.gender_filter,
                                     values=['all', 'male', 'female'], state='readonly', width=15)
        gender_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Label(selective_frame, text="(Swap only specified gender)",
                 font=('Arial', 8), foreground='#666').grid(row=0, column=2, sticky=tk.W)

        # Target person
        ttk.Label(selective_frame, text="Target Person:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.target_person_entry = ttk.Entry(selective_frame, textvariable=self.target_person_path, width=35)
        self.target_person_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(selective_frame, text="Browse...", command=self.browse_target_person).grid(row=1, column=2, pady=(10, 0))
        ttk.Label(selective_frame, text="(Reference image of specific person to target)",
                 font=('Arial', 8), foreground='#666').grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=(2, 0))

        # Options Section
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Checkbutton(options_frame, text="Use GPU/CUDA (Faster)",
                       variable=self.use_cuda).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="Add Watermark",
                       variable=self.add_watermark).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="Keep Frame Files",
                       variable=self.keep_frames).grid(row=0, column=2, sticky=tk.W)

        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=(0, 15))

        self.swap_button = ttk.Button(button_frame, text="Start Face Swap",
                                     command=self.start_swap,
                                     style='Accent.TButton')
        self.swap_button.grid(row=0, column=0, padx=(0, 10), ipadx=20, ipady=10)

        self.cancel_button = ttk.Button(button_frame, text="Cancel",
                                       command=self.cancel_swap,
                                       state='disabled')
        self.cancel_button.grid(row=0, column=1, ipadx=20, ipady=10)

        # Progress/Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        status_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.status_text = scrolledtext.ScrolledText(status_frame, height=12, width=70,
                                                     font=('Courier', 9),
                                                     state='disabled',
                                                     background='#f5f5f5')
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground='#4CAF50')
        self.status_label.grid(row=10, column=0, columnspan=3)

        # Configure style for accent button
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 12, 'bold'))

    def toggle_video_source(self):
        """Enable/disable URL or file inputs based on selection"""
        if self.video_source.get() == "url":
            self.url_entry.config(state='normal')
            self.video_file_entry.config(state='disabled')
            self.video_browse_button.config(state='disabled')
        else:
            self.url_entry.config(state='disabled')
            self.video_file_entry.config(state='normal')
            self.video_browse_button.config(state='normal')

    def browse_video_file(self):
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.webm"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.local_video_path.set(filename)

    def browse_source_face(self):
        filename = filedialog.askopenfilename(
            title="Select Source Face Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.source_face_path.set(filename)

    def browse_output_dir(self):
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get()
        )
        if directory:
            self.output_dir.set(directory)

    def browse_target_person(self):
        filename = filedialog.askopenfilename(
            title="Select Target Person Reference Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.target_person_path.set(filename)

    def log_output(self, message, color=None):
        """Add message to status text widget"""
        self.status_text.config(state='normal')

        if color:
            # Create tag for colored text
            tag_name = f"color_{color}"
            self.status_text.tag_config(tag_name, foreground=color)
            self.status_text.insert(tk.END, message + "\n", tag_name)
        else:
            self.status_text.insert(tk.END, message + "\n")

        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')

    def clear_log(self):
        """Clear the status text"""
        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state='disabled')

    def validate_inputs(self):
        """Validate all inputs before starting"""
        face_path = self.source_face_path.get().strip()

        # Validate video source
        if self.video_source.get() == "url":
            url = self.url_entry.get().strip()
            if not url or url == "https://youtube.com/shorts/":
                messagebox.showerror("Error", "Please enter a YouTube URL")
                return False
            # Allow regular YouTube URLs too, not just Shorts
            if not "youtube.com" in url and not "youtu.be/" in url:
                messagebox.showerror("Error", "Invalid YouTube URL")
                return False
        else:
            video_path = self.local_video_path.get().strip()
            if not video_path:
                messagebox.showerror("Error", "Please select a local video file")
                return False
            if not os.path.exists(video_path):
                messagebox.showerror("Error", f"Video file not found:\n{video_path}")
                return False

        # Validate face image
        if not face_path:
            messagebox.showerror("Error", "Please select a source face image")
            return False

        if not os.path.exists(face_path):
            messagebox.showerror("Error", f"Source face image not found:\n{face_path}")
            return False

        return True

    def start_swap(self):
        """Start the face swap process"""
        if self.is_processing:
            messagebox.showwarning("Warning", "A face swap is already in progress!")
            return

        if not self.validate_inputs():
            return

        # Clear previous log
        self.clear_log()

        # Update UI state
        self.is_processing = True
        self.swap_button.config(state='disabled', text='Processing...')
        self.cancel_button.config(state='normal')
        self.progress.start(10)
        self.status_label.config(text="Processing...", foreground='#FF9800')

        # Build command
        cmd = [self.script_path]

        # Add video source (URL or local file)
        if self.video_source.get() == "url":
            cmd.extend(["--url", self.url_entry.get().strip()])
        else:
            cmd.extend(["--video", self.local_video_path.get().strip()])

        # Add face and output
        cmd.extend([
            "--face", self.source_face_path.get().strip(),
            "--output", self.output_dir.get()
        ])

        if self.use_cuda.get():
            cmd.append("--cuda")

        if self.add_watermark.get():
            cmd.append("--watermark")

        if self.keep_frames.get():
            cmd.append("--keep-frames")

        if self.gender_filter.get() != "all":
            cmd.extend(["--gender", self.gender_filter.get()])

        if self.target_person_path.get().strip():
            cmd.extend(["--target-person", self.target_person_path.get().strip()])

        # Log the command
        self.log_output("Starting ShortSwap Pipeline...", "#2196F3")
        self.log_output(f"Command: {' '.join(cmd)}", "#666")
        self.log_output("=" * 70)

        # Run in separate thread
        thread = threading.Thread(target=self.run_swap, args=(cmd,))
        thread.daemon = True
        thread.start()

    def run_swap(self, cmd):
        """Run the swap command in a separate thread"""
        try:
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            process = self.current_process

            # Read output line by line
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    # Color code based on content
                    if "✓" in line or "Success" in line or "Complete" in line:
                        self.root.after(0, self.log_output, line, "#4CAF50")
                    elif "ERROR" in line or "✗" in line or "Failed" in line:
                        self.root.after(0, self.log_output, line, "#F44336")
                    elif "==>" in line or "Step" in line:
                        self.root.after(0, self.log_output, line, "#2196F3")
                    elif "⚠" in line or "WARNING" in line:
                        self.root.after(0, self.log_output, line, "#FF9800")
                    else:
                        self.root.after(0, self.log_output, line)

            process.wait()

            # Check return code
            if process.returncode == 0:
                self.root.after(0, self.on_success)
            else:
                self.root.after(0, self.on_error, f"Process exited with code {process.returncode}")

        except Exception as e:
            self.root.after(0, self.on_error, str(e))

    def cancel_swap(self):
        """Cancel the current face swap process"""
        if self.current_process and self.current_process.poll() is None:
            # Process is still running, terminate it
            self.current_process.terminate()
            try:
                self.current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                self.current_process.kill()
                self.current_process.wait()

            self.log_output("=" * 70)
            self.log_output("Process cancelled by user", "#FF9800")

            # Reset UI state
            self.progress.stop()
            self.swap_button.config(state='normal', text='Start Face Swap')
            self.cancel_button.config(state='disabled')
            self.status_label.config(text="Cancelled", foreground='#FF9800')
            self.is_processing = False
            self.current_process = None

    def on_success(self):
        """Called when swap completes successfully"""
        self.progress.stop()
        self.swap_button.config(state='normal', text='Start Face Swap')
        self.cancel_button.config(state='disabled')
        self.status_label.config(text="Completed Successfully!", foreground='#4CAF50')
        self.is_processing = False
        self.current_process = None

        self.log_output("=" * 70)
        self.log_output("ShortSwap completed successfully!", "#4CAF50")

        # Show success dialog
        result = messagebox.askyesno(
            "Success!",
            "Face swap completed successfully!\n\nWould you like to open the output folder?",
            icon='info'
        )

        if result:
            subprocess.Popen(['xdg-open', self.output_dir.get()])

    def on_error(self, error_msg):
        """Called when swap fails"""
        self.progress.stop()
        self.swap_button.config(state='normal', text='Start Face Swap')
        self.cancel_button.config(state='disabled')
        self.status_label.config(text="Failed", foreground='#F44336')
        self.is_processing = False
        self.current_process = None

        self.log_output("=" * 70)
        self.log_output(f"ERROR: {error_msg}", "#F44336")

        messagebox.showerror("Error", f"Face swap failed:\n\n{error_msg}")


def main():
    root = tk.Tk()
    app = ShortSwapGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
