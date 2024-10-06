import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tkinter.font as tkFont
import time
from ttkthemes import ThemedTk
from idlelib.tooltip import Hovertip
from pathlib import Path
import glob
import hashlib

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Convert processed_files to a dictionary if it's a list
            if isinstance(config.get("processed_files"), list):
                config["processed_files"] = {file: "" for file in config["processed_files"]}
            return config
    else:
        return {"outputs_path": "", "prompts_path": "", "processed_files": {}}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

class PromptExtractionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Prompt Extraction GUI V3")
        self.root.geometry("900x700")
        self.config = load_config()

        self.create_widgets()

    def create_widgets(self):
        self.root.configure(bg="#2C3E50")  # Dark blue background

        # Title
        title_font = tkFont.Font(family="Helvetica", size=28, weight="bold")
        title_label = tk.Label(self.root, text="Prompt Extraction GUI", font=title_font, fg="#ECF0F1", bg="#2C3E50")
        title_label.grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

        # Version
        version_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        version_label = tk.Label(self.root, text="V3", font=version_font, fg="#E74C3C", bg="#2C3E50")
        version_label.grid(row=0, column=2, pady=20, sticky="ne")

        # Subtitle
        subtitle_font = tkFont.Font(family="Helvetica", size=12, slant="italic")
        subtitle_label = tk.Label(self.root, text="Extract prompts from markdown files into your prompt library", 
                                  font=subtitle_font, fg="#ECF0F1", bg="#2C3E50", wraplength=700)
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=5, sticky="n")

        # Instructions
        instructions_font = tkFont.Font(family="Helvetica", size=10)
        instructions_label = tk.Label(self.root, 
                                      text="Set paths, then click 'Extract Prompts'. The GUI will process files and save your paths.\nAlways backup before running!",
                                      font=instructions_font, fg="#F39C12", bg="#2C3E50", wraplength=700)
        instructions_label.grid(row=2, column=0, columnspan=3, pady=10, sticky="n")

        # Frame for path entries
        path_frame = tk.Frame(self.root, bg="#34495E", padx=20, pady=20)
        path_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=20, pady=10)

        # Outputs Path Configuration
        self.label_outputs = tk.Label(path_frame, text="Outputs Folder:", fg="#ECF0F1", bg="#34495E")
        self.label_outputs.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.path_outputs = tk.Entry(path_frame, width=60, bg="#ECF0F1", fg="#2C3E50")
        self.path_outputs.grid(row=0, column=1, padx=10, pady=10)
        self.path_outputs.insert(0, self.config["outputs_path"])

        self.button_browse_outputs = tk.Button(path_frame, text="Browse", command=self.set_outputs_path,
                                               bg="#3498DB", fg="#ECF0F1", activebackground="#2980B9")
        self.button_browse_outputs.grid(row=0, column=2, padx=10, pady=10)

        # Prompts Path Configuration
        self.label_prompts = tk.Label(path_frame, text="Prompts Folder:", fg="#ECF0F1", bg="#34495E")
        self.label_prompts.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.path_prompts = tk.Entry(path_frame, width=60, bg="#ECF0F1", fg="#2C3E50")
        self.path_prompts.grid(row=1, column=1, padx=10, pady=10)
        self.path_prompts.insert(0, self.config["prompts_path"])

        self.button_browse_prompts = tk.Button(path_frame, text="Browse", command=self.set_prompts_path,
                                               bg="#3498DB", fg="#ECF0F1", activebackground="#2980B9")
        self.button_browse_prompts.grid(row=1, column=2, padx=10, pady=10)

        # Buttons frame
        button_frame = tk.Frame(self.root, bg="#2C3E50")
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)

        # Extract button
        self.button_extract = tk.Button(button_frame, text="Extract Prompts", command=self.extract_prompts,
                                        bg="#2ECC71", fg="#ECF0F1", activebackground="#27AE60", 
                                        font=("Helvetica", 12, "bold"), padx=20, pady=10)
        self.button_extract.pack(side=tk.LEFT, padx=10)

        # Reset button
        self.button_reset_paths = tk.Button(button_frame, text="Reset Paths", command=self.reset_paths,
                                            bg="#E74C3C", fg="#ECF0F1", activebackground="#C0392B",
                                            font=("Helvetica", 12), padx=20, pady=10)
        self.button_reset_paths.pack(side=tk.LEFT, padx=10)

        # Tooltips
        Hovertip(self.button_browse_outputs, "Set the Outputs folder where markdown files are stored.")
        Hovertip(self.button_browse_prompts, "Set the Prompts folder where extracted prompts will be saved.")
        Hovertip(self.button_extract, "Start extracting prompts from markdown files.")
        Hovertip(self.button_reset_paths, "Clear both paths and reset to default.")

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=700, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, pady=10)

        # Log Frame
        log_frame = tk.Frame(self.root, bg="#34495E", padx=10, pady=10)
        log_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=20, pady=10)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)

        # Log
        self.log_text = tk.Text(log_frame, wrap="word", height=15, bg="#ECF0F1", fg="#2C3E50")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for Log
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # Status Label
        self.status_label = tk.Label(self.root, text="Status: Idle", fg="#ECF0F1", bg="#2C3E50")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=10)

        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(6, weight=1)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def set_outputs_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_outputs.delete(0, tk.END)
            self.path_outputs.insert(0, folder)
            self.config["outputs_path"] = folder
            save_config(self.config)

    def set_prompts_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_prompts.delete(0, tk.END)
            self.path_prompts.insert(0, folder)
            self.config["prompts_path"] = folder
            save_config(self.config)

    def reset_paths(self):
        self.path_outputs.delete(0, tk.END)
        self.path_prompts.delete(0, tk.END)
        self.config["outputs_path"] = ""
        self.config["prompts_path"] = ""
        save_config(self.config)
        messagebox.showinfo("Reset", "Paths have been reset. Please set new paths.")

    def extract_prompts(self):
        outputs_path = self.path_outputs.get()
        prompts_path = self.path_prompts.get()

        if not os.path.exists(outputs_path) or not os.path.exists(prompts_path):
            messagebox.showerror("Error", "Please ensure both folders are set correctly.")
            return

        processed_files = self.config.get("processed_files", {})
        new_processed_files = {}

        count = 0
        files = glob.glob(os.path.join(outputs_path, "**/*.md"), recursive=True)
        self.progress["maximum"] = len(files)
        self.log("Starting prompt extraction process...")

        for idx, file_path in enumerate(files):
            file_hash = self.get_file_hash(file_path)
            if file_hash != processed_files.get(file_path, ""):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                prompt_text = self.extract_prompt(content)
                if prompt_text:
                    relative_path = os.path.relpath(file_path, outputs_path)
                    prompt_file = os.path.join(prompts_path, relative_path.replace(".md", "_prompt.md"))
                    os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
                    with open(prompt_file, 'w', encoding='utf-8') as prompt_f:
                        prompt_f.write(f"# Prompt\n\n{prompt_text}\n")
                    new_processed_files[file_path] = file_hash
                    count += 1
                    self.log(f"Extracted prompt from: {relative_path}")
                    self.log(f"Prompt preview: {prompt_text[:100]}...")
            else:
                self.log(f"Skipping already processed file: {os.path.relpath(file_path, outputs_path)}")

            self.progress["value"] = idx + 1
            self.status_label.config(text=f"Processing {idx+1}/{len(files)} files")
            self.root.update_idletasks()

        # Update the processed files list and save config
        self.config["processed_files"].update(new_processed_files)
        save_config(self.config)

        # Show confirmation message
        self.log(f"Extraction complete: {count} prompts extracted.")
        messagebox.showinfo("Success", f"{count} prompts were extracted.")
        self.status_label.config(text="Status: Done")

    def extract_prompt(self, content):
        start = content.find("# Prompt")
        end = content.find("# Output")
        if start != -1 and end != -1:
            return content[start + len("# Prompt"):end].strip()
        return None

    def get_file_hash(self, file_path):
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    gui = PromptExtractionGUI(root)
    root.mainloop()