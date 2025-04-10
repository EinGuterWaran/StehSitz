import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import json
import logging
from datetime import datetime, timedelta
import subprocess
import webbrowser

class SitStandReminder:
    def __init__(self, root):
        self.root = root
        self.root.title("StehSitz, your personal Sit-Stand Reminder")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Setup logging
        self.setup_logging()
        
        # Default settings
        self.default_settings = {
            "sit_duration": 30,  # minutes
            "stand_duration": 30,  # minutes
            "break_interval": 90,  # minutes
            "break_duration": 5,   # minutes
            "start_automatically": True,
            "current_position": "Sitting",
            "sound_enabled": True
        }
        
        # Load saved settings or use defaults
        self.settings = self.load_settings()
        
        # Status variables
        self.timer_running = False
        self.current_timer = None
        self.position_start_time = None
        self.last_break_time = None
        
        # Sound process
        self.sound_process = None

        # Create UI
        self.create_ui()
        
        # Start timer automatically if set
        if self.settings["start_automatically"]:
            self.start_timer()

    def setup_logging(self):
        """Setup logging configuration."""
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(script_dir, "logs")
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f"sit_stand_{datetime.now().strftime('%Y%m%d')}.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        logging.info("Application started")

    def load_settings(self):
        """Load saved settings or use defaults."""
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        settings_path = os.path.join(script_dir, "sit_stand_settings.json")
        
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    saved_settings = json.load(f)
                    # Ensure all settings are present
                    for key in self.default_settings:
                        if key not in saved_settings:
                            saved_settings[key] = self.default_settings[key]
                    logging.info("Settings loaded successfully")
                    return saved_settings
            else:
                # Save default settings if file doesn't exist
                with open(settings_path, 'w') as f:
                    json.dump(self.default_settings, f)
                logging.info("Default settings saved")
                return self.default_settings.copy()
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return self.default_settings.copy()

    def save_settings(self):
        """Save current settings."""
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        settings_path = os.path.join(script_dir, "sit_stand_settings.json")
        
        try:
            # Update settings with current values from UI
            self.settings["sit_duration"] = int(self.sit_duration_var.get())
            self.settings["stand_duration"] = int(self.stand_duration_var.get())
            self.settings["break_interval"] = int(self.break_interval_var.get())
            self.settings["break_duration"] = int(self.break_duration_var.get())
            self.settings["start_automatically"] = bool(self.start_auto_var.get())
            self.settings["sound_enabled"] = bool(self.sound_enabled_var.get())
            
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f)
            logging.info("Settings saved successfully")
            messagebox.showinfo("Info", "Settings saved!")
            self.play_sound()
        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Error saving settings: {e}")

    def create_ui(self):
        """Create the user interface."""
        # Create a notebook (tab container)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab for timer
        timer_frame = ttk.Frame(notebook)
        notebook.add(timer_frame, text="Timer")
        
        # Tab for settings
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        
        # Tab for about/credits
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="About")
        
        # ---------- Timer Tab ----------
        # Display current position
        self.position_label = ttk.Label(timer_frame, text=f"Current position: {self.settings['current_position']}", font=("Arial", 14))
        self.position_label.pack(pady=20)
        
        # Display remaining time
        self.time_left_label = ttk.Label(timer_frame, text="Time remaining: --:--", font=("Arial", 24))
        self.time_left_label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(timer_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)
        
        # Start/Stop button
        self.timer_button_frame = ttk.Frame(timer_frame)
        self.timer_button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(self.timer_button_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(self.timer_button_frame, text="Stop", command=self.stop_timer)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Manual switch buttons
        self.switch_button_frame = ttk.Frame(timer_frame)
        self.switch_button_frame.pack(pady=20)
        
        self.sit_button = ttk.Button(self.switch_button_frame, text="Sitting", command=lambda: self.manual_switch("Sitting"))
        self.sit_button.grid(row=0, column=0, padx=5)
        
        self.stand_button = ttk.Button(self.switch_button_frame, text="Standing", command=lambda: self.manual_switch("Standing"))
        self.stand_button.grid(row=0, column=1, padx=5)
        
        self.break_button = ttk.Button(self.switch_button_frame, text="Break", command=lambda: self.manual_switch("Break"))
        self.break_button.grid(row=0, column=2, padx=5)
        
        # Status
        status_frame = ttk.LabelFrame(timer_frame, text="Status")
        status_frame.pack(fill="x", padx=10, pady=10)
        
        self.status_text = tk.Text(status_frame, height=4, wrap=tk.WORD)
        self.status_text.pack(fill="x", padx=5, pady=5)
        self.status_text.insert(tk.END, "Ready to start...\n")
        self.status_text.config(state=tk.DISABLED)
        
        # ---------- Settings Tab ----------
        # Settings for sit/stand duration
        duration_frame = ttk.LabelFrame(settings_frame, text="Time settings (minutes)")
        duration_frame.pack(fill="x", padx=10, pady=10)
        
        # Sitting duration
        ttk.Label(duration_frame, text="Sitting:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.sit_duration_var = tk.StringVar(value=str(self.settings["sit_duration"]))
        ttk.Spinbox(duration_frame, from_=5, to=120, increment=5, textvariable=self.sit_duration_var, width=5).grid(row=0, column=1, padx=10, pady=5)
        
        # Standing duration
        ttk.Label(duration_frame, text="Standing:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.stand_duration_var = tk.StringVar(value=str(self.settings["stand_duration"]))
        ttk.Spinbox(duration_frame, from_=5, to=120, increment=5, textvariable=self.stand_duration_var, width=5).grid(row=1, column=1, padx=10, pady=5)
        
        # Break interval
        ttk.Label(duration_frame, text="Break every:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.break_interval_var = tk.StringVar(value=str(self.settings["break_interval"]))
        ttk.Spinbox(duration_frame, from_=30, to=180, increment=15, textvariable=self.break_interval_var, width=5).grid(row=2, column=1, padx=10, pady=5)
        
        # Break duration
        ttk.Label(duration_frame, text="Break duration:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.break_duration_var = tk.StringVar(value=str(self.settings["break_duration"]))
        ttk.Spinbox(duration_frame, from_=1, to=15, increment=1, textvariable=self.break_duration_var, width=5).grid(row=3, column=1, padx=10, pady=5)
        
        # Additional settings
        options_frame = ttk.LabelFrame(settings_frame, text="General settings")
        options_frame.pack(fill="x", padx=10, pady=10)
        
        # Automatic start
        self.start_auto_var = tk.BooleanVar(value=self.settings["start_automatically"])
        ttk.Checkbutton(options_frame, text="Start timer automatically", variable=self.start_auto_var).pack(anchor="w", padx=10, pady=5)
        
        # Enable sound
        self.sound_enabled_var = tk.BooleanVar(value=self.settings["sound_enabled"])
        ttk.Checkbutton(options_frame, text="Sound for notifications", variable=self.sound_enabled_var).pack(anchor="w", padx=10, pady=5)
        
        # Save button
        ttk.Button(settings_frame, text="Save settings", command=self.save_settings).pack(pady=20)
        
        # ---------- About Tab ----------
        # Add credits information
        about_frame_inner = ttk.Frame(about_frame)
        about_frame_inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        # App title
        ttk.Label(about_frame_inner, text="StehSitz", font=("Arial", 16, "bold")).pack(pady=(0, 5))
        ttk.Label(about_frame_inner, text="Your personal Sit-Stand Reminder").pack(pady=(0, 20))
        
        # Credits frame
        credits_frame = ttk.LabelFrame(about_frame_inner, text="Credits")
        credits_frame.pack(fill="x", padx=10, pady=10)
        
        # Creator info
        ttk.Label(credits_frame, text="Vibe coded by Janu from FeatherFlow", font=("Arial", 10)).pack(pady=(10, 5))
        
        # Links frame
        links_frame = ttk.Frame(credits_frame)
        links_frame.pack(pady=10)
        
        # Janu link
        janu_link = ttk.Label(links_frame, text="Janu", foreground="blue", cursor="hand2", font=("Arial", 10, "underline"))
        janu_link.grid(row=0, column=0, padx=(0, 5))
        janu_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://x.com/JanuBuilds"))
        
        ttk.Label(links_frame, text="|", font=("Arial", 10)).grid(row=0, column=1, padx=5)
        
        # FeatherFlow link
        featherflow_link = ttk.Label(links_frame, text="FeatherFlow", foreground="blue", cursor="hand2", font=("Arial", 10, "underline"))
        featherflow_link.grid(row=0, column=2, padx=(5, 0))
        featherflow_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://feather-flow.com"))
        
        # Version info
        ttk.Label(about_frame_inner, text="Version 1.0", font=("Arial", 8)).pack(side="bottom", pady=10)

    def play_sound(self, sound_name="Pop"):
        """Play a system sound more efficiently."""
        if self.settings["sound_enabled"]:
            try:
                # Kill any existing sound process
                if self.sound_process and self.sound_process.poll() is None:
                    self.sound_process.terminate()
                
                # Start new sound process
                sound_path = f"/System/Library/Sounds/{sound_name}.aiff"
                self.sound_process = subprocess.Popen(['afplay', sound_path], 
                                                    stdout=subprocess.DEVNULL,
                                                    stderr=subprocess.DEVNULL)
                logging.debug(f"Playing sound: {sound_name}")
            except Exception as e:
                logging.error(f"Error playing sound: {e}")

    def start_timer(self):
        """Start the timer."""
        if self.timer_running:
            return
            
        self.timer_running = True
        self.position_start_time = datetime.now()
        self.last_break_time = datetime.now()
        self.update_status(f"Timer started. Position: {self.settings['current_position']}")
        self.play_sound()
        
        # Start timer in separate thread
        self.current_timer = threading.Thread(target=self.run_timer)
        self.current_timer.daemon = True
        self.current_timer.start()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_timer(self):
        """Stop the timer."""
        self.timer_running = False
        self.update_status("Timer stopped.")
        self.time_left_label.config(text="Time remaining: --:--")
        self.progress.config(value=0)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.play_sound()

    def run_timer(self):
        """Main timer function."""
        while self.timer_running:
            now = datetime.now()
            
            # Calculate time since last position change
            elapsed_time = now - self.position_start_time
            
            # Determine time until next switch based on current position
            if self.settings["current_position"] == "Sitting":
                total_duration = timedelta(minutes=int(self.settings["sit_duration"]))
            elif self.settings["current_position"] == "Standing":
                total_duration = timedelta(minutes=int(self.settings["stand_duration"]))
            else:  # Break
                total_duration = timedelta(minutes=int(self.settings["break_duration"]))
            
            # Calculate remaining time
            time_left = total_duration - elapsed_time
            
            # Update the UI
            if time_left.total_seconds() > 0:
                minutes, seconds = divmod(int(time_left.total_seconds()), 60)
                self.root.after(0, lambda: self.time_left_label.config(text=f"Time remaining: {minutes:02d}:{seconds:02d}"))
                
                # Update progress bar
                progress_value = 100 - (time_left.total_seconds() / total_duration.total_seconds() * 100)
                self.root.after(0, lambda v=progress_value: self.progress.config(value=v))
            else:
                # Time is up, switch position
                if self.settings["current_position"] == "Sitting":
                    next_pos = "Standing"
                elif self.settings["current_position"] == "Standing":
                    next_pos = "Sitting"
                else:  # After a break, return to previous position
                    next_pos = "Sitting"  # Default if no previous position is known
                
                # Use after to ensure UI updates and notifications happen in the main thread
                self.root.after(0, lambda p=next_pos: self.change_position(p))
            
            # Check if a break should be taken
            if self.settings["current_position"] != "Break":
                time_since_break = now - self.last_break_time
                break_interval = timedelta(minutes=int(self.settings["break_interval"]))
                
                if time_since_break >= break_interval:
                    # Use after to ensure UI updates and notifications happen in the main thread
                    self.root.after(0, lambda: self.change_position("Break"))
            
            # Wait a second before next check
            time.sleep(1)

    def change_position(self, new_position):
        """Change position and update UI."""
        old_position = self.settings["current_position"]
        self.settings["current_position"] = new_position
        self.position_start_time = datetime.now()
        
        if new_position == "Break":
            self.last_break_time = datetime.now()
        
        self.position_label.config(text=f"Current position: {new_position}")
        
        # Play sound for position change
        self.play_sound("Glass")
        
        # Send notification with more detailed message
        notification_title = "Position Change"
        notification_message = f"Time to switch from {old_position} to {new_position}"
        self.send_notification(notification_title, notification_message)
        self.update_status(f"Position changed: {old_position} → {new_position}")

    def manual_switch(self, new_position):
        """Manual position switch."""
        self.play_sound()
        if self.timer_running:
            self.change_position(new_position)
        else:
            self.settings["current_position"] = new_position
            self.position_label.config(text=f"Current position: {new_position}")
            self.update_status(f"Position manually changed to: {new_position}")

    def send_notification(self, title, message):
        """Send a macOS notification."""
        try:
            # First try with sound
            os_command = f'''
            osascript -e 'display notification "{message}" with title "{title}" sound name "Glass"'
            '''
            result = os.system(os_command)
            if result != 0:
                logging.warning("Notification with sound failed, trying without sound")
                # If failed, try without sound
                os_command = f'''
                osascript -e 'display notification "{message}" with title "{title}"'
                '''
                result = os.system(os_command)
                if result != 0:
                    logging.error("Notification failed completely")
                    # If still failed, try alternative notification method
                    try:
                        subprocess.run(['notify-send', title, message], check=True)
                    except Exception as e:
                        logging.error(f"Alternative notification also failed: {e}")
                else:
                    logging.info("Notification sent without sound")
            else:
                logging.info(f"Notification sent with sound: {title} - {message}")
        except Exception as e:
            logging.error(f"Error with notification: {e}")
            # Try one last time with a simpler command
            try:
                os.system(f'osascript -e \'display dialog "{message}" with title "{title}"\'')
            except Exception as e2:
                logging.error(f"Final notification attempt also failed: {e2}")

    def update_status(self, message):
        """Update the status text field."""
        self.status_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)

    def __del__(self):
        """Cleanup when object is destroyed."""
        if self.sound_process and self.sound_process.poll() is None:
            self.sound_process.terminate()

if __name__ == "__main__":
    root = tk.Tk()
    app = SitStandReminder(root)
    root.mainloop()
