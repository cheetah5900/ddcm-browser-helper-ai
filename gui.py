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
        self.btn_export = ctk.CTkButton(self.controls_frame, text="Export PNG (Size 1, P.1-4)", command=self.action_export_png, fg_color="#00C4CC")
        self.btn_export.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Action: Export JPG
        self.btn_export_jpg = ctk.CTkButton(self.controls_frame, text="Export JPG (Size 0.5, P.6-9)", command=self.action_export_jpg, fg_color="#00C4CC")
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

        # --- Etsy and DDMC Section ---
        self.lbl_etsy = ctk.CTkLabel(self.controls_frame, text="Etsy and DDMC", font=("Arial", 14, "bold"))
        self.lbl_etsy.grid(row=5, column=0, columnspan=2, pady=(15, 5), sticky="w", padx=20)

        # --- Etsy Data Inputs ---
        self.lbl_etsy_data = ctk.CTkLabel(self.controls_frame, text="Etsy Listing Details", font=("Arial", 12, "italic"))
        self.lbl_etsy_data.grid(row=6, column=0, columnspan=2, pady=(5, 0), sticky="w", padx=20)

        # Primary Color & Secondary Color
        self.entry_primary = ctk.CTkEntry(self.controls_frame, placeholder_text="Primary Color")
        self.entry_primary.insert(0, "Red")
        self.entry_primary.grid(row=7, column=0, padx=10, pady=5, sticky="ew")
        
        self.entry_secondary = ctk.CTkEntry(self.controls_frame, placeholder_text="Secondary Color")
        self.entry_secondary.insert(0, "Gray")
        self.entry_secondary.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

        # Price & Shop Section
        self.entry_price = ctk.CTkEntry(self.controls_frame, placeholder_text="Price (e.g. 5.99)")
        self.entry_price.insert(0, "2")
        self.entry_price.grid(row=8, column=0, padx=10, pady=5, sticky="ew")
        
        self.entry_section = ctk.CTkEntry(self.controls_frame, placeholder_text="Shop Section Name")
        self.entry_section.insert(0, "Chinese New Year")
        self.entry_section.grid(row=8, column=1, padx=10, pady=5, sticky="ew")

        # Action: Create Etsy Listing
        self.btn_etsy = ctk.CTkButton(self.controls_frame, text="Create Etsy Listing", command=self.action_etsy_listing, fg_color="#F1641E") # Etsy Orange
        self.btn_etsy.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # --- Status Section ---
        self.status_label = ctk.CTkLabel(self, text="Connecting...", text_color="orange")
        self.status_label.grid(row=10, column=0, pady=10)
        
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
            
            # Step 7: Set Pages to 1-4
            ("Set Pages to 1-4", "//input[@placeholder='Select pages']", "1-4"),
            
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
            
            # Step 6: Set Pages to 6-9
            ("Set Pages to 6-9", "//input[@placeholder='Select pages']", "6-9"),
            
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

        # Define steps for PDF
        steps = [
            # Step 1: Rename Design (New!)
            ("Rename Design to 'pdf_for_downloading'", "//input[@aria-label='Design title']", "pdf_for_downloading"),

            ("Click Share/Export", "//button[.//span[text()='Share']]"),
            ("Click Download", "//button[@aria-label='Download']"),
            ("Click File Type", "//button[@aria-label='File type']"),
            ("Select PDF Standard", "//li[@role='option']//div[contains(text(), 'PDF Standard')]"),
            
            # Step 5: Set Pages to 10
            ("Set Pages to 10", "//input[@placeholder='Select pages']", "10"),
            
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

    def action_etsy_listing(self):
        """Extracts data from DDCM and populates the Etsy listing creator with user inputs."""
        self.log("Starting Etsy Listing process...")
        
        # 0. Get user inputs from GUI and validate
        user_primary = self.entry_primary.get().strip()
        user_secondary = self.entry_secondary.get().strip()
        user_price = self.entry_price.get().strip()
        user_section = self.entry_section.get().strip()

        if not all([user_primary, user_secondary, user_price, user_section]):
            self.log("Error: All 4 fields (Colors, Price, Section) must be filled!", error=True)
            return

        # 1. Extract from DDCM
        if not self.bot.switch_to_tab_containing("ddcm.litarandfriends.uk"):
            self.bot.driver.execute_script("window.open('https://ddcm.litarandfriends.uk', '_blank');")
            time.sleep(2)
            self.bot.switch_to_tab_containing("ddcm.litarandfriends.uk")

        extracted_data = {}
        ddcm_fields = [
            ("name", "/html/body/main/div[3]/div/div[2]/div[2]/div/div/div"),
            ("tag", "/html/body/main/div[3]/div/div[2]/div[10]/div/div/div"),
            ("material", "/html/body/main/div[3]/div/div[2]/div[11]/div/div/div/div"),
            ("description", "/html/body/main/div[3]/div/div[2]/div[12]/div/div/div/div")
        ]

        for field_name, xpath in ddcm_fields:
            try:
                element = WebDriverWait(self.bot.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                # Auto-scroll to element before extracting
                self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.2)
                
                # Filter out any weird characters if needed
                text = element.text.strip()
                extracted_data[field_name] = text
                self.log(f"Extracted {field_name}")
            except Exception:
                self.log(f"Error: Could not find '{field_name}' on DDCM within 10s.", error=True)
                return

        self.log("Extracted all data from DDCM.")

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
            # 3. Price
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
            
            # 10. Shop Section
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
