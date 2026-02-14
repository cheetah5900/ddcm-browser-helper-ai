import customtkinter as ctk
import threading
import time
from browser_bot import BrowserBot
import time

# --- Configuration ---
# You can update these XPaths later
XPATH_CONFIG = {
    "export_png": "//button[contains(text(), 'Export PNG')]", # Placeholder
    "login_button": "//button[@id='login']",                   # Placeholder
    # Add more placeholders here
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Browser Controller")
        self.geometry("400x500")
        
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

        # --- Buttons ---
        
        # 3. Action: Export PNG
        self.btn_export = ctk.CTkButton(self.controls_frame, text="Action: Export PNG", command=self.action_export_png, fg_color="green")
        self.btn_export.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # 4. Action: Custom Action 1 (Example)
        self.btn_custom1 = ctk.CTkButton(self.controls_frame, text="Action: Custom 1", command=self.action_custom_1)
        self.btn_custom1.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # 5. Debug: Check Tabs
        self.btn_check = ctk.CTkButton(self.controls_frame, text="Debug: Check Tabs", command=self.debug_check_tabs, fg_color="gray")
        self.btn_check.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # 6. Close Browser
        self.btn_close = ctk.CTkButton(self.controls_frame, text="Close Browser", command=self.bot.close_browser, fg_color="red")
        self.btn_close.grid(row=5, column=0, padx=20, pady=20, sticky="ew")

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Connecting...", text_color="orange")
        self.status_label.grid(row=2, column=0, pady=10)
        
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
            
            # Step 6: Click option (Transparent background?)
            ("Click Option", "//p[contains(text(), 'Transparent background')]"),
            
            # Step 7: Set Pages to 1-4
            # We use the placeholder 'Select pages' which is very specific
            ("Set Pages to 1-4", "//input[@placeholder='Select pages']", "1-4"),
            
            # Step 8: Click Final Download Button
            # It's usually a submit button with text 'Download'
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
                     from selenium.webdriver.common.keys import Keys
                     from selenium.webdriver.common.by import By
                     
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

    def action_custom_1(self):
        """Defines a custom action sequence."""
        self.log("Running Custom Action 1...")
        # Add logic here
        pass

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
