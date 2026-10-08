import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import threading
import time
import logging
import cv2
from PIL import Image
from .base_frame import BaseFrame
from config import settings
from utils import detect_and_crop_face, save_face_image, count_user_images, frame_to_pil, pil_to_ctk_image, VALID_EXTENSIONS

logger = logging.getLogger(__name__)


class UserManagementPage(BaseFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._capture_running = False
        self._capture_count = 0
        self._selected_user = None
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(20, 10))
        ctk.CTkLabel(
            header, text="User Management",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=settings.TEXT_PRIMARY
        ).pack(side="left")

        # Left panel - user list
        left = ctk.CTkFrame(
            self, fg_color=settings.BG_SURFACE,
            corner_radius=16, border_width=1, border_color="#2A2A3E"
        )
        left.grid(row=1, column=0, sticky="nsew", padx=(24, 12), pady=(0, 20))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left, text="USERS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=settings.TEXT_SECONDARY
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))

        self._user_list_frame = ctk.CTkScrollableFrame(
            left, fg_color="transparent", corner_radius=0
        )
        self._user_list_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._user_list_frame.grid_columnconfigure(0, weight=1)

        add_btn = ctk.CTkButton(
            left, text="+ Add New User",
            fg_color=settings.ACCENT_COLOR, hover_color="#6A50E0",
            height=38, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._show_add_user_dialog
        )
        add_btn.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))

        # Right panel - user detail
        self._right = ctk.CTkFrame(
            self, fg_color=settings.BG_SURFACE,
            corner_radius=16, border_width=1, border_color="#2A2A3E"
        )
        self._right.grid(row=1, column=1, sticky="nsew", padx=(0, 24), pady=(0, 20))
        self._right.grid_columnconfigure(0, weight=1)
        self._right.grid_rowconfigure(2, weight=1)

        self._detail_placeholder = ctk.CTkLabel(
            self._right,
            text="👤\n\nSelect a user to manage their profile,\nimages, and assigned song.",
            font=ctk.CTkFont(size=14),
            text_color=settings.TEXT_SECONDARY,
            justify="center"
        )
        self._detail_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        self._build_detail_widgets()
        self._refresh_user_list()

    def _build_detail_widgets(self):
        """Build the user detail area (hidden until user selected)."""
        self._detail_container = ctk.CTkFrame(self._right, fg_color="transparent")

        # Name header
        name_row = ctk.CTkFrame(self._detail_container, fg_color="transparent")
        name_row.pack(fill="x", padx=20, pady=(20, 0))
        self._detail_name = ctk.CTkLabel(
            name_row, text="",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=settings.TEXT_PRIMARY
        )
        self._detail_name.pack(side="left")

        delete_btn = ctk.CTkButton(
            name_row, text="🗑 Delete User",
            fg_color="#CC2222", hover_color="#AA1111",
            height=34, corner_radius=8, width=130,
            command=self._delete_selected_user
        )
        delete_btn.pack(side="right")

        # Stats row
        stats_row = ctk.CTkFrame(self._detail_container, fg_color="transparent")
        stats_row.pack(fill="x", padx=20, pady=(8, 16))
        self._img_count_label = ctk.CTkLabel(
            stats_row, text="0 images",
            font=ctk.CTkFont(size=12),
            text_color=settings.TEXT_SECONDARY
        )
        self._img_count_label.pack(side="left")

        # Song section
        song_frame = ctk.CTkFrame(
            self._detail_container, fg_color=settings.BG_DARK,
            corner_radius=12
        )
        song_frame.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(
            song_frame, text="ASSIGNED SONG",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=settings.TEXT_SECONDARY
        ).pack(anchor="w", padx=14, pady=(12, 4))
        row = ctk.CTkFrame(song_frame, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(0, 12))
        self._song_label = ctk.CTkLabel(
            row, text="No song assigned",
            font=ctk.CTkFont(size=12),
            text_color=settings.TEXT_SECONDARY
        )
        self._song_label.pack(side="left", expand=True, fill="x")
        ctk.CTkButton(
            row, text="Browse",
            fg_color=settings.ACCENT_COLOR, hover_color="#6A50E0",
            height=30, corner_radius=8, width=80,
            command=self._browse_song
        ).pack(side="right")

        # Images section - tabs
        img_frame = ctk.CTkFrame(
            self._detail_container, fg_color=settings.BG_DARK, corner_radius=12
        )
        img_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        img_frame.grid_columnconfigure(0, weight=1)
        img_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            img_frame, text="FACE IMAGES",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=settings.TEXT_SECONDARY
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 8))

        tab_row = ctk.CTkFrame(img_frame, fg_color="transparent")
        tab_row.grid(row=1, column=0, sticky="ew", padx=14)
        ctk.CTkButton(
            tab_row, text="📁 Upload Images",
            fg_color=settings.BG_SURFACE, hover_color="#2A2A4E",
            height=36, corner_radius=8, text_color=settings.TEXT_PRIMARY,
            command=self._upload_images
        ).pack(side="left", padx=(0, 8))
        self._webcam_btn = ctk.CTkButton(
            tab_row, text="📷 Capture from Webcam",
            fg_color=settings.BG_SURFACE, hover_color="#2A2A4E",
            height=36, corner_radius=8, text_color=settings.TEXT_PRIMARY,
            command=self._toggle_webcam_capture
        )
        self._webcam_btn.pack(side="left")

        # Webcam capture preview
        self._webcam_frame = ctk.CTkFrame(img_frame, fg_color="transparent")
        self._webcam_frame.grid(row=2, column=0, sticky="nsew", padx=14, pady=(10, 4))
        self._webcam_preview = ctk.CTkLabel(self._webcam_frame, text="")
        self._webcam_preview.pack()
        self._capture_info = ctk.CTkLabel(
            self._webcam_frame, text="",
            font=ctk.CTkFont(size=11),
            text_color=settings.TEXT_SECONDARY
        )
        self._capture_info.pack(pady=4)
        self._capture_btn = ctk.CTkButton(
            self._webcam_frame, text="📸 Capture Image",
            fg_color=settings.SUCCESS_COLOR, hover_color="#00BB55",
            height=36, corner_radius=8, text_color="#000",
            command=self._capture_single
        )
        self._capture_btn.pack(pady=(0, 8))
        self._webcam_frame.grid_remove()

    def on_show(self):
        self._refresh_user_list()

    def on_hide(self):
        self._stop_webcam_capture()

    def _refresh_user_list(self):
        for w in self._user_list_frame.winfo_children():
            w.destroy()

        users = self.app.db.get_all_users()
        if not users:
            ctk.CTkLabel(
                self._user_list_frame,
                text="No users yet.\nClick '+ Add New User' to begin.",
                font=ctk.CTkFont(size=12),
                text_color=settings.TEXT_SECONDARY,
                justify="center"
            ).pack(pady=20)
            return

        for user in users:
            self._make_user_row(user)

    def _make_user_row(self, user: dict):
        name = user["name"]
        row = ctk.CTkFrame(
            self._user_list_frame,
            fg_color=settings.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color="#2A2A3E"
        )
        row.pack(fill="x", padx=4, pady=4)
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row, text="👤", font=ctk.CTkFont(size=20)).grid(
            row=0, column=0, padx=(10, 8), pady=10
        )
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(
            info, text=name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=settings.TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w")
        img_count = count_user_images(
            os.path.join(settings.DATASET_DIR, name)
        )
        song_info = "♪ " + os.path.basename(user["song_path"]) if user.get("song_path") else "No song"
        ctk.CTkLabel(
            info, text=f"{img_count} images · {song_info}",
            font=ctk.CTkFont(size=11),
            text_color=settings.TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w")

        select_btn = ctk.CTkButton(
            row, text="Manage",
            fg_color=settings.ACCENT_COLOR, hover_color="#6A50E0",
            height=28, corner_radius=6, width=70,
            command=lambda n=name: self._select_user(n)
        )
        select_btn.grid(row=0, column=2, padx=10)

    def _select_user(self, name: str):
        self._selected_user = name
        user = self.app.db.get_user(name)
        if not user:
            return

        self._detail_placeholder.place_forget()
        self._detail_container.pack(fill="both", expand=True)

        self._detail_name.configure(text=name)
        img_count = count_user_images(os.path.join(settings.DATASET_DIR, name))
        self._img_count_label.configure(text=f"{img_count} training images")

        if user.get("song_path"):
            self._song_label.configure(
                text=os.path.basename(user["song_path"]),
                text_color=settings.SUCCESS_COLOR
            )
        else:
            self._song_label.configure(text="No song assigned", text_color=settings.TEXT_SECONDARY)

    def _browse_song(self):
        if not self._selected_user:
            return
        path = filedialog.askopenfilename(
            title="Select Song",
            filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")]
        )
        if path:
            self.app.db.update_user_song(self._selected_user, path)
            self._song_label.configure(
                text=os.path.basename(path), text_color=settings.SUCCESS_COLOR
            )
            self._refresh_user_list()

    def _upload_images(self):
        if not self._selected_user:
            return
        paths = filedialog.askopenfilenames(
            title="Select Face Images",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if not paths:
            return

        user_dir = os.path.join(settings.DATASET_DIR, self._selected_user)
        os.makedirs(user_dir, exist_ok=True)
        existing = count_user_images(user_dir)
        accepted = 0
        rejected = 0

        for path in paths:
            face = detect_and_crop_face(path)
            if face is not None:
                save_face_image(face, user_dir, existing + accepted)
                accepted += 1
            else:
                rejected += 1

        msg = f"Imported {accepted} images."
        if rejected:
            msg += f"\n{rejected} images rejected (no face detected)."
        messagebox.showinfo("Upload Complete", msg)
        self._select_user(self._selected_user)
        self._refresh_user_list()

    def _toggle_webcam_capture(self):
        if self._capture_running:
            self._stop_webcam_capture()
        else:
            self._start_webcam_capture()

    def _start_webcam_capture(self):
        if not self._selected_user:
            return
        if not self.app.camera.open():
            messagebox.showerror("Camera Error", "Could not open camera.")
            return
        self._capture_running = True
        self._capture_count = count_user_images(
            os.path.join(settings.DATASET_DIR, self._selected_user)
        )
        self._webcam_frame.grid()
        self._webcam_btn.configure(text="⏹ Stop Webcam", fg_color=settings.ERROR_COLOR)
        threading.Thread(target=self._webcam_preview_loop, daemon=True).start()

    def _stop_webcam_capture(self):
        self._capture_running = False
        self.app.camera.close()
        self._webcam_frame.grid_remove()
        if hasattr(self, '_webcam_btn'):
            self._webcam_btn.configure(
                text="📷 Capture from Webcam",
                fg_color=settings.BG_SURFACE
            )

    def _webcam_preview_loop(self):
        import face_recognition as fr
        while self._capture_running:
            frame = self.app.camera.read()
            if frame is None:
                time.sleep(0.05)
                continue
            import cv2 as cv
            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            small = cv.resize(rgb, (0, 0), fx=0.5, fy=0.5)
            locs = fr.face_locations(small, model="hog")
            for t, r, b, l in locs:
                cv.rectangle(frame, (l*2, t*2), (r*2, b*2), (123, 97, 255), 2)

            pil = frame_to_pil(frame)
            ctk_img = pil_to_ctk_image(pil, (340, 255))
            self.after(0, lambda img=ctk_img: self._webcam_preview.configure(image=img))
            count = count_user_images(os.path.join(settings.DATASET_DIR, self._selected_user))
            self.after(0, lambda c=count: self._capture_info.configure(
                text=f"{c} images captured", text_color=settings.TEXT_SECONDARY
            ))
            time.sleep(0.05)

    def _capture_single(self):
        if not self._selected_user or not self._capture_running:
            return
        frame = self.app.camera.capture_single()
        if frame is None:
            return
        face = detect_and_crop_face(frame)
        if face is not None:
            user_dir = os.path.join(settings.DATASET_DIR, self._selected_user)
            count = count_user_images(user_dir)
            save_face_image(face, user_dir, count)
            self._refresh_user_list()
        else:
            self.after(0, lambda: self._capture_info.configure(
                text="No face detected — try again", text_color=settings.WARNING_COLOR
            ))

    def _delete_selected_user(self):
        if not self._selected_user:
            return
        if messagebox.askyesno(
            "Confirm Delete",
            f"Delete user '{self._selected_user}' and all their data?"
        ):
            user_dir = os.path.join(settings.DATASET_DIR, self._selected_user)
            if os.path.isdir(user_dir):
                shutil.rmtree(user_dir)
            self.app.db.delete_user(self._selected_user)
            self._selected_user = None
            self._detail_container.pack_forget()
            self._detail_placeholder.place(relx=0.5, rely=0.5, anchor="center")
            self._refresh_user_list()

    def _show_add_user_dialog(self):
        dialog = ctk.CTkInputDialog(
            text="Enter new user name:",
            title="Add User"
        )
        name = dialog.get_input()
        if name:
            name = name.strip()
            if not name:
                return
            if self.app.db.user_exists(name):
                messagebox.showerror("Error", f"User '{name}' already exists.")
                return
            self.app.db.add_user(name)
            os.makedirs(os.path.join(settings.DATASET_DIR, name), exist_ok=True)
            self._refresh_user_list()
            self._select_user(name)
