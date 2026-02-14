import customtkinter as ctk
import threading
import time
import os
import zipfile
from browser_bot import BrowserBot
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- Configuration ---
# You can update these XPaths later
XPATH_CONFIG = {
    "export_png": "//button[contains(text(), 'Export PNG')]", # Placeholder
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Browser Controller")
        self.geometry("400x600") # Increased height for new buttons
        
        # Initialize the bot
        self.bot = BrowserBot()

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title area
        self.grid_rowconfigure(1, weight=1) # Controls area

        # Title
        self.label = ctk.CTkLabel(self, text="Browser Controller", font=("Arial", 20, "bold"))
        self.label.grid(row=0, column=0, padx=20, pady=20)

        # Controls Frame
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.controls_frame.grid_columnconfigure(0, weight=1)
        self.controls_frame.grid_columnconfigure(1, weight=1) # 2 Columns

        # --- Canva Automation Section ---
        self.lbl_canva = ctk.CTkLabel(self.controls_frame, text="Canva Automation", font=("Arial", 14, "bold"))
        self.lbl_canva.grid(row=0, column=0, columnspan=2, pady=(10, 5), sticky="w", padx=20)

        # Action: Export PNG
        self.btn_export = ctk.CTkButton(self.controls_frame, text="Export PNG (Size 1)", command=self.action_export_png, fg_color="#00C4CC")
        self.btn_export.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Action: Export JPG
        self.btn_export_jpg = ctk.CTkButton(self.controls_frame, text="Export JPG (Size 0.5)", command=self.action_export_jpg, fg_color="#00C4CC")
        self.btn_export_jpg.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Action: Export PDF
        self.btn_export_pdf = ctk.CTkButton(self.controls_frame, text="Export PDF (Page 10)", command=self.action_export_pdf, fg_color="#E04F5F") # Reddish
        self.btn_export_pdf.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Action: Export ALL
        self.btn_export_all = ctk.CTkButton(self.controls_frame, text="Export ALL", command=self.action_export_all, fg_color="#005F99") # Dark Blue
        self.btn_export_all.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # --- File Tools Section ---
        self.lbl_files = ctk.CTkLabel(self.controls_frame, text="File Tools", font=("Arial", 14, "bold"))
        self.lbl_files.grid(row=3, column=0, columnspan=2, pady=(15, 5), sticky="w", padx=20)

        # Action: Unzip All
        self.btn_unzip = ctk.CTkButton(self.controls_frame, text="Unzip All Zips", command=self.action_unzip_downloads, fg_color="#FFA500") # Orange
        self.btn_unzip.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        # --- Status Section ---
        self.status_label = ctk.CTkLabel(self, text="Connecting...", text_color="orange")
        self.status_label.grid(row=2, column=0, pady=20)
        
        # Auto-start connection
        self.start_browser_thread()

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

        # Define steps with your specific XPaths
        steps = [
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
            
            # Step 7: Set Pages to 1-4
            ("Set Pages to 1-4", "//input[@placeholder='Select pages']", "1-4"),
            
            # Step 8: Click Final Download Button
            ("Final Download", "//button[@type='submit'][.//span[contains(text(), 'Download')]]")
        ]

        for step in steps:
            name = step[0]
            xpath = step[1]
            
            if len(step) == 3: # It's an input/value task
                value = step[2]
                self.log(f"Step: {name}")
                
                # Special handling for Page Selector: Clear first, then TAB
                if "placeholder='Select pages'" in xpath:
                     # Keys and By are already imported globally
                     try:
                         # Use driver directly to find element
                         element = self.bot.driver.find_element(By.XPATH, xpath)
                         element.click()
                         time.sleep(0.5)
                         # Clear by Select All + Delete (More reliable for React inputs)
                         element.send_keys(Keys.CONTROL + "a")
                         element.send_keys(Keys.DELETE)
                         time.sleep(0.5)
                         # Type new value
                         element.send_keys(value)
                         time.sleep(0.5)
                         # Press TAB
                         element.send_keys(Keys.TAB)
                     except Exception as e:
                         self.log(f"Error in Page Selector step: {e}")
                         return
                else:
                    if not self.bot.input_text(xpath, value, timeout=10):
                        self.log(f"Failed at step: {name}")
                        return
            else: # It's a click task
                self.log(f"Step: {name}")
                if not self.bot.click_element(xpath, timeout=10):
                    self.log(f"Failed at step: {name}")
                    return
            
            time.sleep(0.5) # Small delay between steps to be safe

        self.log("Export PNG sequence completed.")

    def action_export_jpg(self):
        """Defines the sequence for Export JPG on Canva."""
        self.log("Running Export JPG...")
        
        # 0. Ensure we are on Canva
        if not self.bot.switch_to_tab_containing("canva.com"):
            self.log("Error: 'canva.com' is not open in any tab.")
            return

        time.sleep(1) # Brief pause after switch

        # Define steps for JPG
        steps = [
            ("Click Share/Export", "//button[.//span[text()='Share']]"),
            ("Click Download", "//button[@aria-label='Download']"),
            ("Click File Type", "//button[@aria-label='File type']"),
            ("Select JPG", "//li[@role='option']//div[contains(text(), 'JPG')]"),
            
            # Step 5: Set Size to 0.5
            ("Set Size to 0.5", "//input[@role='spinbutton']", "0.5"),
            
            # Step 6: Set Pages to 6-9
            ("Set Pages to 6-9", "//input[@placeholder='Select pages']", "6-9"),
            
            # Step 7: Click Final Download Button
            ("Final Download", "//button[@type='submit'][.//span[contains(text(), 'Download')]]")
        ]

        for step in steps:
            name = step[0]
            xpath = step[1]
            
            if len(step) == 3: # It's an input/value task
                value = step[2]
                self.log(f"Step: {name}")
                
                # Special handling for Page Selector: Clear first, then TAB
                if "placeholder='Select pages'" in xpath:
                     # Keys and By are already imported globally
                     try:
                         # Use driver directly to find element
                         element = self.bot.driver.find_element(By.XPATH, xpath)
                         element.click()
                         time.sleep(0.5)
                         # Clear by Select All + Delete
                         element.send_keys(Keys.CONTROL + "a")
                         element.send_keys(Keys.DELETE)
                         time.sleep(0.5)
                         # Type new value
                         element.send_keys(value)
                         time.sleep(0.5)
                         # Press TAB
                         element.send_keys(Keys.TAB)
                     except Exception as e:
                         self.log(f"Error in Page Selector step: {e}")
                         return
                else:
                    if not self.bot.input_text(xpath, value, timeout=10):
                        self.log(f"Failed at step: {name}")
                        return
            else: # Click task
                self.log(f"Step: {name}")
                if not self.bot.click_element(xpath, timeout=10):
                    self.log(f"Failed at step: {name}")
                    return
            
            time.sleep(0.5)

        self.log("Export JPG sequence completed.")

    def action_export_pdf(self):
        """Defines the sequence for Export PDF (Standard) on Canva."""
        self.log("Running Export PDF...")
        
        # 0. Ensure we are on Canva
        if not self.bot.switch_to_tab_containing("canva.com"):
            self.log("Error: 'canva.com' is not open in any tab.")
            return

        time.sleep(1) # Brief pause after switch

        # Define steps for PDF
        steps = [
            ("Click Share/Export", "//button[.//span[text()='Share']]"),
            ("Click Download", "//button[@aria-label='Download']"),
            ("Click File Type", "//button[@aria-label='File type']"),
            ("Select PDF Standard", "//li[@role='option']//div[contains(text(), 'PDF Standard')]"),
            
            # Step 5: Set Pages to 10
            ("Set Pages to 10", "//input[@placeholder='Select pages']", "10"),
            
            # Step 6: Click Final Download Button
            ("Final Download", "//button[@type='submit'][.//span[contains(text(), 'Download')]]")
        ]

        # Use existing step execution logic (copy-paste style for safety)
        for step in steps:
            name = step[0]
            xpath = step[1]
            
            if len(step) == 3: # It's an input/value task
                value = step[2]
                self.log(f"Step: {name}")
                
                # Special handling for Page Selector
                if "placeholder='Select pages'" in xpath:
                     try:
                         element = self.bot.driver.find_element(By.XPATH, xpath)
                         element.click()
                         time.sleep(0.5)
                         element.send_keys(Keys.CONTROL + "a")
                         element.send_keys(Keys.DELETE)
                         time.sleep(0.5)
                         element.send_keys(value)
                         time.sleep(0.5)
                         element.send_keys(Keys.TAB)
                     except Exception as e:
                         self.log(f"Error in Page Selector step: {e}")
                         return
                # Special handling for Size Input (Spinbutton) - Fix Focus/Delay issue
                elif "role='spinbutton'" in xpath:
                     try:
                         element = self.bot.driver.find_element(By.XPATH, xpath)
                         # Simple clear and set value
                         element.send_keys(Keys.CONTROL + "a")
                         element.send_keys(Keys.DELETE)
                         time.sleep(0.2)
                         
                         element.send_keys(value)
                         time.sleep(0.5)
                         element.send_keys(Keys.ENTER) # Confirm value and exit focus
                         time.sleep(1.0) # Extra wait for UI to settle before next click
                     except Exception as e:
                         self.log(f"Error in Size step: {e}")
                         return
                else:
                    if not self.bot.input_text(xpath, value, timeout=10):
                        self.log(f"Failed at step: {name}")
                        return
            else: # Click task
                self.log(f"Step: {name}")
                if not self.bot.click_element(xpath, timeout=10):
                    self.log(f"Failed at step: {name}")
                    return
            
            time.sleep(0.5)
        
        self.log("Export PDF sequence completed.")

    def action_export_all(self):
        """Runs PNG, JPG, and PDF export sequences."""
        self.log("Starting ALL Exports (PNG + JPG + PDF)...")
        
        # Run PNG Export
        self.action_export_png()
        self.log("Waiting for PNG cleanup...")
        time.sleep(3) 
        
        # Run JPG Export
        self.action_export_jpg()
        self.log("Waiting for JPG cleanup...")
        time.sleep(3)
        
        # Run PDF Export
        self.action_export_pdf()
        
        self.log("ALL Exports Completed Successfully!")

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
