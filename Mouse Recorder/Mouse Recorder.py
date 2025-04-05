import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mouse
import keyboard
import time
import json
import threading
import os

class MouseRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Action Recorder")
        self.root.geometry("450x300")
        
        # Variables
        self.recording = False
        self.playing = False
        self.loop_playback = False
        self.recorded_events = []
        self.start_time = 0
        self.playback_thread = None
        
        # UI Elements
        self.setup_ui()
        
    def setup_ui(self):
        # Main Frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Recording Button
        self.record_button = ttk.Button(
            main_frame, 
            text="Start Recording", 
            command=self.toggle_recording,
            width=20
        )
        self.record_button.pack(pady=5)
        
        # Playback Button
        self.play_button = ttk.Button(
            main_frame, 
            text="Play Recording", 
            command=self.play_recording,
            state=tk.DISABLED,
            width=20
        )
        self.play_button.pack(pady=5)
        
        # Loop Checkbutton
        self.loop_var = tk.BooleanVar()
        self.loop_check = ttk.Checkbutton(
            main_frame,
            text="Loop Playback",
            variable=self.loop_var,
            command=self.toggle_loop
        )
        self.loop_check.pack(pady=5)
        
        # Status Label
        self.status_label = ttk.Label(
            main_frame, 
            text="Status: Ready",
            font=('Helvetica', 10, 'bold')
        )
        self.status_label.pack(pady=10)
        
        # Speed Control
        speed_frame = ttk.Frame(main_frame)
        speed_frame.pack(pady=5)
        
        ttk.Label(speed_frame, text="Playback Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_options = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 5.0]
        self.speed_combobox = ttk.Combobox(
            speed_frame, 
            textvariable=self.speed_var,
            values=speed_options,
            width=5,
            state="readonly"
        )
        self.speed_combobox.current(speed_options.index(1.0))
        self.speed_combobox.pack(side=tk.LEFT, padx=5)
        
        # Button Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Save Button
        self.save_button = ttk.Button(
            button_frame, 
            text="Save Recording",
            command=self.save_recording,
            state=tk.DISABLED,
            width=15
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Load Button
        self.load_button = ttk.Button(
            button_frame, 
            text="Load Recording",
            command=self.load_recording,
            width=15
        )
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        # Stop Button (initially hidden)
        self.stop_button = ttk.Button(
            main_frame,
            text="Stop Playback",
            command=self.stop_playback,
            state=tk.DISABLED
        )

        # Hotkey info
        ttk.Label(main_frame, text="Press F10 to stop recording", font=('Helvetica', 8)).pack(pady=5)
        ttk.Label(main_frame, text="Press F9 to stop playback", font=('Helvetica', 8)).pack(pady=2)
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.recording = True
        self.recorded_events = []
        self.record_button.config(text="Stop Recording (F10)")
        self.play_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Recording...")
        
        # Register hotkey to stop recording
        keyboard.add_hotkey('f10', self.stop_recording)
        
        # Start recording
        self.start_time = time.time()
        mouse.hook(self.record_event)
        keyboard.hook(self.record_key_event)
        
    def stop_recording(self):
        if self.recording:
            self.recording = False
            mouse.unhook_all()
            keyboard.unhook_all()
            self.record_button.config(text="Start Recording")
            
            if self.recorded_events:
                self.play_button.config(state=tk.NORMAL)
                self.save_button.config(state=tk.NORMAL)
                self.status_label.config(text=f"Status: Ready ({len(self.recorded_events)} events recorded)")
            else:
                self.status_label.config(text="Status: Ready (No events recorded)")
    
    def record_event(self, event):
        if self.recording:
            event_dict = {
                'type': 'mouse',
                'event_type': str(type(event)).split('.')[-1][:-2],
                'time': time.time() - self.start_time
            }
            
            if hasattr(event, 'x') and hasattr(event, 'y'):
                event_dict.update({'x': event.x, 'y': event.y})
            
            if isinstance(event, mouse.ButtonEvent):
                event_dict.update({
                    'button': str(event.button),
                    'action': 'pressed' if event.event_type == 'down' else 'released'
                })
            
            elif isinstance(event, mouse.WheelEvent):
                event_dict.update({
                    'delta': event.delta
                })
            
            self.recorded_events.append(event_dict)
    
    def record_key_event(self, event):
        if self.recording and event.event_type == 'down':
            self.recorded_events.append({
                'type': 'keyboard',
                'event_type': 'key_press',
                'time': time.time() - self.start_time,
                'key': event.name
            })
    
    def play_recording(self):
        if not self.recorded_events or self.playing:
            return
            
        self.playing = True
        self.record_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Playing...")
        
        # Register hotkey to stop playback
        keyboard.add_hotkey('f9', self.stop_playback)
        
        self.playback_thread = threading.Thread(target=self._play_actions, daemon=True)
        self.playback_thread.start()
    
    def _play_actions(self):
        speed = self.speed_var.get()
        
        try:
            while True:
                start_time = time.time()
                
                for event in self.recorded_events:
                    if not self.playing:
                        self.root.after(0, self._playback_finished)
                        return
                    
                    # Wait for the right time to perform the action
                    while time.time() - start_time < event['time'] / speed:
                        if not self.playing:
                            self.root.after(0, self._playback_finished)
                            return
                        time.sleep(0.001)
                    
                    # Execute the recorded action
                    if event['type'] == 'mouse':
                        if event['event_type'] == 'MoveEvent':
                            mouse.move(event['x'], event['y'])
                        elif event['event_type'] == 'ButtonEvent':
                            if event['action'] == 'pressed':
                                mouse.press(event['button'])
                            else:
                                mouse.release(event['button'])
                        elif event['event_type'] == 'WheelEvent':
                            mouse.wheel(event['delta'])
                    
                    elif event['type'] == 'keyboard':
                        keyboard.press(event['key'])
                        keyboard.release(event['key'])
                
                if not self.loop_playback:
                    break
                
            self.root.after(0, self._playback_finished)
        except Exception as e:
            self.root.after(0, lambda: self._playback_finished(f"Error: {str(e)}"))
    
    def stop_playback(self):
        self.playing = False
        self.stop_button.pack_forget()
        self._playback_finished("Playback stopped")
    
    def _playback_finished(self, message=None):
        self.playing = False
        self.record_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        self.load_button.config(state=tk.NORMAL)
        self.stop_button.pack_forget()
        keyboard.unhook_all()
        
        if message:
            self.status_label.config(text=f"Status: {message}")
        else:
            self.status_label.config(text="Status: Playback completed")
    
    def toggle_loop(self):
        self.loop_playback = self.loop_var.get()
    
    def save_recording(self):
        if not self.recorded_events:
            messagebox.showwarning("Warning", "No events to save")
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile="recording.json"
            )
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(self.recorded_events, f, indent=2)
                self.status_label.config(text=f"Status: Saved to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def load_recording(self):
        if self.recording or self.playing:
            messagebox.showwarning("Warning", "Cannot load while recording or playing")
            return
            
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, 'r') as f:
                    self.recorded_events = json.load(f)
                self.play_button.config(state=tk.NORMAL)
                self.save_button.config(state=tk.NORMAL)
                self.status_label.config(text=f"Status: Loaded {len(self.recorded_events)} events")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseRecorder(root)
    
    # Optional: Set app icon if you have one
    try:
        root.iconbitmap('mouse_icon.ico')
    except:
        pass
    
    root.mainloop()
