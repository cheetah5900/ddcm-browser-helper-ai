import customtkinter as ctk
import threading
import time
import os
import zipfile
import shutil
import json
from browser_bot import BrowserBot
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration ---
CONFIG_FILE = "config_win.json" if os.name == 'nt' else "config_mac.json"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Browser Controller")
        self.geometry("1400x650") # Widen to support side-by-side file tools
        
        # Initialize the bot
        self.bot = BrowserBot()

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title area
        self.grid_rowconfigure(1, weight=1) # Controls area

        # Title
        self.label = ctk.CTkLabel(self, text="Browser Controller", font=("Arial", 20, "bold"))
        self.label.grid(row=0, column=0, padx=20, pady=20)

        # Controls Frame (Main Container)
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        # Configure columns for horizontal layout
        self.controls_frame.grid_columnconfigure(0, weight=0) # Canva
        self.controls_frame.grid_columnconfigure(1, weight=1) # File Tools (Expands)
        self.controls_frame.grid_columnconfigure(2, weight=0) # Etsy
        self.controls_frame.grid_columnconfigure(3, weight=0) # Gemini

        # === COLUMN 0: Canva Automation ===
        self.frame_canva = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.frame_canva.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_canva.grid_columnconfigure(0, weight=1)

        self.lbl_canva = ctk.CTkLabel(self.frame_canva, text="Canva Automation", font=("Arial", 16, "bold"))
        self.lbl_canva.grid(row=0, column=0, pady=(10, 15), sticky="w")

        # PNG Config
        self.entry_png_pages = ctk.CTkEntry(self.frame_canva, placeholder_text="Pages (e.g. 1-4)", width=140)
        self.entry_png_pages.insert(0, "1-4")
        self.entry_png_pages.grid(row=1, column=0, pady=(10, 0), sticky="w")

        self.btn_export = ctk.CTkButton(self.frame_canva, text="Export PNG", width=140, command=self.action_export_png, fg_color="#00C4CC")
        self.btn_export.grid(row=2, column=0, pady=(5, 10), sticky="w")

        # JPG Config
        self.entry_jpg_pages = ctk.CTkEntry(self.frame_canva, placeholder_text="Pages (e.g. 6-9)", width=140)
        self.entry_jpg_pages.insert(0, "6-9")
        self.entry_jpg_pages.grid(row=3, column=0, pady=(10, 0), sticky="w")

        self.btn_export_jpg = ctk.CTkButton(self.frame_canva, text="Export JPG", width=140, command=self.action_export_jpg, fg_color="#00C4CC")
        self.btn_export_jpg.grid(row=4, column=0, pady=(5, 10), sticky="w")
        
        # PDF Config
        self.entry_pdf_pages = ctk.CTkEntry(self.frame_canva, placeholder_text="Pages (e.g. 10)", width=140)
        self.entry_pdf_pages.insert(0, "10")
        self.entry_pdf_pages.grid(row=5, column=0, pady=(10, 0), sticky="w")

        self.btn_export_pdf = ctk.CTkButton(self.frame_canva, text="Export PDF", width=140, command=self.action_export_pdf, fg_color="#E04F5F")
        self.btn_export_pdf.grid(row=6, column=0, pady=(5, 10), sticky="w")

        self.btn_export_all = ctk.CTkButton(self.frame_canva, text="Export ALL", width=140, command=self.action_export_all, fg_color="#005F99")
        self.btn_export_all.grid(row=7, column=0, pady=10, sticky="w")


        # === COLUMN 1: File Tools ===
        self.frame_files = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.frame_files.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.lbl_files = ctk.CTkLabel(self.frame_files, text="File Tools", font=("Arial", 16, "bold"))
        self.lbl_files.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="w")

        # Container for side-by-side layout
        self.files_container = ctk.CTkFrame(self.frame_files, fg_color="transparent")
        self.files_container.grid(row=1, column=0, sticky="nsew")

        # --- LEFT SIDE: Inputs ---
        self.files_left = ctk.CTkFrame(self.files_container, fg_color="transparent")
        self.files_left.grid(row=0, column=0, padx=(0, 20), sticky="n")

        # Folder Name
        self.lbl_folder_name = ctk.CTkLabel(self.files_left, text="Folder Name", font=("Arial", 10))
        self.lbl_folder_name.grid(row=0, column=0, sticky="w")
        self.entry_folder_name = ctk.CTkEntry(self.files_left, placeholder_text="Folder Name", width=300)
        self.entry_folder_name.grid(row=1, column=0, pady=(0, 10), sticky="ew")

        # Element Name
        self.lbl_element_name = ctk.CTkLabel(self.files_left, text="Element Name (optional)", font=("Arial", 10))
        self.lbl_element_name.grid(row=2, column=0, sticky="w")
        self.entry_element_name = ctk.CTkEntry(self.files_left, placeholder_text="Element Name", width=300)
        self.entry_element_name.insert(0, "Songkran")
        self.entry_element_name.grid(row=3, column=0, pady=(0, 10), sticky="ew")

        # Element Path
        self.lbl_element_path = ctk.CTkLabel(self.files_left, text="Element Path", font=("Arial", 10))
        self.lbl_element_path.grid(row=4, column=0, sticky="w")
        self.entry_element_path = ctk.CTkEntry(self.files_left, placeholder_text="Element Path", width=300)
        self.entry_element_path.grid(row=5, column=0, pady=(0, 10), sticky="ew")

        # Local Path Config
        self.lbl_local_path = ctk.CTkLabel(self.files_left, text="Local Path (Original, Preview, etc.)", font=("Arial", 10))
        self.lbl_local_path.grid(row=6, column=0, sticky="w")
        self.entry_local_path = ctk.CTkEntry(self.files_left, placeholder_text="Local Path", width=300)
        self.entry_local_path.grid(row=7, column=0, pady=(0, 10), sticky="ew")
        
        # Remote Path Config
        self.lbl_remote_path = ctk.CTkLabel(self.files_left, text="Remote Path (4000x4000, Sticker Set)", font=("Arial", 10))
        self.lbl_remote_path.grid(row=8, column=0, sticky="w")
        self.entry_remote_path = ctk.CTkEntry(self.files_left, placeholder_text="Remote Path", width=300)
        self.entry_remote_path.grid(row=9, column=0, pady=(0, 10), sticky="ew")

        # Set as Default Button
        self.btn_set_default = ctk.CTkButton(self.files_left, text="Set Paths as Default", width=140, command=self.action_save_defaults, fg_color="#5D6D7E")
        self.btn_set_default.grid(row=10, column=0, pady=(5, 10), sticky="w")

        # --- RIGHT SIDE: Actions ---
        self.files_right = ctk.CTkFrame(self.files_container, fg_color="transparent")
        self.files_right.grid(row=0, column=1, sticky="n")

        self.btn_create_folders = ctk.CTkButton(self.files_right, text="Create Folders", width=140, command=self.action_create_folders, fg_color="#27AE60")
        self.btn_create_folders.grid(row=0, column=0, pady=(0, 0), sticky="w")
        self.lbl_desc_create = ctk.CTkLabel(self.files_right, text="สร้างโฟลเดอร์ที่ Local และ Remote โดยจะมีโฟลเดอร์ที่จำเป็นสำหรับแต่ละฝั่ง เช่น 4000x4000, Sticker Set เป็นต้น", font=("Arial", 10), wraplength=350, justify="left")
        self.lbl_desc_create.grid(row=1, column=0, pady=(0, 5), sticky="w")

        self.btn_copy_upscale = ctk.CTkButton(self.files_right, text="Copy upscale img", width=140, command=self.action_copy_upscale, fg_color="#8E44AD")
        self.btn_copy_upscale.grid(row=2, column=0, pady=(5, 0), sticky="w")
        self.lbl_desc_copy_upscale = ctk.CTkLabel(self.files_right, text="1. เข้าไปที่ [Local Path] > [Folder Name] > Original > upscayl_png_remacri-4x_4x เพื่อคัดลอกไฟล์มาที่ 4000x4000 และลบโฟลเดอร์ต้นทางทิ้ง\n2. เข้าไปที่ [Element Path] > [Element Name] เพื่อคัดลอกไฟล์องค์ประกอบเสริมมาวางรวมไว้ที่ 4000x4000", font=("Arial", 10), wraplength=350, justify="left")
        self.lbl_desc_copy_upscale.grid(row=3, column=0, pady=(0, 5), sticky="w")

        self.btn_local_remote = ctk.CTkButton(self.files_right, text="Local to Remote", width=140, command=self.action_local_remote, fg_color="#3498DB")
        self.btn_local_remote.grid(row=4, column=0, pady=(5, 0), sticky="w")
        self.lbl_desc_local_remote = ctk.CTkLabel(self.files_right, text="คัดลอก 4000x4000, Sticker Set ไป Remote Path", font=("Arial", 10), wraplength=350, justify="left")
        self.lbl_desc_local_remote.grid(row=5, column=0, pady=(0, 5), sticky="w")

        self.btn_unzip = ctk.CTkButton(self.files_right, text="Unzip Downloads", width=140, command=self.action_unzip_downloads, fg_color="#FFA500")
        self.btn_unzip.grid(row=6, column=0, pady=(5, 0), sticky="w")
        self.lbl_desc_unzip = ctk.CTkLabel(self.files_right, text="แตกไฟล์ Zip จากโฟลเดอร์ Download", font=("Arial", 10), wraplength=350, justify="left")
        self.lbl_desc_unzip.grid(row=7, column=0, pady=(0, 10), sticky="w")
        

        # === COLUMN 2: Etsy and DDMC ===
        self.frame_etsy = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.frame_etsy.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.frame_etsy.grid_columnconfigure(0, weight=1)

        self.lbl_etsy = ctk.CTkLabel(self.frame_etsy, text="Etsy and DDMC", font=("Arial", 16, "bold"))
        self.lbl_etsy.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="w")

        self.entry_primary = ctk.CTkEntry(self.frame_etsy, placeholder_text="Primary Color", width=100)
        self.entry_primary.insert(0, "Red")
        self.entry_primary.grid(row=1, column=0, padx=5, pady=10, sticky="w")
        
        self.entry_secondary = ctk.CTkEntry(self.frame_etsy, placeholder_text="Secondary Color", width=100)
        self.entry_secondary.insert(0, "Gray")
        self.entry_secondary.grid(row=2, column=0, padx=5, pady=10, sticky="w")

        self.btn_etsy = ctk.CTkButton(self.frame_etsy, text="Create Listing", width=140, command=self.action_etsy_listing, fg_color="#F1641E")
        self.btn_etsy.grid(row=3, column=0, pady=20, sticky="w")


        # === COLUMN 3: Gemini Automation ===
        self.frame_gemini = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.frame_gemini.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")
        self.frame_gemini.grid_columnconfigure(0, weight=1)

        self.lbl_gemini = ctk.CTkLabel(self.frame_gemini, text="Gemini Automation", font=("Arial", 16, "bold"))
        self.lbl_gemini.grid(row=0, column=0, pady=(10, 15), sticky="w")

        self.entry_gemini_count = ctk.CTkEntry(self.frame_gemini, placeholder_text="Count", width=80)
        self.entry_gemini_count.insert(0, "5")
        self.entry_gemini_count.grid(row=1, column=0, pady=10, sticky="w")

        self.btn_gemini = ctk.CTkButton(self.frame_gemini, text="Gen Characters", width=120, command=self.action_gemini_gen, fg_color="#8E44AD")
        self.btn_gemini.grid(row=2, column=0, pady=5, sticky="w")

        self.btn_gemini_elements = ctk.CTkButton(self.frame_gemini, text="Gen Elements", width=120, command=self.action_gemini_elements, fg_color="#8E44AD")
        self.btn_gemini_elements.grid(row=3, column=0, pady=5, sticky="w")

        self.btn_download_imgs = ctk.CTkButton(self.frame_gemini, text="Download images", width=120, command=self.action_download_images, fg_color="#2E86C1")
        self.btn_download_imgs.grid(row=4, column=0, pady=5, sticky="w")


        # --- Status Section ---
        self.status_label = ctk.CTkLabel(self, text="Connecting...", text_color="orange")
        self.status_label.grid(row=2, column=0, pady=10)
        
        # Load Defaults and Start browser
        self.load_defaults()
        self.start_browser_thread()

    def action_save_defaults(self):
        """Saves current paths to a config file."""
        config = {
            "element_path": self.entry_element_path.get().strip(),
            "local_path": self.entry_local_path.get().strip(),
            "remote_path": self.entry_remote_path.get().strip()
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            self.log("Defaults saved successfully!")
        except Exception as e:
            self.log(f"Error saving defaults: {e}", error=True)

    def load_defaults(self):
        """Loads paths from config file or sets system-appropriate defaults."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.entry_element_path.insert(0, config.get("element_path", ""))
                    self.entry_local_path.insert(0, config.get("local_path", ""))
                    self.entry_remote_path.insert(0, config.get("remote_path", ""))
                return
            except:
                pass
        
        # System defaults (Fallback)
        if os.name == 'nt': # Windows
            self.entry_element_path.insert(0, r"C:\Files\Project\local DDCM\Elements")
            self.entry_local_path.insert(0, r"C:\Files\Project\local DDCM")
            self.entry_remote_path.insert(0, r"G:\My Drive\Projects\DDCM\Cliparts DDCM")
        else: # macOS/Linux
            home = os.path.expanduser("~")
            self.entry_element_path.insert(0, os.path.join(home, "Documents/DDCM/Elements"))
            self.entry_local_path.insert(0, os.path.join(home, "Documents/DDCM"))
            self.entry_remote_path.insert(0, "/Volumes/GoogleDrive/My Drive/Projects/DDCM/Cliparts DDCM")

    def action_gemini_gen(self):
        """Starts the Gemini generation process for characters."""
        threading.Thread(target=self._run_gemini_gen, args=("characters",)).start()

    def action_gemini_elements(self):
        """Starts the Gemini generation process for elements."""
        threading.Thread(target=self._run_gemini_gen, args=("elements",)).start()

    def action_download_images(self):
        """Starts the Gemini image download process."""
        threading.Thread(target=self._run_download_images).start()

    def _run_download_images(self):
        try:
            self.log("Starting Image Download...")
            
            # 1. Switch to Gemini
            gemini_url = "gemini.google.com/app"
            found_gemini = False
            for handle in self.bot.driver.window_handles:
                self.bot.driver.switch_to.window(handle)
                if gemini_url in self.bot.driver.current_url:
                    found_gemini = True
                    break
            
            if not found_gemini:
                self.log("Error: Gemini tab not found!", error=True)
                return

            time.sleep(1)

            # 2. Scroll to TOP
            self.log("Scrolling to TOP...")
            self.bot.driver.execute_script("window.scrollTo(0, 0);")
            scrollers = self.bot.driver.find_elements(By.CSS_SELECTOR, ".infinite-scroller, .conversation-container, main")
            for s in scrollers:
                self.bot.driver.execute_script("arguments[0].scrollTop = 0;", s)
            
            time.sleep(2)

            # 3. Find Download Buttons
            buttons = self.bot.driver.find_elements(By.CSS_SELECTOR, "download-generated-image-button > button")
            if not buttons:
                self.log("No download buttons found initially. Trying to scroll down a bit...", error=False)
                self.bot.driver.execute_script("window.scrollTo(0, 1000);")
                time.sleep(1)
                buttons = self.bot.driver.find_elements(By.CSS_SELECTOR, "download-generated-image-button > button")

            if not buttons:
                self.log("Error: No download buttons found.", error=True)
                return

            self.log(f"Found {len(buttons)} images to download.")

            count = len(buttons)
            for i, btn in enumerate(buttons):
                self.log(f"Downloading image {i+1}/{count}...")
                
                try:
                    self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(0.5)
                    try:
                        btn.click()
                    except:
                        self.bot.driver.execute_script("arguments[0].click();", btn)
                    
                    try:
                        time.sleep(1) 
                        WebDriverWait(self.bot.driver, 15).until(
                             EC.element_to_be_clickable(btn)
                        )
                    except:
                        self.log(f"Warning: Button {i+1} didn't return to clickable state quickly.", error=False) 

                except Exception as e:
                    self.log(f"Error clicking btn {i}: {e}", error=True)

            self.log("Download sequence finished.")

        except Exception as e:
             self.log(f"Error: {e}", error=True)

    def _run_gemini_gen(self, mode="characters"):
        try:
            self.log(f"Starting Gemini Gen ({mode})...")

            # 1. Switch to DDCM
            ddcm_url = "ddcm.litarandfriends.uk"
            found_ddcm = False
            for handle in self.bot.driver.window_handles:
                self.bot.driver.switch_to.window(handle)
                if ddcm_url in self.bot.driver.current_url:
                    found_ddcm = True
                    break
            
            if not found_ddcm:
                self.log("Error: DDCM tab not found! Please open it.", error=True)
                return

            time.sleep(1)

            # 2. Select Containers based on Mode
            containers = []
            if mode == "characters":
                containers = [
                    ("Set 1", "body > main > div.modal-overlay > div > div:nth-child(2) > div:nth-child(13) > div > div > div > div:nth-child(1) > div:nth-child(2)"),
                    ("Set 2", "body > main > div.modal-overlay > div > div:nth-child(2) > div:nth-child(13) > div > div > div > div:nth-child(2) > div:nth-child(2)")
                ]
            elif mode == "elements":
                containers = [
                    ("Elements", "body > main > div.modal-overlay > div > div:nth-child(2) > div:nth-child(13) > div > div > div > div:nth-child(3) > div:nth-child(2)")
                ]
            else:
                self.log("Unknown mode.", error=True)
                return

            all_prompts = []
            for name, selector in containers:
                self.log(f"Scanning {name}...")
                try:
                    container = WebDriverWait(self.bot.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
                    time.sleep(0.5)

                    buttons = container.find_elements(By.TAG_NAME, "button")
                    if not buttons:
                         buttons = container.find_elements(By.XPATH, ".//button")
                    
                    if len(buttons) > 0:
                        for i, btn in enumerate(buttons):
                            try:
                                self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                try: btn.click()
                                except: self.bot.driver.execute_script("arguments[0].click();", btn)
                                time.sleep(0.1)
                                try:
                                    text = self.clipboard_get()
                                    if text: all_prompts.append(text)
                                except: pass
                            except Exception as e:
                                print(f"Error btn {i}: {e}")
                except Exception as e:
                    self.log(f"Error {name}: {e}", error=True)

            self.log(f"Collected {len(all_prompts)} prompts. Switching to Gemini...")
            
            if not all_prompts:
                self.log("No prompts collected. Stopping.")
                return

            # 3. Switch to Gemini
            found_gemini = False
            for handle in self.bot.driver.window_handles:
                self.bot.driver.switch_to.window(handle)
                if "gemini.google.com/app" in self.bot.driver.current_url:
                    found_gemini = True
                    break
            
            if not found_gemini:
                self.log("Error: Gemini tab not found!", error=True)
                return

            time.sleep(1)

            # 4. Input Prompts loop
            input_box_xpath = "//div[contains(@class, 'ql-editor') and @contenteditable='true']"
            for i, prompt in enumerate(all_prompts):
                self.log(f"Processing Gemini {i+1}/{len(all_prompts)}...")
                try:
                    input_box = WebDriverWait(self.bot.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, input_box_xpath))
                    )
                    input_box.click()
                    input_box.send_keys(prompt)
                    time.sleep(1)
                    input_box.send_keys(Keys.ENTER)
                    
                    self.log(f"  -> Sent prompt {i+1}. Waiting for generation...")
                    time.sleep(2)

                    stop_icon_xpath = "//mat-icon[contains(@data-mat-icon-name, 'stop') or @fonticon='stop']"
                    while True:
                        try:
                            self.bot.driver.find_element(By.XPATH, stop_icon_xpath)
                            time.sleep(1)
                        except:
                            self.log("  -> Generation finished.")
                            break
                except Exception as e:
                    self.log(f"Error in Gemini loop: {e}", error=True)
                    return

            self.log("Gemini Automation Complete!", error=False)

        except Exception as e:
            self.log(f"Critical Error: {e}", error=True)

    def log(self, message, error=False):
        color = "red" if error else "SystemButtonFace"
        if "SystemButtonFace" == color:
             color = "gray"
        self.status_label.configure(text=message, text_color=color)
        print(message)

    def start_browser_thread(self):
        """Runs browser start in a separate thread to keep GUI responsive."""
        threading.Thread(target=self._start_browser_task).start()

    def _start_browser_task(self):
        success = self.bot.start_browser(attach=True)
        if success:
            self.log("Connected to Browser.")
            self.status_label.configure(text_color="green")
        else:
            self.log("Failed: Please Close ALL Chrome Windows & Restart App", error=True)

    def action_export_png(self):
        """Defines the sequence for Export PNG on Canva."""
        self.log("Running Export PNG...")
        if not self.bot.switch_to_tab_containing("canva.com"):
            self.log("Error: 'canva.com' is not open in any tab.")
            return

        time.sleep(1)
        pages = self.entry_png_pages.get().strip() or "1-4"
        steps = [
            ("Rename Design to 'png'", "//input[@aria-label='Design title']", "png"),
            ("Click Share/Export", "//button[.//span[text()='Share']]"),
            ("Click Download", "//button[@aria-label='Download']"),
            ("Click File Type", "//button[@aria-label='File type']"),
            ("Select PNG", "//li[@role='option']//div[contains(text(), 'PNG')]"),
            ("Set Size to 1", "//input[@role='spinbutton']", "1"), 
            ("Click Transparent", "//label[.//p[contains(text(), 'Transparent background')]]"),
            (f"Set Pages to {pages}", "//input[@placeholder='Select pages']", pages),
            ("Final Download", "//button[@type='submit'][.//span[contains(text(), 'Download')]]")
        ]

        if not self._execute_steps(steps):
             self.log("Export PNG Failed. Stopping sequence.", error=True)
             return False
        
        self.log("Export PNG sequence completed.")
        return True

    def action_export_jpg(self):
        """Defines the sequence for Export JPG on Canva."""
        self.log("Running Export JPG...")
        if not self.bot.switch_to_tab_containing("canva.com"):
            self.log("Error: 'canva.com' is not open in any tab.")
            return False

        time.sleep(1)
        pages = self.entry_jpg_pages.get().strip() or "6-9"
        steps = [
            ("Rename Design to 'jpg'", "//input[@aria-label='Design title']", "jpg"),
            ("Click Share/Export", "//button[.//span[text()='Share']]"),
            ("Click Download", "//button[@aria-label='Download']"),
            ("Click File Type", "//button[@aria-label='File type']"),
            ("Select JPG", "//li[@role='option']//div[contains(text(), 'JPG')]"),
            ("Set Size to 0.5", "//input[@role='spinbutton']", "0.5"),
            (f"Set Pages to {pages}", "//input[@placeholder='Select pages']", pages),
            ("Final Download", "//button[@type='submit'][.//span[contains(text(), 'Download')]]")
        ]

        if not self._execute_steps(steps):
             self.log("Export JPG Failed. Stopping sequence.", error=True)
             return False

        self.log("Export JPG sequence completed.")
        return True

    def action_export_pdf(self):
        """Defines the sequence for Export PDF (Standard) on Canva."""
        self.log("Running Export PDF...")
        if not self.bot.switch_to_tab_containing("canva.com"):
            self.log("Error: 'canva.com' is not open in any tab.")
            return False

        time.sleep(1)
        pages = self.entry_pdf_pages.get().strip() or "10"
        steps = [
            ("Rename Design to 'pdf_for_downloading'", "//input[@aria-label='Design title']", "pdf_for_downloading"),
            ("Click Share/Export", "//button[.//span[text()='Share']]"),
            ("Click Download", "//button[@aria-label='Download']"),
            ("Click File Type", "//button[@aria-label='File type']"),
            ("Select PDF Standard", "//li[@role='option']//div[contains(text(), 'PDF Standard')]"),
            (f"Set Pages to {pages}", "//input[@placeholder='Select pages']", pages),
            ("Final Download", "//button[@type='submit'][.//span[contains(text(), 'Download')]]")
        ]

        if not self._execute_steps(steps):
             self.log("Export PDF Failed. Stopping sequence.", error=True)
             return False
        
        self.log("Export PDF sequence completed.")
        return True

    def action_export_all(self):
        """Runs PNG, JPG, and PDF export sequences."""
        self.log("Starting ALL Exports (PNG + JPG + PDF)...")
        if not self.action_export_png():
             return

        time.sleep(8) 
        if not self.action_export_jpg():
             return

        time.sleep(8)
        if not self.action_export_pdf():
             return
        
        self.log("ALL Exports Completed Successfully!")

    def action_create_folders(self):
        """Creates folder structures based on user input."""
        folder_name = self.entry_folder_name.get().strip()
        if not folder_name:
             self.log("Error: Folder Name is required.", error=True)
             return

        configs = [
            {
                "path": self.entry_local_path.get().strip(),
                "folder": folder_name,
                "subfolders": ["4000x4000", "Download file", "Original", "Preview", "Sticker Set"]
            },
            {
                "path": self.entry_remote_path.get().strip(),
                "folder": folder_name,
                "subfolders": ["4000x4000", "Sticker Set"]
            }
        ]

        for i, config in enumerate(configs):
            base_path = config["path"]
            folder_name = config["folder"]
            subfolders = config["subfolders"]
            if not base_path or not folder_name:
                continue

            full_path = os.path.join(base_path, folder_name)
            try:
                if os.path.exists(full_path):
                    self.log(f"'{folder_name}' already exists in Path {i+1}. Skipping.")
                else:
                    os.makedirs(full_path)
                    for sub in subfolders:
                        os.makedirs(os.path.join(full_path, sub))
                    self.log(f"Created '{folder_name}' and subfolders in Path {i+1}.")
            except Exception as e:
                self.log(f"Error creating folders for Path {i+1}: {e}", error=True)

    def action_copy_upscale(self):
        """Copies files from upscayl folder to 4000x4000 in Local Path."""
        folder_name = self.entry_folder_name.get().strip()
        local_path = self.entry_local_path.get().strip()
        
        if not folder_name or not local_path:
            self.log("Error: Folder Name and Local Path are required.", error=True)
            return

        dest_dir = os.path.join(local_path, folder_name, "4000x4000")
        src_dir = os.path.join(local_path, folder_name, "Original", "upscayl_png_remacri-4x_4x")
        
        if os.path.exists(src_dir):
            os.makedirs(dest_dir, exist_ok=True)
            try:
                count = 0
                for item in os.listdir(src_dir):
                    s = os.path.join(src_dir, item)
                    d = os.path.join(dest_dir, item)
                    if os.path.isfile(s):
                        shutil.copy2(s, d)
                        count += 1
                shutil.rmtree(src_dir)
                self.log(f"Copied {count} files to 4000x4000.")
            except Exception as e:
                self.log(f"Error copying upscale images: {e}", error=True)

        element_name = self.entry_element_name.get().strip()
        element_path = self.entry_element_path.get().strip()
        if element_name and element_path:
            element_src_dir = os.path.join(element_path, element_name)
            if os.path.exists(element_src_dir):
                os.makedirs(dest_dir, exist_ok=True)
                try:
                    elem_count = 0
                    for item in os.listdir(element_src_dir):
                        s = os.path.join(element_src_dir, item)
                        d = os.path.join(dest_dir, item)
                        if os.path.isfile(s):
                            shutil.copy2(s, d)
                            elem_count += 1
                    self.log(f"Copied {elem_count} element files.")
                except Exception as e:
                    self.log(f"Error copying elements: {e}", error=True)

    def action_local_remote(self):
        """Copies folders from Local Path to Remote Path."""
        folder_name = self.entry_folder_name.get().strip()
        local_path = self.entry_local_path.get().strip()
        remote_path = self.entry_remote_path.get().strip()
        
        if not folder_name or not local_path or not remote_path:
            self.log("Error: All paths required.", error=True)
            return
            
        folders_to_copy = ["4000x4000", "Sticker Set"]
        total_copied = 0
        try:
            for subfolder in folders_to_copy:
                src_dir = os.path.join(local_path, folder_name, subfolder)
                dest_dir = os.path.join(remote_path, folder_name, subfolder)
                if not os.path.exists(src_dir):
                    continue
                os.makedirs(dest_dir, exist_ok=True)
                for item in os.listdir(src_dir):
                    s = os.path.join(src_dir, item)
                    d = os.path.join(dest_dir, item)
                    if os.path.isfile(s):
                        shutil.copy2(s, d)
                        total_copied += 1
            self.log(f"Copied {total_copied} files to Remote Path.")
        except Exception as e:
            self.log(f"Error copying to remote: {e}", error=True)

    def action_etsy_listing(self):
        """Extracts data from DDCM and populates Etsy."""
        self.log("Starting Etsy Listing process...")
        user_primary = self.entry_primary.get().strip()
        user_secondary = self.entry_secondary.get().strip()
        if not all([user_primary, user_secondary]):
            self.log("Error: Colors required!", error=True)
            return

        if not self.bot.switch_to_tab_containing("ddcm.litarandfriends.uk"):
            self.bot.driver.get("https://ddcm.litarandfriends.uk")
            time.sleep(2)

        ddcm_fields = [
            ("name", "/html/body/main/div[4]/div/div[2]/div[2]/div/div/div"),
            ("tag", "/html/body/main/div[4]/div/div[2]/div[10]/div/div/div"), 
            ("material", "/html/body/main/div[4]/div/div[2]/div[11]/div/div/div/div"), 
            ("description", "/html/body/main/div[4]/div/div[2]/div[12]/div/div/div/div"),
            ("theme", "/html/body/main/div[4]/div/div[2]/div[5]/div/div/div"),
            ("price", "/html/body/main/div[4]/div/div[2]/div[8]/div/div/div")
        ]

        extracted_data = {}
        for field_name, xpath in ddcm_fields:
            try:
                element = WebDriverWait(self.bot.driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
                extracted_data[field_name] = element.text.strip()
            except:
                self.log(f"Extraction error: {field_name}", error=True)
                return

        user_price = extracted_data.get('price', '5.99') or "5.99"
        user_section = extracted_data.get('theme', 'General') or "General"

        self.bot.driver.switch_to.new_window('tab')
        self.bot.driver.get("https://www.etsy.com/your/shops/me/listing-editor/create")
        
        setup_steps = [
            ("Select Category: Clip Art", "//div[contains(@class, 'le-category-action-item') and .//h2[contains(text(), 'Clip Art')]]"),
            ("Click Continue (1)", "//button[contains(@class, 'wt-btn--primary') and text()='Continue']"),
            ("Select Digital Download", "//input[@name='listing_type_options_group' and @value='download']"),
            ("Select 'I did'", "//label[contains(text(), 'I did')]"),
            ("Select 'A supply or tool'", "//label[contains(text(), 'A supply or tool to make things')]"),
            ("Select '2020-2026'", "//select[@id='when-made-select']", "2020_2026"),
            ("Select 'With an AI generator'", "//input[@value='ai_gen']"),
            ("Click Continue (2)", "//button[contains(@class, 'wt-btn--primary') and text()='Continue']")
        ]

        for name, xpath, *value in setup_steps:
            try:
                element = WebDriverWait(self.bot.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.3)
                if value:
                    from selenium.webdriver.support.ui import Select
                    Select(element).select_by_value(value[0])
                else:
                    try: element.click()
                    except: self.bot.driver.execute_script("arguments[0].click();", element)
                time.sleep(0.5)
            except:
                self.log(f"Etsy Setup Error: {name}", error=True)
                return

        content_steps = [
            ("Paste Title", "//textarea[@id='listing-title-input']", extracted_data.get('name', '')),
            ("Paste Description", "//textarea[@id='listing-description-textarea' or @name='description']", extracted_data.get('description', '')),
            ("Paste Price", "//input[@id='listing-price-input']", user_price),
            ("Paste Quantity", "//input[@id='listing-quantity-input']", "999"),
            ("Click Topic Search", "//input[@placeholder='Type to search…' and contains(@aria-describedby, 'attribute-0')]"),
            ("Check Scrapbooking Box", "//label[contains(text(), 'Scrapbooking')]"),
            ("Press ESC", "SPECIAL_ESC"),
            ("Paste Primary Color", "/html/body/div[3]/div/div[1]/main/div/div/form/div/div[3]/div/div[4]/div/div/div[3]/div[3]/div/div/div/div/div[1]/input", user_primary),
            ("Select Primary Color", "//button[@role='menuitemradio']//p[contains(text(), '" + user_primary + "')]"),
            ("Paste Secondary Color", "/html/body/div[3]/div/div[1]/main/div/div/form/div/div[3]/div/div[4]/div/div/div[3]/div[4]/div/div/div/div/div[1]/input", user_secondary),
            ("Select Secondary Color", "//button[@role='menuitemradio']//p[contains(text(), '" + user_secondary + "')]"),
            ("Paste Tag", "//input[@id='listing-tags-input']", extracted_data.get('tag', '')),
            ("Click Add Tag", "//button[@id='listing-tags-button']"),
            ("Paste Material", "//input[@id='listing-materials-input']", extracted_data.get('material', '')),
            ("Click Add Material", "//button[@id='listing-materials-button']"),
            ("Select Shop Section", "//select[@id='shop-section-select']", user_section)
        ]

        for step in content_steps:
            name, xpath = step[0], step[1]
            try:
                if xpath == "SPECIAL_ESC":
                    self.bot.driver.find_element(By.TAG_NAME, "body").click()
                    continue
                element = WebDriverWait(self.bot.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)
                if len(step) == 3:
                    text_value = step[2]
                    if element.tag_name == "select":
                        from selenium.webdriver.support.ui import Select
                        Select(element).select_by_visible_text(text_value)
                    else:
                        element.click()
                        if "placeholder='Type to search…'" in xpath:
                            element.send_keys(Keys.CONTROL + "a", Keys.DELETE, text_value)
                        else:
                            self.bot.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element, text_value)
                else:
                    try: element.click()
                    except: self.bot.driver.execute_script("arguments[0].click();", element)
                time.sleep(0.5)
            except:
                self.log(f"Etsy Content Error: {name}", error=True)
                return
        self.log("Etsy Listing populated successfully!")

    def action_unzip_downloads(self):
        """Unzips zip files in Downloads."""
        self.log("Starting Unzip...")
        try:
            download_path = os.path.join(os.path.expanduser("~"), "Downloads")
            zip_files = [f for f in os.listdir(download_path) if f.lower().endswith('.zip')]
            for zip_filename in zip_files:
                zip_path = os.path.join(download_path, zip_filename)
                extract_path = os.path.join(download_path, os.path.splitext(zip_filename)[0])
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    os.makedirs(extract_path, exist_ok=True)
                    zip_ref.extractall(extract_path)
            self.log("Unzip Complete!")
        except Exception as e:
             self.log(f"Unzip Error: {e}", error=True)

    def _execute_steps(self, steps):
        for step in steps:
            name, xpath = step[0], step[1]
            try:
                if len(step) == 3:
                    value = step[2]
                    element = self.bot.driver.find_element(By.XPATH, xpath)
                    if "placeholder='Select pages'" in xpath:
                         element.click()
                         element.send_keys(Keys.CONTROL + "a", Keys.DELETE, value, Keys.TAB)
                    elif "role='spinbutton'" in xpath:
                         element.send_keys(Keys.CONTROL + "a", Keys.DELETE, value, Keys.ENTER)
                    elif "aria-label='Design title'" in xpath:
                         element = WebDriverWait(self.bot.driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                         element.click()
                         element.send_keys(Keys.CONTROL + "a", Keys.DELETE, value, Keys.ENTER)
                    else:
                        if not self.bot.input_text(xpath, value): return False
                else:
                    element = WebDriverWait(self.bot.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                    self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    if not self.bot.click_element(xpath, timeout=2):
                         self.bot.driver.execute_script("arguments[0].click();", element)
                time.sleep(0.5)
            except:
                return False
        return True

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    app = App()
    app.mainloop()
