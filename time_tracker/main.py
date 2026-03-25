import sys
from pathlib import Path
from typing import Any, cast

import customtkinter as ctk
from PIL import Image, ImageTk

from time_tracker.database import DBManager

if sys.platform == "win32":
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "com.opencode.timetracker"
        )
    except Exception:
        pass


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
ICON_PNG = ASSETS_DIR / "icon.png"
ICON_ICO = ASSETS_DIR / "icon.ico"


class TimerCard(ctk.CTkFrame):
    def __init__(self, master, timer_data, db_manager, on_update):
        super().__init__(master)
        self.timer_id = timer_data["id"]
        self.client_id = timer_data["client_id"]
        self.db = db_manager
        self.on_update = on_update
        self.is_running = timer_data["start_timestamp"] is not None

        self.label_name = ctk.CTkLabel(
            self,
            text=f"{timer_data['client_name']} ({timer_data['client_tag']})",
            font=("Arial", 14, "bold"),
            anchor="w",
        )
        self.label_name.pack(side="left", padx=10, fill="x", expand=True)

        self.time_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.time_frame.pack(side="left", padx=10)

        self.label_time = ctk.CTkLabel(
            self.time_frame, text="0.00 min", font=("Courier New", 18, "bold")
        )
        self.label_time.pack(side="top")

        self.label_hours = ctk.CTkLabel(
            self.time_frame,
            text="0.00 hours",
            font=("Arial", 10),
            text_color="gray",
        )
        self.label_hours.pack(side="top")

        btn_text = "Stop" if self.is_running else "Start"
        self.btn_toggle = ctk.CTkButton(
            self,
            text=btn_text,
            command=self.toggle_timer,
            width=60,
        )
        self.btn_toggle.pack(side="left", padx=5)

        self.btn_reset = ctk.CTkButton(
            self,
            text="Reset",
            command=self.reset_timer,
            width=60,
            fg_color="darkred",
        )
        self.btn_reset.pack(side="left", padx=5)

        self._icon_ref = None
        self.update_display()

    def toggle_timer(self):
        if self.is_running:
            self.db.stop_timer(self.timer_id)
            self.is_running = False
            self.btn_toggle.configure(text="Start")
        else:
            self.db.start_timer(self.timer_id)
            self.is_running = True
            self.btn_toggle.configure(text="Stop")
            self.update_display()

        self.on_update()

    def reset_timer(self):
        self.db.reset_timer(self.timer_id)
        self.is_running = False
        self.btn_toggle.configure(text="Start")
        self.update_display()
        self.on_update()

    def update_display(self):
        total_min = self.db.get_total_minutes(self.client_id)
        self.label_time.configure(text=f"{total_min:.2f} min")
        self.label_hours.configure(text=f"{total_min / 60.0:.2f} hours")
        if self.is_running:
            self.after(1000, self.update_display)


class TimeTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Opencode Time Tracker")
        self.geometry("600x800")
        self.db = DBManager(db_path="storage.db")
        self.timer_cards = []
        self._icon_ref = None

        self._setup_icon()

        self.grid_columnconfigure(0, weight=1)

        self.add_frame = ctk.CTkFrame(self)
        self.add_frame.pack(pady=20, padx=20, fill="x")

        self.entry_name = ctk.CTkEntry(self.add_frame, placeholder_text="Client Name")
        self.entry_name.pack(side="left", padx=5, expand=True, fill="x")

        self.entry_tag = ctk.CTkEntry(
            self.add_frame,
            placeholder_text="Tag (e.g. ACME-01)",
        )
        self.entry_tag.pack(side="left", padx=5, expand=True, fill="x")

        self.btn_add = ctk.CTkButton(
            self.add_frame,
            text="Add Client",
            command=self.add_client,
        )
        self.btn_add.pack(side="left", padx=5)

        self.sub_frame = ctk.CTkFrame(self)
        self.sub_frame.pack(pady=10, padx=20, fill="x")

        self.label_sub = ctk.CTkLabel(self.sub_frame, text="Log Subcontractor Time:")
        self.label_sub.pack(side="left", padx=5)

        self.client_var = ctk.StringVar(value="Select Client")
        self.client_option = ctk.CTkOptionMenu(
            self.sub_frame,
            variable=self.client_var,
            values=["Select Client"],
        )
        self.client_option.pack(side="left", padx=5)

        self.entry_sub = ctk.CTkEntry(
            self.sub_frame,
            placeholder_text="Minutes",
            width=100,
        )
        self.entry_sub.pack(side="left", padx=5)

        self.btn_sub = ctk.CTkButton(
            self.sub_frame,
            text="Log",
            command=self.log_sub_time,
            width=60,
        )
        self.btn_sub.pack(side="left", padx=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Active Timers")
        self.scroll_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.refresh_timers()

    def _setup_icon(self):
        if ICON_PNG.exists():
            try:
                image = Image.open(ICON_PNG)
                self._icon_ref = ImageTk.PhotoImage(image)
                self.iconphoto(True, cast(Any, self._icon_ref))
            except Exception:
                pass

        if sys.platform == "win32" and ICON_ICO.exists():
            try:
                self.iconbitmap(default=str(ICON_ICO))
            except Exception:
                pass

        if sys.platform == "darwin" and ICON_PNG.exists():
            try:
                import AppKit

                appkit = cast(Any, AppKit)
                ns_image = appkit.NSImage.alloc().initByReferencingFile_(str(ICON_PNG))
                appkit.NSApplication.sharedApplication().setApplicationIconImage_(
                    ns_image
                )
            except Exception:
                pass

    def add_client(self):
        name = self.entry_name.get().strip()
        tag = self.entry_tag.get().strip()
        if not name or not tag:
            return

        self.db.add_client(name, tag)
        self.entry_name.delete(0, "end")
        self.entry_tag.delete(0, "end")
        self.refresh_timers()

    def log_sub_time(self):
        selected = self.client_var.get()
        if selected == "Select Client":
            return

        try:
            minutes = float(self.entry_sub.get())
        except ValueError:
            return

        tag = selected.rsplit("(", 1)[-1].rstrip(")")
        clients = self.db.get_clients()
        client = next((item for item in clients if item["tag"] == tag), None)
        if client is None:
            return

        self.db.log_time(client["id"], minutes, "subcontractor")
        self.entry_sub.delete(0, "end")
        self.refresh_timers()

    def refresh_timers(self):
        clients = self.db.get_clients()
        client_options = [f"{c['name']} ({c['tag']})" for c in clients]
        if client_options:
            self.client_option.configure(values=client_options)
            if self.client_var.get() not in client_options:
                self.client_var.set(client_options[0])
        else:
            self.client_option.configure(values=["Select Client"])
            self.client_var.set("Select Client")

        for card in self.timer_cards:
            card.destroy()
        self.timer_cards = []

        for timer in self.db.get_timers():
            card = TimerCard(self.scroll_frame, timer, self.db, lambda: None)
            card.pack(pady=10, padx=10, fill="x")
            self.timer_cards.append(card)


def main():
    app = TimeTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
