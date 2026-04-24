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

        self.title("DDCM WorkFlow - Sequential Guide")
        self.geometry("900x950")
        
        # Initialize the bot
        self.bot = BrowserBot()

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title
        self.grid_rowconfigure(1, weight=1) # Main Content

        # Title
        self.label = ctk.CTkLabel(self, text="DDCM WorkFlow - Sequential Guide", font=("Arial", 24, "bold"), text_color="white")
        self.label.grid(row=0, column=0, padx=20, pady=20)

        # Scrollable Frame for 13 Steps (Single Column)
        self.main_container = ctk.CTkScrollableFrame(self)
        self.main_container.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)

        # ---------------------------------------------------------
        # STEP 1: Basic Info
        # ---------------------------------------------------------
        self.frame_step1 = self.create_step_frame("1. กรอกข้อมูลพื้นฐาน (Basic Info)")
        self.add_label(self.frame_step1, "Folder Name (ชื่อโฟลเดอร์งาน)")
        self.entry_folder_name = self.add_entry(self.frame_step1, "Folder Name")
        self.add_label(self.frame_step1, "Element Name (ชื่อโฟลเดอร์ของตกแต่ง)")
        self.entry_element_name = self.add_entry(self.frame_step1, "Element Name", "Songkran")
        self.add_label(self.frame_step1, "Element Path (ที่เก็บของตกแต่ง)")
        self.entry_element_path = self.add_entry(self.frame_step1, "Element Path")
        self.add_label(self.frame_step1, "Local Path (ที่เก็บงานในเครื่อง)")
        self.entry_local_path = self.add_entry(self.frame_step1, "Local Path")
        self.add_label(self.frame_step1, "Remote Path (ที่เก็บงานบน Drive)")
        self.entry_remote_path = self.add_entry(self.frame_step1, "Remote Path")

        # ---------------------------------------------------------
        # STEP 2: Config & Folders
        # ---------------------------------------------------------
        self.frame_step2 = self.create_step_frame("2. ตั้งค่าและเตรียมโฟลเดอร์")
        self.add_desc(self.frame_step2, "บันทึกค่า Element, Local และ Remote Path ด้านบนให้เป็นค่าเริ่มต้นสำหรับการเปิดโปรแกรมครั้งถัดไป")
        self.btn_set_default = self.add_button(self.frame_step2, "Set Paths as Default", self.action_save_defaults, "#5D6D7E")
        self.add_desc(self.frame_step2, "สร้างโฟลเดอร์งานที่ Local และ Remote พร้อมโฟลเดอร์ย่อยที่จำเป็น (เช่น 4000x4000, Sticker Set)")
        self.btn_create_folders = self.add_button(self.frame_step2, "Create Folders", self.action_create_folders, "#27AE60")

        # ---------------------------------------------------------
        # STEP 3: Gemini Automation
        # ---------------------------------------------------------
        self.frame_step3 = self.create_step_frame("3. Gemini Automation (ดึงข้อมูลและสร้างรูปภาพ)")
        self.add_desc(self.frame_step3, "ดึงข้อมูลจาก DDCM ไปสร้างภาพใน Gemini (*ต้องเปิดเมนูสร้างรูปภาพใน Gemini และ Modal ใน DDCM รอไว้*)")
        inner_gemini = ctk.CTkFrame(self.frame_step3, fg_color="transparent"); inner_gemini.pack(fill="x")
        self.entry_single_count = ctk.CTkEntry(inner_gemini, width=60); self.entry_single_count.insert(0, "12")
        self.entry_single_count.grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(inner_gemini, text="Gen Single", width=140, command=self.action_gemini_single, fg_color="#8E44AD").grid(row=0, column=1, padx=5, pady=5)
        self.entry_companion_count = ctk.CTkEntry(inner_gemini, width=60); self.entry_companion_count.insert(0, "12")
        self.entry_companion_count.grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(inner_gemini, text="Gen Companion", width=140, command=self.action_gemini_companion, fg_color="#8E44AD").grid(row=1, column=1, padx=5, pady=5)
        self.entry_elements_count = ctk.CTkEntry(inner_gemini, width=60); self.entry_elements_count.insert(0, "5")
        self.entry_elements_count.grid(row=2, column=0, padx=5, pady=5)
        ctk.CTkButton(inner_gemini, text="Gen Elements", width=140, command=self.action_gemini_elements, fg_color="#8E44AD").grid(row=2, column=1, padx=5, pady=5)

        # ---------------------------------------------------------
        # STEP 4: Download Images
        # ---------------------------------------------------------
        self.frame_step4 = self.create_step_frame("4. จัดเก็บรูปภาพจาก Gemini")
        self.add_desc(self.frame_step4, "โหลดรูปสติ๊กเกอร์ทั้งหมดในหน้า Gemini และย้ายไปไว้ที่โฟลเดอร์ images ใน Downloads")
        self.btn_download_imgs = self.add_button(self.frame_step4, "Download images", self.action_download_images, "#2E86C1")

        # ---------------------------------------------------------
        # STEP 5: Remove Background
        # ---------------------------------------------------------
        self.frame_step5 = self.create_step_frame("5. ตัดพื้นหลัง (Remove Background)")
        self.add_desc(self.frame_step5, "ให้นำรูปใน Downloads/images เข้าโปรแกรม Photoshop เพื่อตัดพื้นหลังให้เป็นพื้นหลังใส (Transparent) ให้เรียบร้อย")

        # ---------------------------------------------------------
        # STEP 6: Upscale Instruction
        # ---------------------------------------------------------
        self.frame_step6 = self.create_step_frame("6. การขยายภาพ (Upscale)")
        self.add_desc(self.frame_step6, "ให้นำรูปที่ตัดพื้นหลังแล้วไปขยายขนาดด้วยโปรแกรม Upscayl โดยตั้งค่าให้บันทึกผลลัพธ์ไว้ในโฟลเดอร์ย่อยชื่อ 'upscale' ภายในโฟลเดอร์ images เดิม")

        # ---------------------------------------------------------
        # STEP 7: Upscale to Local
        # ---------------------------------------------------------
        self.frame_step7 = self.create_step_frame("7. ย้ายไฟล์ Upscale เข้าเครื่อง")
        self.add_desc(self.frame_step7, "ย้ายไฟล์ภาพต้นฉบับไปที่ Original และย้ายไฟล์ที่ขยายแล้วจากโฟลเดอร์ upscale ไปที่ 4000x4000 พร้อมเปลี่ยนชื่อไฟล์และลบไฟล์ชั่วคราวทิ้ง")
        self.btn_copy_upscale = self.add_button(self.frame_step7, "Upscale to Local", self.action_copy_upscale, "#8E44AD")

        # ---------------------------------------------------------
        # STEP 8: Canva Instruction
        # ---------------------------------------------------------
        self.frame_step8 = self.create_step_frame("8. ออกแบบปกใน Canva")
        self.add_desc(self.frame_step8, "ให้เปิดโปรแกรม Canva และนำรูปภาพที่เตรียมไว้มาจัดวางทำเป็นรูปหน้าปกสินค้าและ Preview ให้เรียบร้อย")

        # ---------------------------------------------------------
        # STEP 9: Canva Automation
        # ---------------------------------------------------------
        self.frame_step9 = self.create_step_frame("9. Canva Automation (ส่งออกไฟล์อัตโนมัติ)")
        self.add_desc(self.frame_step9, "กำหนดช่วงหน้าและสั่ง Export ไฟล์ PNG, JPG, PDF ตามลำดับ")
        f_canva = ctk.CTkFrame(self.frame_step9, fg_color="transparent"); f_canva.pack(fill="x")
        self.entry_png_pages = self.add_entry(f_canva, "PNG Pages", "1-4", width=100)
        self.entry_jpg_pages = self.add_entry(f_canva, "JPG Pages", "6-9", width=100)
        self.entry_pdf_pages = self.add_entry(f_canva, "PDF Pages", "10", width=100)
        self.btn_export_png = self.add_button(self.frame_step9, "Export PNG", self.action_export_png, "#00C4CC")
        self.btn_export_jpg = self.add_button(self.frame_step9, "Export JPG", self.action_export_jpg, "#00C4CC")
        self.btn_export_pdf = self.add_button(self.frame_step9, "Export PDF", self.action_export_pdf, "#E04F5F")
        self.btn_export_all = self.add_button(self.frame_step9, "Export ALL (ลำดับต่อเนื่อง)", self.action_export_all, "#005F99")

        # ---------------------------------------------------------
        # STEP 10: Unzip
        # ---------------------------------------------------------
        self.frame_step10 = self.create_step_frame("10. แตกไฟล์ Zip งาน")
        self.add_desc(self.frame_step10, "แตกไฟล์ Zip ทั้งหมดที่เพิ่งดาวน์โหลดมาจาก Canva เพื่อเตรียมรวบรวมเข้าโฟลเดอร์งาน")
        self.btn_unzip = self.add_button(self.frame_step10, "Unzip Downloads", self.action_unzip_downloads, "#FFA500")

        # ---------------------------------------------------------
        # STEP 11: Download to Local
        # ---------------------------------------------------------
        self.frame_step11 = self.create_step_frame("11. รวบรวมไฟล์เข้าโฟลเดอร์งาน")
        self.add_desc(self.frame_step11, "ย้ายไฟล์ภาพจาก Downloads เข้าสู่โฟลเดอร์ย่อย Sticker Set และ Preview ในเครื่องคอมพิวเตอร์ของคุณ")
        self.btn_download_local = self.add_button(self.frame_step11, "Download to Local", self.action_download_to_local, "#F39C12")

        # ---------------------------------------------------------
        # STEP 12: Local to Remote
        # ---------------------------------------------------------
        self.frame_step12 = self.create_step_frame("12. สำรองไฟล์ขึ้น Cloud (Drive)")
        self.add_desc(self.frame_step12, "คัดลอกโฟลเดอร์งานทั้งหมด และดึงไฟล์ Elements จากคลัง มาเก็บไว้ที่ Remote Path (Google Drive)")
        self.btn_local_remote = self.add_button(self.frame_step12, "Local to Remote", self.action_local_remote, "#3498DB")

        # ---------------------------------------------------------
        # STEP 13: Upload to Etsy
        # ---------------------------------------------------------
        self.frame_step13 = self.create_step_frame("13. ลงสินค้าใน Etsy")
        self.etsy_colors = ["Beige", "Black", "Blue", "Bronze", "Brown", "Clear", "Copper", "Gold", "Gray", "Green", "Orange", "Pink", "Purple", "Rainbow", "Red", "Rose gold", "Silver", "White", "Yellow"]
        self.add_label(self.frame_step13, "Primary Color (สีหลัก)")
        self.dropdown_primary = ctk.CTkOptionMenu(self.frame_step13, values=self.etsy_colors, width=200); self.dropdown_primary.set("Red"); self.dropdown_primary.pack(pady=(0, 10), anchor="w")
        self.add_label(self.frame_step13, "Secondary Color (สีรอง)")
        self.dropdown_secondary = ctk.CTkOptionMenu(self.frame_step13, values=self.etsy_colors, width=200); self.dropdown_secondary.set("Gray"); self.dropdown_secondary.pack(pady=(0, 10), anchor="w")
        self.btn_etsy = self.add_button(self.frame_step13, "Create Listing", self.action_etsy_listing, "#F1641E")
        self.add_desc(self.frame_step13, "*อย่าลืมเปิด Modal ในหน้า DDCM ไว้รอ*")

        # --- Status Section ---
        self.status_label = ctk.CTkLabel(self, text="Connecting...", text_color="orange", font=("Arial", 15, "bold"))
        self.status_label.grid(row=2, column=0, pady=10)
        
        self.load_defaults()
        self.start_browser_thread()

    # --- UI Helpers ---
    def create_step_frame(self, title):
        frame = ctk.CTkFrame(self.main_container); frame.pack(fill="x", padx=10, pady=10)
        lbl = ctk.CTkLabel(frame, text=title, font=("Arial", 18, "bold"), text_color="white"); lbl.pack(pady=10, padx=15, anchor="w")
        inner = ctk.CTkFrame(frame, fg_color="transparent"); inner.pack(fill="both", expand=True, padx=25, pady=(0, 15)); return inner
    def add_label(self, parent, text, text_color="white"):
        lbl = ctk.CTkLabel(parent, text=text, font=("Arial", 13), text_color=text_color); lbl.pack(pady=(5, 0), anchor="w"); return lbl
    def add_entry(self, parent, placeholder, default_val="", width=400):
        e = ctk.CTkEntry(parent, placeholder_text=placeholder, width=width)
        if default_val: e.insert(0, default_val)
        e.pack(pady=(0, 10), anchor="w"); return e
    def add_button(self, parent, text, command, color):
        btn = ctk.CTkButton(parent, text=text, command=command, fg_color=color, width=200, height=40, font=("Arial", 14, "bold"))
        btn.pack(pady=(5, 10), anchor="w"); return btn
    def add_desc(self, parent, text, color="white", font_size=13):
        lbl = ctk.CTkLabel(parent, text=text, font=("Arial", font_size), wraplength=750, justify="left", text_color=color); lbl.pack(pady=(0, 5), anchor="w"); return lbl

    # --- Logic Methods ---
    def action_save_defaults(self):
        c = {"element_name": self.entry_element_name.get().strip(), "element_path": self.entry_element_path.get().strip(), "local_path": self.entry_local_path.get().strip(), "remote_path": self.entry_remote_path.get().strip()}
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f: json.dump(c, f, indent=4)
            self.log("Defaults saved successfully!")
        except Exception as e: self.log(f"Error: {e}", error=True)

    def load_defaults(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    c = json.load(f)
                    if "element_name" in c:
                        self.entry_element_name.delete(0, 'end'); self.entry_element_name.insert(0, c.get("element_name", ""))
                    self.entry_element_path.insert(0, c.get("element_path", ""))
                    self.entry_local_path.insert(0, c.get("local_path", ""))
                    self.entry_remote_path.insert(0, c.get("remote_path", ""))
                return
            except: pass
        if os.name == 'nt':
            self.entry_element_path.insert(0, r"C:\Files\Project\local DDCM\Elements")
            self.entry_local_path.insert(0, r"C:\Files\Project\local DDCM")
            self.entry_remote_path.insert(0, r"G:\My Drive\Projects\DDCM\Cliparts DDCM")
        else:
            h = os.path.expanduser("~")
            self.entry_element_path.insert(0, os.path.join(h, "Documents/DDCM/Elements"))
            self.entry_local_path.insert(0, os.path.join(h, "Documents/DDCM"))
            self.entry_remote_path.insert(0, "/Users/litarcopperkaikem/Library/CloudStorage/GoogleDrive-cheetah6541@gmail.com/My Drive/Projects/DDCM/Cliparts DDCM")

    def log(self, m, error=False):
        c = "red" if error else "white"
        self.status_label.configure(text=m, text_color=c); print(m)
    def start_browser_thread(self): threading.Thread(target=self._start_browser_task).start()
    def _start_browser_task(self):
        if self.bot.start_browser(attach=True): self.log("Connected to Browser."); self.status_label.configure(text_color="#27AE60")
        else: self.log("Failed: Close ALL Chrome & Restart App", error=True)

    def action_gemini_single(self): threading.Thread(target=self._run_gemini_gen, args=("single",)).start()
    def action_gemini_companion(self): threading.Thread(target=self._run_gemini_gen, args=("companion",)).start()
    def action_gemini_elements(self): threading.Thread(target=self._run_gemini_gen, args=("elements",)).start()
    def action_download_images(self): threading.Thread(target=self._run_download_images).start()

    def _run_download_images(self):
        try:
            self.log("Starting Image Download...")
            if not self.bot.switch_to_tab_containing("gemini.google.com/app"): self.log("Error: Gemini tab not found!", error=True); return
            time.sleep(1); self.bot.driver.execute_script("window.scrollTo(0, 0);")
            scs = self.bot.driver.find_elements(By.CSS_SELECTOR, ".infinite-scroller, .conversation-container, main")
            for s in scs: self.bot.driver.execute_script("arguments[0].scrollTop = 0;", s)
            time.sleep(2); btns = self.bot.driver.find_elements(By.CSS_SELECTOR, "download-generated-image-button > button")
            if not btns:
                self.bot.driver.execute_script("window.scrollTo(0, 1000);"); time.sleep(1)
                btns = self.bot.driver.find_elements(By.CSS_SELECTOR, "download-generated-image-button > button")
            if not btns: self.log("Error: No download buttons found.", error=True); return
            cnt = len(btns); self.log(f"Found {cnt} images.")
            for i in range(cnt):
                self.log(f"Downloading {i+1}/{cnt}...")
                try:
                    curr_btns = self.bot.driver.find_elements(By.CSS_SELECTOR, "download-generated-image-button > button")
                    if i >= len(curr_btns): break
                    btn = curr_btns[i]; self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(1); ohtml = btn.get_attribute("innerHTML")
                    try: btn.click()
                    except: self.bot.driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1); wt = 0
                    while wt < 20:
                        try:
                            c_btn = self.bot.driver.find_elements(By.CSS_SELECTOR, "download-generated-image-button > button")[i]
                            if c_btn.get_attribute("innerHTML") == ohtml: break
                        except: pass
                        time.sleep(1); wt += 1
                    time.sleep(1)
                except Exception as e: self.log(f"Error clicking btn {i+1}: {e}", error=True)
            self.log("Moving files...")
            try:
                dp = os.path.join(os.path.expanduser("~"), "Downloads"); ip = os.path.join(dp, "images")
                os.makedirs(ip, exist_ok=True); mc = 0
                for f in os.listdir(dp):
                    if f.lower().endswith(".png"):
                        src, dst = os.path.join(dp, f), os.path.join(ip, f)
                        if os.path.exists(dst): os.remove(dst)
                        shutil.move(src, dst); mc += 1
                self.log(f"Moved {mc} PNG files to 'Downloads/images'.")
            except Exception as me: self.log(f"Error moving images: {me}", error=True)
        except Exception as e: self.log(f"Error: {e}", error=True)

    def _run_gemini_gen(self, mode="single"):
        try:
            self.log(f"Starting Gemini Gen ({mode})...")
            if not self.bot.switch_to_tab_containing("ddcm.litarandfriends.uk"): self.log("Error: DDCM tab not found!", error=True); return
            time.sleep(1); containers = []
            if mode == "single": containers = [("Set 1", "body > main > div.modal-overlay > div > div:nth-child(2) > div:nth-child(13) > div > div > div > div:nth-child(1) > div:nth-child(2)")]
            elif mode == "companion": containers = [("Set 2", "body > main > div.modal-overlay > div > div:nth-child(2) > div:nth-child(13) > div > div > div > div:nth-child(2) > div:nth-child(2)")]
            elif mode == "elements": containers = [("Elements", "body > main > div.modal-overlay > div > div:nth-child(2) > div:nth-child(13) > div > div > div > div:nth-child(3) > div:nth-child(2)")]
            all_p = []
            for n, sel in containers:
                try:
                    cont = WebDriverWait(self.bot.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                    self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cont); time.sleep(0.5)
                    bs = cont.find_elements(By.TAG_NAME, "button")
                    if not bs: bs = cont.find_elements(By.XPATH, ".//button")
                    for i, b in enumerate(bs):
                        try:
                            self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", b); time.sleep(0.5)
                            try: b.click()
                            except: self.bot.driver.execute_script("arguments[0].click();", b)
                            time.sleep(1.0); text = self.clipboard_get()
                            if text: all_p.append(text)
                        except: pass
                except Exception as e: self.log(f"Error {n}: {e}", error=True)
            if not all_p: self.log("No prompts collected."); return
            try:
                if mode == "single": cl = int(self.entry_single_count.get().strip())
                elif mode == "companion": cl = int(self.entry_companion_count.get().strip())
                else: cl = int(self.entry_elements_count.get().strip())
            except: cl = 5
            all_p = all_p[:cl]
            self.log(f"Processing {len(all_p)} prompts. Switching to Gemini...")
            if not self.bot.switch_to_tab_containing("gemini.google.com/app"): self.log("Error: Gemini tab not found!", error=True); return
            time.sleep(1); strats = ["//div[contains(@class, 'ql-editor') and @contenteditable='true']", "//rich-textarea//div[@contenteditable='true']", "//div[@contenteditable='true' and @role='textbox']"]
            for i, p in enumerate(all_p):
                self.log(f"Processing Gemini {i+1}/{len(all_p)}...")
                try:
                    box = None
                    for s in strats:
                        try:
                            tmp = WebDriverWait(self.bot.driver, 5).until(EC.presence_of_element_located((By.XPATH, s)))
                            if tmp.is_displayed(): box = tmp; break
                        except: continue
                    if not box: self.log("Error: No Input Box", error=True); return
                    try: box.click()
                    except: self.bot.driver.execute_script("arguments[0].click();", box)
                    time.sleep(0.5); self.bot.driver.execute_script("if(arguments[0].textContent !== undefined) { arguments[0].textContent = ''; } else { arguments[0].innerText = ''; }", box)
                    time.sleep(0.5); box.send_keys(p); time.sleep(1); box.send_keys(Keys.ENTER)
                    self.log(f"  -> Sent {i+1}. Waiting..."); time.sleep(3)
                    st_xp = "//mat-icon[contains(@data-mat-icon-name, 'stop') or @fonticon='stop']"
                    mw, el = 120, 0
                    while el < mw:
                        try: self.bot.driver.find_element(By.XPATH, st_xp); time.sleep(2); el += 2
                        except: self.log("  -> Finished."); break
                    time.sleep(3)
                except Exception as e: self.log(f"Error: {e}", error=True); return
            self.log("Gemini Automation Complete!")
        except Exception as e: self.log(f"Critical Error: {e}", error=True)

    def action_export_png(self):
        self.log("Running Export PNG...")
        if not self.bot.switch_to_tab_containing("canva.com"): self.log("Error: Canva not found."); return
        ps = self.entry_png_pages.get().strip() or "1-4"
        steps = [("Rename to 'png'", "//input[@aria-label='Design title']", "png"), ("Share", "//button[.//span[text()='Share']]"), ("Download", "//button[@aria-label='Download']"), ("Type", "//button[@aria-label='File type']"), ("PNG", "//li[@role='option']//div[contains(text(), 'PNG')]"), ("Size 1", "//input[@role='spinbutton']", "1"), ("Trans", "//label[.//p[contains(text(), 'Transparent background')]]"), (f"Pages {ps}", "//input[@placeholder='Select pages']", ps), ("Go", "//button[@type='submit'][.//span[contains(text(), 'Download')]]")]
        self._execute_steps(steps)

    def action_export_jpg(self):
        self.log("Running Export JPG...")
        if not self.bot.switch_to_tab_containing("canva.com"): self.log("Error: Canva not found."); return
        ps = self.entry_jpg_pages.get().strip() or "6-9"
        steps = [("Rename to 'jpg'", "//input[@aria-label='Design title']", "jpg"), ("Share", "//button[.//span[text()='Share']]"), ("Download", "//button[@aria-label='Download']"), ("Type", "//button[@aria-label='File type']"), ("JPG", "//li[@role='option']//div[contains(text(), 'JPG')]"), ("Size 0.5", "//input[@role='spinbutton']", "0.5"), (f"Pages {ps}", "//input[@placeholder='Select pages']", ps), ("Go", "//button[@type='submit'][.//span[contains(text(), 'Download')]]")]
        self._execute_steps(steps)

    def action_export_pdf(self):
        self.log("Running Export PDF...")
        if not self.bot.switch_to_tab_containing("canva.com"): self.log("Error: Canva not found."); return
        ps = self.entry_pdf_pages.get().strip() or "10"
        steps = [("Rename to 'pdf'", "//input[@aria-label='Design title']", "pdf_for_downloading"), ("Share", "//button[.//span[text()='Share']]"), ("Download", "//button[@aria-label='Download']"), ("Type", "//button[@aria-label='File type']"), ("PDF", "//li[@role='option']//div[contains(text(), 'PDF Standard')]"), (f"Pages {ps}", "//input[@placeholder='Select pages']", ps), ("Go", "//button[@type='submit'][.//span[contains(text(), 'Download')]]")]
        self._execute_steps(steps)

    def action_export_all(self):
        self.log("Starting ALL Exports..."); self.action_export_png(); time.sleep(8); self.action_export_jpg(); time.sleep(8); self.action_export_pdf()

    def action_create_folders(self):
        fn = self.entry_folder_name.get().strip()
        if not fn: self.log("Error: Folder Name required.", error=True); return
        configs = [{"path": self.entry_local_path.get().strip(), "folder": fn, "subfolders": ["4000x4000", "Download file", "Original", "Preview", "Sticker Set"]}, {"path": self.entry_remote_path.get().strip(), "folder": fn, "subfolders": ["4000x4000", "Sticker Set"]}]
        for i, c in enumerate(configs):
            base, name, subs = c["path"], c["folder"], c["subfolders"]
            if not base or not name: continue
            f = os.path.join(base, name); os.makedirs(f, exist_ok=True); cr = 0
            for sub in subs:
                sp = os.path.join(f, sub)
                if not os.path.exists(sp): os.makedirs(sp, exist_ok=True); cr += 1
            self.log(f"Path {i+1}: {'Done' if cr > 0 else 'Exist'}")

    def action_copy_upscale(self):
        fn, lp = self.entry_folder_name.get().strip(), self.entry_local_path.get().strip()
        if not fn or not lp: self.log("Error: Paths required.", error=True); return
        clean_name = fn.split(" - ", 1)[1] if " - " in fn else fn
        base, dp = os.path.join(lp, fn), os.path.join(os.path.expanduser("~"), "Downloads")
        img_d = os.path.join(dp, "images")
        if not os.path.exists(img_d): self.log("Error: No 'images' folder", error=True); return
        up_d = next((os.path.join(img_d, it) for it in os.listdir(img_d) if os.path.isdir(os.path.join(img_d, it)) and "upscayl" in it.lower()), None)
        if up_d:
            d4000 = os.path.join(base, "4000x4000"); os.makedirs(d4000, exist_ok=True)
            files = sorted([f for f in os.listdir(up_d) if os.path.isfile(os.path.join(up_d, f))])
            for i, it in enumerate(files):
                shutil.copy2(os.path.join(up_d, it), os.path.join(d4000, f"{clean_name} ({i+1}){os.path.splitext(it)[1]}"))
            shutil.rmtree(up_d); self.log(f"Moved {len(files)} to 4000x4000.")
        else: self.log("Error: No upscayl folder", error=True); return
        dorig = os.path.join(base, "Original"); os.makedirs(dorig, exist_ok=True)
        files = sorted([f for f in os.listdir(img_d) if os.path.isfile(os.path.join(img_d, f))])
        for i, it in enumerate(files):
            shutil.copy2(os.path.join(img_d, it), os.path.join(dorig, f"{clean_name} ({i+1}){os.path.splitext(it)[1]}"))
        shutil.rmtree(img_d); self.log(f"Moved {len(files)} to Original.")

    def action_unzip_downloads(self):
        self.log("Starting Unzip...")
        try:
            dp = os.path.join(os.path.expanduser("~"), "Downloads")
            for zfn in [f for f in os.listdir(dp) if f.lower().endswith('.zip')]:
                zp, ep = os.path.join(dp, zfn), os.path.join(dp, os.path.splitext(zfn)[0])
                with zipfile.ZipFile(zp, 'r') as zr: os.makedirs(ep, exist_ok=True); zr.extractall(ep)
            self.log("Unzip Complete!")
        except Exception as e: self.log(f"Unzip Error: {e}", error=True)

    def action_download_to_local(self):
        fn, lp = self.entry_folder_name.get().strip(), self.entry_local_path.get().strip()
        if not fn or not lp: self.log("Error: Paths required.", error=True); return
        base, dp = os.path.join(lp, fn), os.path.join(os.path.expanduser("~"), "Downloads")
        for s, d_sub in [("png", "Sticker Set"), ("jpg", "Preview")]:
            src, dst = os.path.join(dp, s), os.path.join(base, d_sub)
            if os.path.exists(src):
                if not os.path.exists(dst): self.log(f"Error: No {d_sub}", error=True); continue
                c = 0
                for it in os.listdir(src):
                    if os.path.isfile(os.path.join(src, it)): shutil.copy2(os.path.join(src, it), os.path.join(dst, it)); c += 1
                self.log(f"Copied {c} {s} files.")
        pdfs = [f for f in os.listdir(dp) if f.lower().endswith('.pdf')]
        if pdfs:
            dst = os.path.join(base, "Download file")
            if not os.path.exists(dst): self.log("Error: No Download file", error=True); return
            ptc = next((p for p in pdfs if "pdf_for_downloading" in p), pdfs[0])
            shutil.copy2(os.path.join(dp, ptc), os.path.join(dst, ptc)); self.log(f"Copied {ptc}.")

    def action_local_remote(self):
        fn, lp, rp = self.entry_folder_name.get().strip(), self.entry_local_path.get().strip(), self.entry_remote_path.get().strip()
        if not all([fn, lp, rp]): self.log("Error: All paths required.", error=True); return
        total = 0
        for sub in ["4000x4000", "Sticker Set"]:
            s, d = os.path.join(lp, fn, sub), os.path.join(rp, fn, sub)
            if not os.path.exists(s): continue
            os.makedirs(d, exist_ok=True)
            for it in os.listdir(s):
                if os.path.isfile(os.path.join(s, it)): shutil.copy2(os.path.join(s, it), os.path.join(d, it)); total += 1
        self.log(f"Copied {total} to Remote.")
        en, ep = self.entry_element_name.get().strip(), self.entry_element_path.get().strip()
        if en and ep:
            es, rd = os.path.join(ep, en), os.path.join(rp, fn, "4000x4000")
            if os.path.exists(es):
                os.makedirs(rd, exist_ok=True); c = 0
                for it in os.listdir(es):
                    if os.path.isfile(os.path.join(es, it)): shutil.copy2(os.path.join(es, it), os.path.join(rd, it)); c += 1
                self.log(f"Copied {c} elements to Remote.")

    def action_etsy_listing(self):
        self.log("Starting Etsy..."); up, us = self.dropdown_primary.get(), self.dropdown_secondary.get()
        if not self.bot.switch_to_tab_containing("ddcm.litarandfriends.uk"): self.log("Error: No DDCM", error=True); return
        fields = [("name", "/html/body/main/div[4]/div/div[2]/div[2]/div/div/div"), ("tag", "/html/body/main/div[4]/div/div[2]/div[10]/div/div/div"), ("description", "/html/body/main/div[4]/div/div[2]/div[12]/div/div/div/div"), ("theme", "/html/body/main/div[4]/div/div[2]/div[5]/div/div/div"), ("price", "/html/body/main/div[4]/div/div[2]/div[8]/div/div/div")]
        data = {}
        for fn, xp in fields:
            try: data[fn] = WebDriverWait(self.bot.driver, 5).until(EC.presence_of_element_located((By.XPATH, xp))).text.strip()
            except: self.log(f"Error: {fn}", error=True); return
        self.bot.driver.switch_to.new_window('tab'); self.bot.driver.get("https://www.etsy.com/your/shops/me/listing-editor/create")
        try: WebDriverWait(self.bot.driver, 20).until(lambda d: "etsy.com" in d.current_url); time.sleep(2)
        except: self.log("Error: Etsy timeout", error=True); return
        setup = [("Cat", "//div[contains(@class, 'le-category-action-item') and .//h2[contains(text(), 'Clip Art')]]"), ("Digital", "//input[@name='listing_type_options_group' and @value='download']"), ("I did", "//label[contains(., 'I did')]"), ("Supply", "//label[contains(., 'A supply or tool')]"), ("Year", "//select[@id='when-made-select']", "2020_2026"), ("AI", "//input[@value='ai_gen']")]
        for n, x, *v in setup:
            try:
                el = WebDriverWait(self.bot.driver, 10).until(EC.presence_of_element_located((By.XPATH, x))); self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el); time.sleep(0.3)
                if v: from selenium.webdriver.support.ui import Select; Select(el).select_by_value(v[0])
                else: el.click()
                time.sleep(0.5)
            except: self.log(f"Etsy Error: {n}", error=True); return
        steps = [("INPUT", "//textarea[@id='listing-title-input']", data.get('name', '')), ("INPUT", "//textarea[@id='listing-description-textarea' or @name='description']", data.get('description', '')), ("INPUT", "//input[@id='listing-tags-input']", data.get('tag', '')), ("CLICK", "//button[@id='listing-tags-button']"), ("LOG", "Craft"), ("DELAY", "1"), ("INPUT_BY_LABEL", "Craft type", "Scrapbooking"), ("WAIT", "//label[contains(., 'Scrapbooking')]"), ("SELECT_CHECKBOX", "Scrapbooking"), ("SPECIAL_ESC", ""), ("DELAY", "1"), ("LOG", "Primary"), ("INPUT_BY_LABEL", "Primary color", up), ("WAIT", "//button[@role='menuitemradio']//p[text()='" + up + "']"), ("CLICK", "//button[@role='menuitemradio']//p[text()='" + up + "']"), ("SPECIAL_ESC", ""), ("LOG", "Secondary"), ("INPUT_BY_LABEL", "Secondary color", us), ("WAIT", "//button[@role='menuitemradio']//p[text()='" + us + "']"), ("CLICK", "//button[@role='menuitemradio']//p[text()='" + us + "']"), ("SPECIAL_ESC", ""), ("LOG", "Price"), ("INPUT", "//input[@id='listing-price-input']", data.get('price', '5.99')), ("LOG", "Quantity"), ("INPUT", "//input[@id='listing-quantity-input']", "999"), ("LOG", "Ads Off"), ("OFF_CHECKBOX", "//*[@id='listing-is-promoted-checkbox']"), ("LOG", "Finalizing"), ("SELECT_DROPDOWN", "//select[@id='shop-section-select']", data.get('theme', 'General'))]
        for s in steps:
            cmd, xp = s[0], s[1]
            try:
                if cmd == "LOG": self.log(xp); continue
                if cmd == "DELAY": time.sleep(float(xp)); continue
                if cmd == "SPECIAL_ESC":
                    try: self.bot.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE); self.bot.driver.execute_script("if(document.activeElement) document.activeElement.blur(); document.body.click();")
                    except: pass
                    time.sleep(1); continue
                if cmd == "WAIT": WebDriverWait(self.bot.driver, 15).until(EC.presence_of_element_located((By.XPATH, xp))); continue
                if cmd == "INPUT_BY_LABEL":
                    ln, tt = xp, str(s[2]); ss = [f"//div[.//label[contains(., '{ln}')]]//input", f"//label[contains(., '{ln}')]/following::input[1]", "//input[@placeholder='Type to search…']"]
                    el = None
                    for st in ss:
                        try:
                            tmp = self.bot.driver.find_element(By.XPATH, st)
                            if tmp.is_displayed(): el = tmp; break
                        except: continue
                    if not el: self.log(f"Error: {ln}", error=True); return
                    self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el); time.sleep(0.5); el.click()
                    self.bot.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", el, tt)
                    el.send_keys(Keys.SPACE); time.sleep(0.1); el.send_keys(Keys.BACKSPACE); continue
                if cmd == "SELECT_CHECKBOX":
                    lt = xp; lb = WebDriverWait(self.bot.driver, 15).until(EC.presence_of_element_located((By.XPATH, f"//label[contains(., '{lt}')]")))
                    cid = lb.get_attribute("for"); cb = self.bot.driver.find_element(By.ID, cid)
                    if not (cb.is_selected() or self.bot.driver.execute_script("return arguments[0].checked;", cb)): self.bot.driver.execute_script("arguments[0].click();", lb)
                    time.sleep(0.5); continue
                if cmd == "OFF_CHECKBOX":
                    cb = WebDriverWait(self.bot.driver, 15).until(EC.presence_of_element_located((By.XPATH, xp)))
                    if cb.is_selected() or self.bot.driver.execute_script("return arguments[0].checked;", cb):
                        try: cb.click()
                        except: self.bot.driver.execute_script("arguments[0].click();", cb)
                    time.sleep(0.5); continue
                if cmd == "SELECT_DROPDOWN":
                    tv = s[2]; el = WebDriverWait(self.bot.driver, 15).until(EC.presence_of_element_located((By.XPATH, xp)))
                    from selenium.webdriver.support.ui import Select; Select(el).select_by_visible_text(tv); time.sleep(0.5); continue
                el = WebDriverWait(self.bot.driver, 15).until(EC.presence_of_element_located((By.XPATH, xp))); self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el); time.sleep(0.5)
                if cmd == "INPUT":
                    tv = str(s[2]); el.click(); time.sleep(0.3)
                    self.bot.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", el, tv)
                elif cmd == "CLICK":
                    try: el.click()
                    except: self.bot.driver.execute_script("arguments[0].click();", el)
                time.sleep(0.5)
            except Exception as e: self.log(f"Error: {cmd}", error=True); return
        self.log("Etsy Listing populated!")

    def _execute_steps(self, steps):
        for n, xp, *v in steps:
            try:
                el = WebDriverWait(self.bot.driver, 20).until(EC.presence_of_element_located((By.XPATH, xp)))
                self.bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el); time.sleep(0.5)
                if v:
                    val = v[0]
                    if any(k in xp for k in ["Select pages", "spinbutton", "Design title"]):
                        try: el.click()
                        except: self.bot.driver.execute_script("arguments[0].click();", el)
                        time.sleep(0.5); self.bot.driver.execute_script("arguments[0].value = '';", el)
                        for _ in range(15): el.send_keys(Keys.BACKSPACE)
                        el.send_keys(val); time.sleep(0.5)
                        if "Design title" in xp or "spinbutton" in xp: el.send_keys(Keys.ENTER)
                        else: el.send_keys(Keys.TAB)
                    else: self.bot.input_text(xp, val)
                else:
                    try: el.click()
                    except: self.bot.driver.execute_script("arguments[0].click();", el)
                self.log(f"Success: {n}"); time.sleep(0.5)
            except Exception as e: self.log(f"Error [{n}]: {str(e)[:50]}", error=True); return False
        return True

    def clipboard_get(self):
        try: return self.selection_get(selection='CLIPBOARD')
        except: return ""

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    app = App()
    app.mainloop()
