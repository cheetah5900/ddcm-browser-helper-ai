import customtkinter as ctk
import threading
import time
import os
import zipfile
from browser_bot import BrowserBot
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration ---
# You can update these XPaths later
XPATH_CONFIG = {
    "export_png": "//button[contains(text(), 'Export PNG')]", # Placeholder
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Browser Controller")
        self.geometry("1200x600") # Widen window 3x
        
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
        
        # Configure columns for horizontal layout (4 main columns)
        self.controls_frame.grid_columnconfigure(0, weight=1) # Canva
        self.controls_frame.grid_columnconfigure(1, weight=1) # File Tools
        self.controls_frame.grid_columnconfigure(2, weight=1) # Etsy
        self.controls_frame.grid_columnconfigure(3, weight=1) # Gemini

        # === COLUMN 0: Canva Automation ===
        self.frame_canva = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.frame_canva.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_canva.grid_columnconfigure(0, weight=1)

        self.lbl_canva = ctk.CTkLabel(self.frame_canva, text="Canva Automation", font=("Arial", 16, "bold"))
        self.lbl_canva.grid(row=0, column=0, pady=(10, 15), sticky="w")

        # Shorter buttons (width=150 is example, adjust as needed)
        
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

        # Adjust rows for subsequent buttons
        self.btn_export_pdf = ctk.CTkButton(self.frame_canva, text="Export PDF", width=140, command=self.action_export_pdf, fg_color="#E04F5F")
        self.btn_export_pdf.grid(row=6, column=0, pady=(5, 10), sticky="w")

        self.btn_export_all = ctk.CTkButton(self.frame_canva, text="Export ALL", width=140, command=self.action_export_all, fg_color="#005F99")
        self.btn_export_all.grid(row=7, column=0, pady=10, sticky="w")


        # === COLUMN 1: File Tools ===
        self.frame_files = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.frame_files.grid(row=0, column=1, padx=10, pady=10, sticky="nsw")
        self.frame_files.grid_columnconfigure(0, weight=1)

        self.lbl_files = ctk.CTkLabel(self.frame_files, text="File Tools", font=("Arial", 16, "bold"))
        self.lbl_files.grid(row=0, column=0, columnspan=2, pady=(10, 15), sticky="w")

        # Path 1 Config
        self.entry_path1 = ctk.CTkEntry(self.frame_files, placeholder_text="Path 1", width=140)
        self.entry_path1.insert(0, r"C:\Files\Project\local DDCM")
        self.entry_path1.grid(row=1, column=0, pady=5, sticky="w")
        
        self.entry_folder1 = ctk.CTkEntry(self.frame_files, placeholder_text="Folder Name 1", width=140)
        self.entry_folder1.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Path 2 Config
        self.entry_path2 = ctk.CTkEntry(self.frame_files, placeholder_text="Path 2", width=140)
        self.entry_path2.insert(0, r"G:\My Drive\Projects\DDCM\Cliparts DDCM")
        self.entry_path2.grid(row=2, column=0, pady=5, sticky="w")

        self.entry_folder2 = ctk.CTkEntry(self.frame_files, placeholder_text="Folder Name 2", width=140)
        self.entry_folder2.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.btn_create_folders = ctk.CTkButton(self.frame_files, text="Create Folders", width=140, command=self.action_create_folders, fg_color="#27AE60")
        self.btn_create_folders.grid(row=3, column=0, columnspan=2, pady=10, sticky="w")

        self.btn_unzip = ctk.CTkButton(self.frame_files, text="Unzip Downloads", width=140, command=self.action_unzip_downloads, fg_color="#FFA500")
        self.btn_unzip.grid(row=4, column=0, columnspan=2, pady=10, sticky="w")
        

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


        # === COLUMN 3: Gemini Automation (Moved Here) ===
        self.frame_gemini = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.frame_gemini.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")
        self.frame_gemini.grid_columnconfigure(0, weight=1)

        self.lbl_gemini = ctk.CTkLabel(self.frame_gemini, text="Gemini Automation", font=("Arial", 16, "bold"))
        self.lbl_gemini.grid(row=0, column=0, pady=(10, 15), sticky="w")

        self.entry_gemini_count = ctk.CTkEntry(self.frame_gemini, placeholder_text="Count", width=80)
        self.entry_gemini_count.insert(0, "5")
        self.entry_gemini_count.grid(row=1, column=0, pady=10, sticky="w")

        self.btn_gemini = ctk.CTkButton(self.frame_gemini, text="Gen Characters", width=120, command=self.action_gemini_gen, fg_color="#8E44AD")
        self.btn_gemini.grid(row=1, column=0, pady=5, sticky="w")

        self.btn_gemini_elements = ctk.CTkButton(self.frame_gemini, text="Gen Elements", width=120, command=self.action_gemini_elements, fg_color="#8E44AD")
        self.btn_gemini_elements.grid(row=2, column=0, pady=5, sticky="w")

        self.btn_download_imgs = ctk.CTkButton(self.frame_gemini, text="Download images", width=120, command=self.action_download_images, fg_color="#2E86C1") # Blue
        self.btn_download_imgs.grid(row=3, column=0, pady=5, sticky="w")


        # --- Status Section ---
        self.status_label = ctk.CTkLabel(self, text="Connecting...", text_color="orange")
        self.status_label.grid(row=2, column=0, pady=10)
        
        # Auto-start connection
        self.start_browser_thread()

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

            # 2. Scroll to TOP (to handle lazy load / find all)
            self.log("Scrolling to TOP...")
            # Try scrolling the main window and common scrollers
            self.bot.driver.execute_script("window.scrollTo(0, 0);")
            
            # Sometimes the scroll is on a specific element. Try widely used classes.
            scrollers = self.bot.driver.find_elements(By.CSS_SELECTOR, ".infinite-scroller, .conversation-container, main")
            for s in scrollers:
                self.bot.driver.execute_script("arguments[0].scrollTop = 0;", s)
            
            time.sleep(2) # Wait for load

            # 3. Find Download Buttons
            # Selector: download-generated-image-button > button
            # Need to find ALL of them.
            
            # Since Gemini lazy loads, we might need to scroll DOWN slowly to find them all?
            # User said "scroll to top" - assuming old items are at top and we need to start there.
            # But if we click, we need to ensure they are in view.

            # Let's find all currently visible/loaded buttons first.
            buttons = self.bot.driver.find_elements(By.CSS_SELECTOR, "download-generated-image-button > button")
            
            if not buttons:
                self.log("No download buttons found initially. Trying to scroll down a bit...", error=False)
                # Maybe scroll specific amount?
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
                    # Scroll into view
                    self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(0.5)

                    # Click
                    try:
                        btn.click()
                    except:
                        self.bot.driver.execute_script("arguments[0].click();", btn)
                    
                    # Smart Wait: Wait until the NEXT button is clickable (or current one if checking state)
                    # The user said "Wait for status to return to normal".
                    # Usually when downloading, the button might be disabled or loading.
                    # We can check if the button itself is re-enabled/clickable.
                    
                    try:
                        # Wait up to 15 seconds for THIS button to be interactable again
                        # Or perhaps just a small delay + check
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
            results = []

            for name, selector in containers:
                self.log(f"Scanning {name}...")
                try:
                    # Find container
                    container = WebDriverWait(self.bot.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    
                    # Scroll container into view
                    self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
                    time.sleep(0.5)

                    # Find buttons
                    buttons = container.find_elements(By.TAG_NAME, "button")
                    if not buttons:
                         buttons = container.find_elements(By.XPATH, ".//button")
                    
                    count = len(buttons)
                    results.append(f"{name}: {count}")
                    
                    if count > 0:
                        for i, btn in enumerate(buttons):
                            try:
                                # Scroll to button (fast)
                                self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                
                                # Click
                                try: btn.click()
                                except: self.bot.driver.execute_script("arguments[0].click();", btn)
                                time.sleep(0.1)

                                # Get text
                                try:
                                    text = self.clipboard_get()
                                    if text: all_prompts.append(text)
                                except: pass
                            except Exception as e:
                                print(f"Error btn {i}: {e}")
                except Exception as e:
                    self.log(f"Error {name}: {e}", error=True)
                    results.append(f"{name}: Error")

            self.log(f"Collected {len(all_prompts)} prompts. Switching to Gemini...")
            
            if not all_prompts:
                self.log("No prompts collected. Stopping.")
                return

            # 3. Switch to Gemini
            gemini_url = "gemini.google.com/app"
            found_gemini = False
            for handle in self.bot.driver.window_handles:
                self.bot.driver.switch_to.window(handle)
                if gemini_url in self.bot.driver.current_url:
                    found_gemini = True
                    break
            
            if not found_gemini:
                self.log("Error: Gemini tab not found! Please open it.", error=True)
                return

            time.sleep(1)

            # 4. Input Prompts loop
            input_box_xpath = "//div[contains(@class, 'ql-editor') and @contenteditable='true']"
            
            for i, prompt in enumerate(all_prompts):
                self.log(f"Processing Gemini {i+1}/{len(all_prompts)}...")
                
                try:
                    # Find Input Box
                    input_box = WebDriverWait(self.bot.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, input_box_xpath))
                    )
                    
                    # Click to focus
                    input_box.click()
                    
                    # Paste text
                    input_box.send_keys(prompt)
                    time.sleep(1)
                    input_box.send_keys(Keys.ENTER)
                    
                    self.log(f"  -> Sent prompt {i+1}. Waiting for generation...")
                    time.sleep(2)

                    # Check for Stop Icon
                    stop_icon_xpath = "//mat-icon[contains(@data-mat-icon-name, 'stop') or @fonticon='stop']"
                    
                    # Wait loop: check if stop icon is present
                    while True:
                        try:
                            # Try to find the stop button with a short timeout
                            self.bot.driver.find_element(By.XPATH, stop_icon_xpath)
                            # If found, it means it's still generating
                            time.sleep(1)
                        except:
                            # If NOT found (NoSuchElementException), it means generation finished
                            self.log("  -> Generation finished.")
                            break
                    
                    # Proceed to next variable immediately

                except Exception as e:
                    self.log(f"Error in Gemini loop: {e}", error=True)
                    return

            self.log("Gemini Automation Complete!", error=False)

        except Exception as e:
            self.log(f"Critical Error: {e}", error=True)
            import traceback
            traceback.print_exc()

    def log(self, message, error=False):
        color = "red" if error else "SystemButtonFace" # Use default or specific color
        if "SystemButtonFace" == color:
             color = "gray"
        
        self.status_label.configure(text=message, text_color=color)
        print(message)

    def start_browser_thread(self):
        """Runs browser start in a separate thread to keep GUI responsive."""
        threading.Thread(target=self._start_browser_task).start()

    def _start_browser_task(self):
        # Changed to True to connect to existing browser
        success = self.bot.start_browser(attach=True)
        if success:
            self.log("Connected to Browser.")
            self.status_label.configure(text_color="green")
        else:
            self.log("Failed: Please Close ALL Chrome Windows & Restart App", error=True)

    # Removed open_target_url method as it's no longer used via button

    def action_export_png(self):
        """Defines the sequence for Export PNG on Canva."""
        self.log("Running Export PNG...")
        
        # 0. Ensure we are on Canva
        if not self.bot.switch_to_tab_containing("canva.com"):
            self.log("Error: 'canva.com' is not open in any tab.")
            return

        time.sleep(1) # Brief pause after switch

        # Get user page range
        pages = self.entry_png_pages.get().strip() or "1-4"

        # Define steps with your specific XPaths
        steps = [
            # Step 1: Rename Design (New!)
            ("Rename Design to 'png'", "//input[@aria-label='Design title']", "png"),

            ("Click Share/Export", "//button[.//span[text()='Share']]"),
            ("Click Download", "//button[@aria-label='Download']"),
            ("Click File Type", "//button[@aria-label='File type']"),
            ("Select PNG", "//li[@role='option']//div[contains(text(), 'PNG')]"),
            # Step 5: Set Size (Input Box next to Slider)
            # Use the text input which is more reliable than the slider
            ("Set Size to 1", "//input[@role='spinbutton']", "1"), 
            
            # Step 6: Ensure Transparent background is CHECKED
            # Force click as requested (assuming it starts unchecked)
            ("Click Transparent", "//label[.//p[contains(text(), 'Transparent background')]]"),
            
            # Step 7: Set Pages
            (f"Set Pages to {pages}", "//input[@placeholder='Select pages']", pages),
            
            # Step 8: Click Final Download Button
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
        
        # 0. Ensure we are on Canva
        if not self.bot.switch_to_tab_containing("canva.com"):
            self.log("Error: 'canva.com' is not open in any tab.")
            return False

        time.sleep(1) # Brief pause after switch

        # Get user page range
        pages = self.entry_jpg_pages.get().strip() or "6-9"

        # Define steps for JPG
        steps = [
            # Step 1: Rename Design (New!)
            ("Rename Design to 'jpg'", "//input[@aria-label='Design title']", "jpg"),

            ("Click Share/Export", "//button[.//span[text()='Share']]"),
            ("Click Download", "//button[@aria-label='Download']"),
            ("Click File Type", "//button[@aria-label='File type']"),
            ("Select JPG", "//li[@role='option']//div[contains(text(), 'JPG')]"),
            
            # Step 5: Set Size to 0.5
            ("Set Size to 0.5", "//input[@role='spinbutton']", "0.5"),
            
            # Step 6: Set Pages
            (f"Set Pages to {pages}", "//input[@placeholder='Select pages']", pages),
            
            # Step 7: Click Final Download Button
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
        
        # 0. Ensure we are on Canva
        if not self.bot.switch_to_tab_containing("canva.com"):
            self.log("Error: 'canva.com' is not open in any tab.")
            return False

        time.sleep(1) # Brief pause after switch

        # Get user page range
        pages = self.entry_pdf_pages.get().strip() or "10"

        # Define steps for PDF
        steps = [
            # Step 1: Rename Design (New!)
            ("Rename Design to 'pdf_for_downloading'", "//input[@aria-label='Design title']", "pdf_for_downloading"),

            ("Click Share/Export", "//button[.//span[text()='Share']]"),
            ("Click Download", "//button[@aria-label='Download']"),
            ("Click File Type", "//button[@aria-label='File type']"),
            ("Select PDF Standard", "//li[@role='option']//div[contains(text(), 'PDF Standard')]"),
            
            # Step 5: Set Pages
            (f"Set Pages to {pages}", "//input[@placeholder='Select pages']", pages),
            
            # Step 6: Click Final Download Button
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
        
        # Run PNG Export
        if not self.action_export_png():
             self.log("ABORTING ALL EXPORTS due to PNG failure.", error=True)
             return

        self.log("Waiting 8s for PNG cleanup...")
        time.sleep(8) 
        
        # Run JPG Export
        if not self.action_export_jpg():
             self.log("ABORTING ALL EXPORTS due to JPG failure.", error=True)
             return

        self.log("Waiting 8s for JPG cleanup...")
        time.sleep(8)
        
        # Run PDF Export
        if not self.action_export_pdf():
             self.log("ABORTING ALL EXPORTS due to PDF failure.", error=True)
             return
        
        self.log("ALL Exports Completed Successfully!")

    def action_create_folders(self):
        """Creates folder structures based on user input."""
        configs = [
            {
                "path": self.entry_path1.get().strip(),
                "folder": self.entry_folder1.get().strip(),
                "subfolders": ["4000x4000", "Download file", "Original", "Preview", "Sticker Set"]
            },
            {
                "path": self.entry_path2.get().strip(),
                "folder": self.entry_folder2.get().strip(),
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
                    self.log(f"Path {i+1}: '{folder_name}' already exists. Skipping.")
                else:
                    os.makedirs(full_path)
                    self.log(f"Path {i+1}: Created '{folder_name}'.")
                    
                    # Create subfolders
                    for sub in subfolders:
                        os.makedirs(os.path.join(full_path, sub))
                    self.log(f"Path {i+1}: Created {len(subfolders)} subfolders.")
            except Exception as e:
                self.log(f"Error creating folders for Path {i+1}: {e}", error=True)

    def action_etsy_listing(self):
        """Extracts data from DDCM and populates the Etsy listing creator with user inputs."""
        self.log("Starting Etsy Listing process...")
        
        # 0. Get user inputs from GUI and validate
        user_primary = self.entry_primary.get().strip()
        user_secondary = self.entry_secondary.get().strip()
        # Price and Section are auto-extracted now, so setting to None for initial logic
        user_price = None 
        user_section = None

        if not all([user_primary, user_secondary]):
            self.log("Error: Colors must be filled!", error=True)
            return

        # 1. Extract from DDCM
        if not self.bot.switch_to_tab_containing("ddcm.litarandfriends.uk"):
            self.bot.driver.execute_script("window.open('https://ddcm.litarandfriends.uk', '_blank');")
            time.sleep(2)
            self.bot.switch_to_tab_containing("ddcm.litarandfriends.uk")

        ddcm_fields = [
            ("name", "/html/body/main/div[4]/div/div[2]/div[2]/div/div/div"),
            ("tag", "/html/body/main/div[4]/div/div[2]/div[10]/div/div/div"), 
            ("material", "/html/body/main/div[4]/div/div[2]/div[11]/div/div/div/div"), 
            ("description", "/html/body/main/div[4]/div/div[2]/div[12]/div/div/div/div"),
            ("theme", "/html/body/main/div[4]/div/div[2]/div[5]/div/div/div"),
            ("price", "/html/body/main/div[4]/div/div[2]/div[8]/div/div/div")
        ]

        extracted_data = {}
        # Simple scroll to top to ensure we find elements if lazy loaded? usually not needed for hardcoded xpaths
        
        for field_name, xpath in ddcm_fields:
            try:
                # Use a smaller timeout for optional fields
                timeout = 5
                element = WebDriverWait(self.bot.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.2)
                
                text = element.text.strip()
                extracted_data[field_name] = text
                self.log(f"Extracted {field_name}: {text[:30]}...")
            except Exception:
                self.log(f"Error: Could not extract '{field_name}' from DDCM. Stopping.", error=True)
                return

        self.log("Extracted all data from DDCM.")
        
        # Prepare variables from extraction
        # Price from DDCM (fallback to "5.99" if Failed)
        user_price = extracted_data.get('price', '5.99')
        if not user_price: user_price = "5.99"
        
        # Shop Section from DDCM Theme (fallback to "General" if Failed)
        user_section = extracted_data.get('theme', 'General')
        if not user_section: user_section = "General"

        if not all([user_primary, user_secondary, user_price, user_section]):
            self.log("Error: All 4 fields (Colors, Price, Section) must be filled!", error=True)
            return

        # 2. Go to Etsy (Force New Tab)
        etsy_create_url = "https://www.etsy.com/your/shops/me/listing-editor/create"
        self.log("Opening new Etsy Create Listing tab...")
        
        # Open NEW tab explicitly EVERY TIME
        self.bot.driver.execute_script(f"window.open('{etsy_create_url}', '_blank');")
        time.sleep(5) 
        # Switch to the NEWly opened tab (last handle)
        self.bot.driver.switch_to.window(self.bot.driver.window_handles[-1])
        self.log("Opened and switched to new Etsy tab.")
        WebDriverWait(self.bot.driver, 10).until(lambda d: "etsy.com" in d.current_url)
        
        time.sleep(2)

        # 3. Etsy Setup Steps (Radio buttons, Category, etc.)
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
                element = WebDriverWait(self.bot.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                # Auto-scroll to element
                self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.3)

                if value: # Dropdown select
                    from selenium.webdriver.support.ui import Select
                    Select(element).select_by_value(value[0])
                else: # Click
                    try: element.click()
                    except: self.bot.driver.execute_script("arguments[0].click();", element)
                time.sleep(0.5)
            except Exception:
                self.log(f"Error: Etsy Setup '{name}' failed within 10s.", error=True)
                return

        self.log("Etsy Setup successful. Waiting 1s to settle...")
        time.sleep(1)

        # 4. Etsy Content Filling (Pasting Variables)
        content_steps = [
            # 1. Title
            ("Paste Title", "//textarea[@id='listing-title-input']", extracted_data.get('name', '')),
            # 2. Description
            ("Paste Description", "//textarea[@id='listing-description-textarea' or @name='description']", extracted_data.get('description', '')),
            # 3. Price (Using Extracted Data)
            ("Paste Price", "//input[@id='listing-price-input']", user_price),
            # 4. Quantity
            ("Paste Quantity", "//input[@id='listing-quantity-input']", "999"),
            
            # 5. Scrapbooking (Craft type)
            ("Click Topic Search", "//input[@placeholder='Type to search…' and contains(@aria-describedby, 'attribute-0')]"),
            ("Check Scrapbooking Box", "//label[contains(text(), 'Scrapbooking')]"),
            ("Press ESC", "SPECIAL_ESC"), # Close scrapbooking dropdown
            
            # 6. Primary color (Verified Absolute XPath)
            ("Paste Primary Color", "/html/body/div[3]/div/div[1]/main/div/div/form/div/div[3]/div/div[4]/div/div/div[3]/div[3]/div/div/div/div/div[1]/input", user_primary),
            ("Select Primary Color", "//button[@role='menuitemradio']//p[contains(text(), '" + user_primary + "')]"),
            
            # 7. Secondary color
            ("Paste Secondary Color", "/html/body/div[3]/div/div[1]/main/div/div/form/div/div[3]/div/div[4]/div/div/div[3]/div[4]/div/div/div/div/div[1]/input", user_secondary),
            ("Select Secondary Color", "//button[@role='menuitemradio']//p[contains(text(), '" + user_secondary + "')]"),
            
            # 8. Tag
            ("Paste Tag", "//input[@id='listing-tags-input']", extracted_data.get('tag', '')),
            ("Click Add Tag", "//button[@id='listing-tags-button']"),
            
            # 9. Material
            ("Paste Material", "//input[@id='listing-materials-input']", extracted_data.get('material', '')),
            ("Click Add Material", "//button[@id='listing-materials-button']"),
            
            # 10. Shop Section (Using Extracted Data)
            ("Select Shop Section", "//select[@id='shop-section-select']", user_section)
        ]

        for step in content_steps:
            name, xpath = step[0], step[1]
            try:
                # Handle special key actions
                if xpath == "SPECIAL_ESC":
                    self.log(f"Etsy Action: Click outside to close Dropdown")
                    # Click body to close dropdown naturally
                    self.bot.driver.find_element(By.TAG_NAME, "body").click()
                    time.sleep(0.5)
                    continue

                # Use element_to_be_clickable for input fields
                element = WebDriverWait(self.bot.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                
                # Strict scroll to ensure visibility
                self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
                time.sleep(0.5)

                self.log(f"Etsy Filling: {name}")
                
                # If there's a third value, it's text to input or dropdown value
                if len(step) == 3:
                    text_value = step[2]
                    if element.tag_name == "select":
                        from selenium.webdriver.support.ui import Select
                        s = Select(element)
                        try: s.select_by_visible_text(text_value)
                        except: s.select_by_value(text_value)
                    else:
                        try:
                            element.click()
                        except:
                            self.bot.driver.execute_script("arguments[0].click();", element)
                        
                        # Special handling for Craft type search / Colors which need 'typing' for the dropdown to appear
                        # OR if it's a field that doesn't like JS injection for focus
                        if "placeholder='Type to search…'" in xpath:
                            element.send_keys(Keys.CONTROL + "a")
                            element.send_keys(Keys.DELETE)
                            element.send_keys(text_value)
                        else:
                            # USE JAVASCRIPT TO SET VALUE (To support Emojis and avoid BMP Error)
                            self.bot.driver.execute_script("""
                                var el = arguments[0];
                                var val = arguments[1];
                                el.value = val;
                                // Trigger React/Modern Framework events
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                            """, element, text_value)
                        
                        time.sleep(0.5)
                else: # Just a click (Native click for better focus)
                    try: 
                        # For checkboxes/labels, native click is better for focus
                        element.click()
                    except: 
                        self.bot.driver.execute_script("arguments[0].click();", element)
                
                time.sleep(0.5)
            except Exception as e:
                # Log the actual error for debugging
                error_msg = str(e).split('\n')[0] # Get first line of error
                self.log(f"Error: Etsy Content '{name}' fail. ({error_msg})", error=True)
                return

        self.log("Etsy Listing populated successfully!")

    def action_unzip_downloads(self):
        """Unzips all .zip files in the Downloads folder."""
        self.log("Starting Unzip process in Downloads folder...")
        
        try:
            download_path = os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(download_path):
                 self.log(f"Error: Downloads folder not found at {download_path}", error=True)
                 return

            zip_files = [f for f in os.listdir(download_path) if f.lower().endswith('.zip')]
            
            if not zip_files:
                self.log("No .zip files found in Downloads.")
                return

            self.log(f"Found {len(zip_files)} zip files. Extracting...")
            
            count = 0
            for zip_filename in zip_files:
                zip_path = os.path.join(download_path, zip_filename)
                # Create a folder with the same name as the zip file
                extract_folder_name = os.path.splitext(zip_filename)[0]
                extract_path = os.path.join(download_path, extract_folder_name)
                
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        # Create directory if it doesn't exist
                        if not os.path.exists(extract_path):
                            os.makedirs(extract_path)
                        zip_ref.extractall(extract_path)
                    
                    self.log(f"Extracted: {zip_filename}")
                    count += 1
                except Exception as e:
                    self.log(f"Failed to extract {zip_filename}: {e}", error=True)
            
            self.log(f"Unzip Complete! Extracted {count} files.")

        except Exception as e:
             self.log(f"Critical Error: {e}", error=True)



    def _execute_steps(self, steps):
        """
        Helper to execute a list of steps with special handling.
        Returns: True if all steps succeeded, False if any failed.
        """
        for step in steps:
            name = step[0]
            xpath = step[1]
            
            if len(step) == 3: # It's an input/value task
                value = step[2]
                self.log(f"Step: {name}")
                
                try:
                    # Special handling for Page Selector
                    if "placeholder='Select pages'" in xpath:
                         element = self.bot.driver.find_element(By.XPATH, xpath)
                         element.click()
                         time.sleep(0.5)
                         element.send_keys(Keys.CONTROL + "a")
                         element.send_keys(Keys.DELETE)
                         time.sleep(0.5)
                         element.send_keys(value)
                         time.sleep(0.5)
                         element.send_keys(Keys.TAB)
                    
                    # Special handling for Size Input (Spinbutton)
                    elif "role='spinbutton'" in xpath:
                         element = self.bot.driver.find_element(By.XPATH, xpath)
                         element.send_keys(Keys.CONTROL + "a")
                         element.send_keys(Keys.DELETE)
                         time.sleep(0.2)
                         element.send_keys(value)
                         time.sleep(0.5)
                         element.send_keys(Keys.ENTER) # Confirm value
                         time.sleep(1.0) # Extra wait for UI
                         
                    # Special handling for Rename (Design title) - WITH 20s TIMEOUT
                    elif "aria-label='Design title'" in xpath:
                         try:
                             # Wait up to 20 seconds for the rename box to be present and interactable
                             element = WebDriverWait(self.bot.driver, 20).until(
                                 EC.element_to_be_clickable((By.XPATH, xpath))
                             )
                             # Click TWICE to ensure focus (bypass popups)
                             element.click()
                             time.sleep(0.5)
                             element.click()
                             
                             # Clear existing name
                             element.send_keys(Keys.CONTROL + "a")
                             element.send_keys(Keys.DELETE)
                             time.sleep(0.2)
                             # Set new name
                             element.send_keys(value)
                             time.sleep(0.5)
                             # Press Enter
                             element.send_keys(Keys.ENTER)
                             time.sleep(1.0) # Wait for save
                         except Exception as e:
                             self.log(f"Error: Could not find Rename Button within 20s. Stopping. ({e})", error=True)
                             return False

                    else: # Normal input
                        if not self.bot.input_text(xpath, value, timeout=10):
                            self.log(f"Failed at step: {name}")
                            return False
                            
                except Exception as e:
                    self.log(f"Error in step '{name}': {e}", error=True)
                    return False

            else: # Click task
                self.log(f"Step: {name}")
                # Wait + Scroll for Canva clicks too
                try:
                    element = WebDriverWait(self.bot.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.3)
                    
                    if not self.bot.click_element(xpath, timeout=2):
                         # Fallback to JS click if normal click fails
                         self.bot.driver.execute_script("arguments[0].click();", element)
                except:
                    self.log(f"Failed at step: {name}")
                    return False
            
            time.sleep(0.5)
            
        return True

    def debug_check_tabs(self):
        """Prints all open tabs to debug."""
        self.log("Checking all open tabs...")
        if not self.bot.driver:
            self.log("Browser not connected.")
            return

        found_canva = False
        original_handle = self.bot.driver.current_window_handle
        
        for handle in self.bot.driver.window_handles:
            self.bot.driver.switch_to.window(handle)
            url = self.bot.driver.current_url
            title = self.bot.driver.title
            print(f"Tab: {title} | URL: {url}")
            if "canva.com" in url:
                found_canva = True
        
        self.bot.driver.switch_to.window(original_handle)
        
        if found_canva:
            self.log("Found Canva! System should work.")
        else:
            self.log("Canva NOT found in any tab.", error=True)

if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    app = App()
    app.mainloop()
