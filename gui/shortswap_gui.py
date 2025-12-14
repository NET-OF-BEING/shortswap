#!/usr/bin/env python3
"""
ShortSwap 2.0 GUI - Video Face-Swap & AI Video Generation
Supports both YouTube videos, local video files, and AI video generation with ComfyUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
from pathlib import Path

# Import ComfyUI client from UnifiedMCP
sys.path.insert(0, str(Path.home() / "Documents/PythonScripts/UnifiedMCP/modules"))
try:
    from comfyui_module import ComfyUIClient
    COMFYUI_AVAILABLE = True
except ImportError:
    COMFYUI_AVAILABLE = False
    print("Warning: ComfyUI module not found. AI tab will have limited functionality.")


class ShortSwapGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ShortSwap 2.0 - Video Face-Swap & AI Generation")
        self.root.geometry("750x900")
        self.root.resizable(True, True)

        # Default values for Face Swap tab
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

        # AI tab variables
        self.ai_model = tk.StringVar(value="veo3")
        self.ai_input_image = tk.StringVar()
        self.ai_positive_prompt = tk.StringVar()
        self.ai_negative_prompt = tk.StringVar()
        self.ai_duration = tk.IntVar(value=5)
        self.ai_output_dir = tk.StringVar(value=os.path.expanduser("~/Videos/ShortSwap/AI"))

        # WAN2.5 specific
        self.wan_frames = tk.IntVar(value=81)
        self.wan_steps = tk.IntVar(value=30)
        self.wan_cfg = tk.DoubleVar(value=7.0)

        # VEO3 specific
        self.veo_aspect_ratio = tk.StringVar(value="16:9")
        self.veo_enhance_prompt = tk.BooleanVar(value=True)
        self.veo_generate_audio = tk.BooleanVar(value=False)

        self.is_processing = False
        self.current_process = None

        # Initialize ComfyUI client
        if COMFYUI_AVAILABLE:
            self.comfyui_client = ComfyUIClient()
        else:
            self.comfyui_client = None

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="ShortSwap 2.0",
                               font=('Arial', 24, 'bold'),
                               foreground='#F44336')
        title_label.grid(row=0, column=0, pady=(0, 5))

        subtitle_label = ttk.Label(main_frame, text="Video Face-Swap & AI Generation Pipeline",
                                  font=('Arial', 10),
                                  foreground='#666')
        subtitle_label.grid(row=1, column=0, pady=(0, 10))

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create tabs
        self.create_face_swap_tab()
        self.create_ai_tab()

    def create_face_swap_tab(self):
        """Create the Face Swap tab (original functionality)"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Face Swap")

        # Video Source Section
        video_frame = ttk.LabelFrame(tab, text="Video Source", padding="10")
        video_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

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
        face_frame = ttk.LabelFrame(tab, text="Source Face Image", padding="10")
        face_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(face_frame, text="Image:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.face_entry = ttk.Entry(face_frame, textvariable=self.source_face_path, width=45)
        self.face_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(face_frame, text="Browse...", command=self.browse_source_face).grid(row=0, column=2)

        # Output Section
        output_frame = ttk.LabelFrame(tab, text="Output Settings", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(output_frame, text="Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=45)
        self.output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_dir).grid(row=0, column=2)

        # Selective Swapping Section
        selective_frame = ttk.LabelFrame(tab, text="Selective Swapping (Optional)", padding="10")
        selective_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

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
        options_frame = ttk.LabelFrame(tab, text="Options", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Checkbutton(options_frame, text="Use GPU/CUDA (Faster)",
                       variable=self.use_cuda).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="Add Watermark",
                       variable=self.add_watermark).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="Keep Frame Files",
                       variable=self.keep_frames).grid(row=0, column=2, sticky=tk.W)

        # Action Buttons
        button_frame = ttk.Frame(tab)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(0, 15))

        self.swap_button = ttk.Button(button_frame, text="Start Face Swap",
                                     command=self.start_swap,
                                     style='Accent.TButton')
        self.swap_button.grid(row=0, column=0, padx=(0, 10), ipadx=20, ipady=10)

        self.cancel_button = ttk.Button(button_frame, text="Cancel",
                                       command=self.cancel_swap,
                                       state='disabled')
        self.cancel_button.grid(row=0, column=1, ipadx=20, ipady=10)

        # Progress/Status Section
        status_frame = ttk.LabelFrame(tab, text="Progress", padding="10")
        status_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.status_text = scrolledtext.ScrolledText(status_frame, height=10, width=70,
                                                     font=('Courier', 9),
                                                     state='disabled',
                                                     background='#f5f5f5')
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Progress bar
        self.progress = ttk.Progressbar(tab, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Status label
        self.status_label = ttk.Label(tab, text="Ready", foreground='#4CAF50')
        self.status_label.grid(row=8, column=0, columnspan=3)

        # Configure style for accent button
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 12, 'bold'))

    def create_ai_tab(self):
        """Create the A.I. video generation tab"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="A.I.")

        # Model Selection Section
        model_frame = ttk.LabelFrame(tab, text="Model Selection", padding="10")
        model_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Radiobutton(model_frame, text="VEO 3.0 (Text-to-Video or Image-to-Video)",
                       variable=self.ai_model, value="veo3",
                       command=self.update_ai_model_options).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Radiobutton(model_frame, text="WAN 2.5 (Image-to-Video only)",
                       variable=self.ai_model, value="wan2.5",
                       command=self.update_ai_model_options).grid(row=1, column=0, sticky=tk.W)

        # ComfyUI Status
        if COMFYUI_AVAILABLE and self.comfyui_client:
            status = "Running" if self.comfyui_client.is_server_running() else "Not Running"
            color = "#4CAF50" if status == "Running" else "#F44336"
            self.comfyui_status_label = ttk.Label(model_frame,
                                                  text=f"ComfyUI Server: {status}",
                                                  foreground=color,
                                                  font=('Arial', 9))
            self.comfyui_status_label.grid(row=0, column=1, columnspan=2, sticky=tk.E, padx=(20, 0))
        else:
            ttk.Label(model_frame, text="ComfyUI: Not Available",
                     foreground='#F44336', font=('Arial', 9)).grid(row=0, column=1, columnspan=2, sticky=tk.E, padx=(20, 0))

        # Input Image Section
        image_frame = ttk.LabelFrame(tab, text="Input Image", padding="10")
        image_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(image_frame, text="Image:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.ai_image_entry = ttk.Entry(image_frame, textvariable=self.ai_input_image, width=45)
        self.ai_image_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(image_frame, text="Browse...", command=self.browse_ai_image).grid(row=0, column=2)
        self.ai_image_note = ttk.Label(image_frame, text="(Required for WAN2.5, optional for VEO3)",
                                       font=('Arial', 8), foreground='#666')
        self.ai_image_note.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(2, 0))

        # Prompts Section
        prompt_frame = ttk.LabelFrame(tab, text="Prompts", padding="10")
        prompt_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(prompt_frame, text="Positive Prompt:").grid(row=0, column=0, sticky=tk.NW, padx=(0, 10), pady=(5, 0))
        self.ai_positive_text = tk.Text(prompt_frame, height=3, width=50, font=('Arial', 9))
        self.ai_positive_text.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(prompt_frame, text="Negative Prompt:").grid(row=1, column=0, sticky=tk.NW, padx=(0, 10), pady=(5, 0))
        self.ai_negative_text = tk.Text(prompt_frame, height=2, width=50, font=('Arial', 9))
        self.ai_negative_text.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))
        ttk.Label(prompt_frame, text="(Optional - for advanced control)",
                 font=('Arial', 8), foreground='#666').grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=(2, 0))

        # Generation Settings Section
        settings_frame = ttk.LabelFrame(tab, text="Generation Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        # Duration
        ttk.Label(settings_frame, text="Duration (seconds):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        duration_spinbox = ttk.Spinbox(settings_frame, from_=5, to=10, textvariable=self.ai_duration,
                                       width=10, state='readonly')
        duration_spinbox.grid(row=0, column=1, sticky=tk.W)

        # Model-specific settings container
        self.model_settings_frame = ttk.Frame(settings_frame)
        self.model_settings_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # Create VEO3 and WAN2.5 settings frames
        self.create_veo_settings()
        self.create_wan_settings()

        # Show initial model settings
        self.update_ai_model_options()

        # Output Section
        ai_output_frame = ttk.LabelFrame(tab, text="Output Settings", padding="10")
        ai_output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(ai_output_frame, text="Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.ai_output_entry = ttk.Entry(ai_output_frame, textvariable=self.ai_output_dir, width=45)
        self.ai_output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(ai_output_frame, text="Browse...", command=self.browse_ai_output_dir).grid(row=0, column=2)

        # Action Buttons
        ai_button_frame = ttk.Frame(tab)
        ai_button_frame.grid(row=5, column=0, columnspan=3, pady=(0, 15))

        self.ai_generate_button = ttk.Button(ai_button_frame, text="Generate Video",
                                            command=self.start_ai_generation,
                                            style='Accent.TButton')
        self.ai_generate_button.grid(row=0, column=0, padx=(0, 10), ipadx=20, ipady=10)

        self.ai_cancel_button = ttk.Button(ai_button_frame, text="Cancel",
                                          command=self.cancel_ai_generation,
                                          state='disabled')
        self.ai_cancel_button.grid(row=0, column=1, ipadx=20, ipady=10)

        # Progress/Status Section
        ai_status_frame = ttk.LabelFrame(tab, text="Progress", padding="10")
        ai_status_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.ai_status_text = scrolledtext.ScrolledText(ai_status_frame, height=10, width=70,
                                                       font=('Courier', 9),
                                                       state='disabled',
                                                       background='#f5f5f5')
        self.ai_status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Progress bar
        self.ai_progress = ttk.Progressbar(tab, mode='indeterminate')
        self.ai_progress.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Status label
        self.ai_status_label = ttk.Label(tab, text="Ready", foreground='#4CAF50')
        self.ai_status_label.grid(row=8, column=0, columnspan=3)

    def create_veo_settings(self):
        """Create VEO3-specific settings"""
        self.veo_settings_frame = ttk.Frame(self.model_settings_frame)

        ttk.Label(self.veo_settings_frame, text="Aspect Ratio:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        aspect_combo = ttk.Combobox(self.veo_settings_frame, textvariable=self.veo_aspect_ratio,
                                    values=['16:9', '9:16', '1:1'], state='readonly', width=10)
        aspect_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        ttk.Checkbutton(self.veo_settings_frame, text="Enhance Prompt",
                       variable=self.veo_enhance_prompt).grid(row=0, column=2, sticky=tk.W, padx=(0, 20))

        ttk.Checkbutton(self.veo_settings_frame, text="Generate Audio",
                       variable=self.veo_generate_audio).grid(row=0, column=3, sticky=tk.W)

    def create_wan_settings(self):
        """Create WAN2.5-specific settings"""
        self.wan_settings_frame = ttk.Frame(self.model_settings_frame)

        ttk.Label(self.wan_settings_frame, text="Frames:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        frames_spinbox = ttk.Spinbox(self.wan_settings_frame, from_=41, to=121, increment=40,
                                     textvariable=self.wan_frames, width=10)
        frames_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        ttk.Label(self.wan_settings_frame, text="Steps:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        steps_spinbox = ttk.Spinbox(self.wan_settings_frame, from_=10, to=50,
                                    textvariable=self.wan_steps, width=10)
        steps_spinbox.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))

        ttk.Label(self.wan_settings_frame, text="CFG Scale:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        cfg_spinbox = ttk.Spinbox(self.wan_settings_frame, from_=1.0, to=20.0, increment=0.5,
                                  textvariable=self.wan_cfg, width=10)
        cfg_spinbox.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))

    def update_ai_model_options(self):
        """Show/hide model-specific settings based on selection"""
        # Hide all model settings
        self.veo_settings_frame.grid_forget()
        self.wan_settings_frame.grid_forget()

        # Show selected model settings
        if self.ai_model.get() == "veo3":
            self.veo_settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        else:  # wan2.5
            self.wan_settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

    # Face Swap Tab Methods
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

    def browse_ai_image(self):
        filename = filedialog.askopenfilename(
            title="Select Input Image for AI Video Generation",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.ai_input_image.set(filename)

    def browse_ai_output_dir(self):
        directory = filedialog.askdirectory(
            title="Select AI Output Directory",
            initialdir=self.ai_output_dir.get()
        )
        if directory:
            self.ai_output_dir.set(directory)

    def log_output(self, message, color=None):
        """Add message to status text widget"""
        self.status_text.config(state='normal')

        if color:
            tag_name = f"color_{color}"
            self.status_text.tag_config(tag_name, foreground=color)
            self.status_text.insert(tk.END, message + "\n", tag_name)
        else:
            self.status_text.insert(tk.END, message + "\n")

        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')

    def log_ai_output(self, message, color=None):
        """Add message to AI status text widget"""
        self.ai_status_text.config(state='normal')

        if color:
            tag_name = f"color_{color}"
            self.ai_status_text.tag_config(tag_name, foreground=color)
            self.ai_status_text.insert(tk.END, message + "\n", tag_name)
        else:
            self.ai_status_text.insert(tk.END, message + "\n")

        self.ai_status_text.see(tk.END)
        self.ai_status_text.config(state='disabled')

    def clear_log(self):
        """Clear the status text"""
        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state='disabled')

    def clear_ai_log(self):
        """Clear the AI status text"""
        self.ai_status_text.config(state='normal')
        self.ai_status_text.delete(1.0, tk.END)
        self.ai_status_text.config(state='disabled')

    def validate_inputs(self):
        """Validate all inputs before starting face swap"""
        face_path = self.source_face_path.get().strip()

        # Validate video source
        if self.video_source.get() == "url":
            url = self.url_entry.get().strip()
            if not url or url == "https://youtube.com/shorts/":
                messagebox.showerror("Error", "Please enter a YouTube URL")
                return False
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

    def validate_ai_inputs(self):
        """Validate all inputs before starting AI generation"""
        model = self.ai_model.get()
        image_path = self.ai_input_image.get().strip()
        positive_prompt = self.ai_positive_text.get("1.0", tk.END).strip()

        # Check ComfyUI
        if not COMFYUI_AVAILABLE or not self.comfyui_client:
            messagebox.showerror("Error", "ComfyUI module not available.\n\nPlease ensure UnifiedMCP is installed properly.")
            return False

        if not self.comfyui_client.is_server_running():
            messagebox.showerror("Error", "ComfyUI server is not running.\n\nStart it with:\ncd ~/ComfyUI && ./venv/bin/python main.py")
            return False

        # Validate image for WAN2.5
        if model == "wan2.5":
            if not image_path:
                messagebox.showerror("Error", "WAN 2.5 requires an input image.\n\nPlease select an image.")
                return False
            if not os.path.exists(image_path):
                messagebox.showerror("Error", f"Input image not found:\n{image_path}")
                return False

        # Validate image for VEO3 if provided
        if image_path and not os.path.exists(image_path):
            messagebox.showerror("Error", f"Input image not found:\n{image_path}")
            return False

        # Validate positive prompt
        if not positive_prompt:
            messagebox.showerror("Error", "Please enter a positive prompt describing the video you want to generate.")
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
            self.current_process.terminate()
            try:
                self.current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
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

    # AI Generation Methods
    def start_ai_generation(self):
        """Start AI video generation"""
        if self.is_processing:
            messagebox.showwarning("Warning", "A generation is already in progress!")
            return

        if not self.validate_ai_inputs():
            return

        # Clear previous log
        self.clear_ai_log()

        # Update UI state
        self.is_processing = True
        self.ai_generate_button.config(state='disabled', text='Generating...')
        self.ai_cancel_button.config(state='normal')
        self.ai_progress.start(10)
        self.ai_status_label.config(text="Generating...", foreground='#FF9800')

        # Run in separate thread
        thread = threading.Thread(target=self.run_ai_generation)
        thread.daemon = True
        thread.start()

    def run_ai_generation(self):
        """Run AI video generation in a separate thread"""
        try:
            model = self.ai_model.get()
            image_path = self.ai_input_image.get().strip() or None
            positive_prompt = self.ai_positive_text.get("1.0", tk.END).strip()
            negative_prompt = self.ai_negative_text.get("1.0", tk.END).strip()

            self.root.after(0, self.log_ai_output, "Starting AI Video Generation...", "#2196F3")
            self.root.after(0, self.log_ai_output, f"Model: {model.upper()}", "#666")
            self.root.after(0, self.log_ai_output, f"Prompt: {positive_prompt}", "#666")
            if negative_prompt:
                self.root.after(0, self.log_ai_output, f"Negative Prompt: {negative_prompt}", "#666")
            self.root.after(0, self.log_ai_output, "=" * 70)

            # Build kwargs based on model
            kwargs = {}

            if model == "wan2.5":
                kwargs = {
                    "num_frames": self.wan_frames.get(),
                    "steps": self.wan_steps.get(),
                    "cfg": self.wan_cfg.get()
                }
                self.root.after(0, self.log_ai_output,
                               f"WAN2.5 Settings: {self.wan_frames.get()} frames, {self.wan_steps.get()} steps, CFG={self.wan_cfg.get()}")
            else:  # veo3
                kwargs = {
                    "duration_seconds": self.ai_duration.get(),
                    "aspect_ratio": self.veo_aspect_ratio.get(),
                    "enhance_prompt": self.veo_enhance_prompt.get(),
                    "generate_audio": self.veo_generate_audio.get()
                }
                self.root.after(0, self.log_ai_output,
                               f"VEO3 Settings: {self.ai_duration.get()}s, {self.veo_aspect_ratio.get()}, "
                               f"Enhance={'Yes' if self.veo_enhance_prompt.get() else 'No'}, "
                               f"Audio={'Yes' if self.veo_generate_audio.get() else 'No'}")

            self.root.after(0, self.log_ai_output, "Sending to ComfyUI...", "#2196F3")

            # Generate video
            result = self.comfyui_client.generate_video(
                model=model,
                image_path=image_path,
                prompt=positive_prompt,
                **kwargs
            )

            if result['status'] == 'success':
                video_path = result['video_path']

                # Move to output directory
                output_dir = Path(self.ai_output_dir.get())
                output_dir.mkdir(parents=True, exist_ok=True)

                # Generate filename
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"ai_video_{model}_{timestamp}.mp4"
                output_path = output_dir / output_filename

                # Copy file
                import shutil
                shutil.copy2(video_path, output_path)

                self.root.after(0, self.log_ai_output, "=" * 70, None)
                self.root.after(0, self.log_ai_output, f"Video saved to: {output_path}", "#4CAF50")
                self.root.after(0, self.on_ai_success, str(output_path))
            else:
                self.root.after(0, self.on_ai_error, result['message'])

        except Exception as e:
            self.root.after(0, self.on_ai_error, str(e))

    def cancel_ai_generation(self):
        """Cancel AI generation (limited functionality - ComfyUI doesn't support cancellation easily)"""
        messagebox.showinfo("Info", "AI generation cannot be cancelled mid-process.\n\nPlease wait for completion or restart ComfyUI server.")

    def on_ai_success(self, output_path):
        """Called when AI generation completes successfully"""
        self.ai_progress.stop()
        self.ai_generate_button.config(state='normal', text='Generate Video')
        self.ai_cancel_button.config(state='disabled')
        self.ai_status_label.config(text="Completed Successfully!", foreground='#4CAF50')
        self.is_processing = False

        self.log_ai_output("AI video generation completed successfully!", "#4CAF50")

        # Show success dialog
        result = messagebox.askyesno(
            "Success!",
            f"AI video generated successfully!\n\nSaved to:\n{output_path}\n\nWould you like to open the output folder?",
            icon='info'
        )

        if result:
            subprocess.Popen(['xdg-open', self.ai_output_dir.get()])

    def on_ai_error(self, error_msg):
        """Called when AI generation fails"""
        self.ai_progress.stop()
        self.ai_generate_button.config(state='normal', text='Generate Video')
        self.ai_cancel_button.config(state='disabled')
        self.ai_status_label.config(text="Failed", foreground='#F44336')
        self.is_processing = False

        self.log_ai_output("=" * 70)
        self.log_ai_output(f"ERROR: {error_msg}", "#F44336")

        messagebox.showerror("Error", f"AI video generation failed:\n\n{error_msg}")


def main():
    root = tk.Tk()
    app = ShortSwapGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
