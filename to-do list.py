import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime

# ── Palette ────────────────────────────────────────────────────────────────
BG          = "#1C1C2E"   # deep navy
SURFACE     = "#252540"   # card surface
SURFACE2    = "#2E2E50"   # slightly lighter panel
ACCENT      = "#7C6AF7"   # violet accent
ACCENT_LITE = "#A99EF9"   # soft violet hover
GREEN       = "#4ECDC4"   # mint-green for "done"
DANGER      = "#FF6B6B"   # coral red for delete
TEXT        = "#E8E6FF"   # near-white text
MUTED       = "#8886AA"   # muted secondary text
BORDER      = "#3A3A60"   # subtle border

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_LABEL  = ("Segoe UI", 11)
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 9)

DATA_FILE = os.path.join(os.path.dirname(__file__), "todo_data.json")

CATEGORIES = ["All", "Personal", "Work", "Shopping", "Health", "Other"]
PRIORITIES  = ["Low", "Medium", "High"]


# ── Data helpers ────────────────────────────────────────────────────────────
def load_tasks():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


# ── Rounded button helper ───────────────────────────────────────────────────
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None,
                 bg=ACCENT, fg=TEXT, hover=ACCENT_LITE,
                 width=120, height=34, radius=8, font=FONT_BODY, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"] if "bg" in parent.keys() else BG,
                         highlightthickness=0, **kw)
        self._bg, self._hover, self._fg = bg, hover, fg
        self._cmd = command
        self._r = radius
        self._text = text
        self._font = font
        self._draw(bg)
        self.bind("<Enter>",    lambda e: self._draw(hover))
        self.bind("<Leave>",    lambda e: self._draw(bg))
        self.bind("<Button-1>", lambda e: command() if command else None)

    def _draw(self, color):
        self.delete("all")
        w, h, r = self.winfo_reqwidth(), self.winfo_reqheight(), self._r
        self.create_arc(0,     0,     r*2,   r*2,   start=90,  extent=90,  fill=color, outline=color)
        self.create_arc(w-r*2, 0,     w,     r*2,   start=0,   extent=90,  fill=color, outline=color)
        self.create_arc(0,     h-r*2, r*2,   h,     start=180, extent=90,  fill=color, outline=color)
        self.create_arc(w-r*2, h-r*2, w,     h,     start=270, extent=90,  fill=color, outline=color)
        self.create_rectangle(r, 0, w-r, h,   fill=color, outline=color)
        self.create_rectangle(0, r, w,   h-r, fill=color, outline=color)
        self.create_text(w//2, h//2, text=self._text, fill=self._fg,
                         font=self._font, anchor="center")


# ── Main application ────────────────────────────────────────────────────────
class ToDoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Do it. — Task Manager")
        self.geometry("900x650")
        self.minsize(780, 540)
        self.configure(bg=BG)
        self.resizable(True, True)

        self.tasks          = load_tasks()
        self.filter_cat     = tk.StringVar(value="All")
        self.filter_pri     = tk.StringVar(value="All")
        self.filter_done    = tk.StringVar(value="All")
        self.search_var     = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())

        self._build_ui()
        self.refresh()

    # ── UI skeleton ─────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header
        hdr = tk.Frame(self, bg=SURFACE, pady=0)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Do it.", font=("Segoe UI", 20, "bold"),
                 bg=SURFACE, fg=ACCENT).pack(side="left", padx=22, pady=14)
        tk.Label(hdr, text="your personal task companion",
                 font=FONT_SMALL, bg=SURFACE, fg=MUTED).pack(side="left", pady=14)

        self.stats_label = tk.Label(hdr, text="", font=FONT_SMALL,
                                    bg=SURFACE, fg=MUTED)
        self.stats_label.pack(side="right", padx=22)

        # ── Body: sidebar + main
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_sidebar(body)
        self._build_main(body)

    # ── Sidebar ──────────────────────────────────────────────────────────────
    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=SURFACE2, width=190)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Search
        tk.Label(sb, text="Search", font=FONT_SMALL,
                 bg=SURFACE2, fg=MUTED).pack(anchor="w", padx=16, pady=(18, 4))
        search_frame = tk.Frame(sb, bg=BORDER, pady=1)
        search_frame.pack(fill="x", padx=12)
        tk.Entry(search_frame, textvariable=self.search_var,
                 bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=FONT_BODY,
                 highlightthickness=0).pack(fill="x", padx=6, pady=6)

        # Category filter
        tk.Label(sb, text="Category", font=FONT_SMALL,
                 bg=SURFACE2, fg=MUTED).pack(anchor="w", padx=16, pady=(18, 4))
        for cat in CATEGORIES:
            self._sidebar_btn(sb, cat, self.filter_cat, "cat")

        # Priority filter
        tk.Label(sb, text="Priority", font=FONT_SMALL,
                 bg=SURFACE2, fg=MUTED).pack(anchor="w", padx=16, pady=(18, 4))
        for pri in ["All"] + PRIORITIES:
            self._sidebar_btn(sb, pri, self.filter_pri, "pri")

        # Status filter
        tk.Label(sb, text="Status", font=FONT_SMALL,
                 bg=SURFACE2, fg=MUTED).pack(anchor="w", padx=16, pady=(18, 4))
        for status in ["All", "Active", "Done"]:
            self._sidebar_btn(sb, status, self.filter_done, "done")

        # Clear completed
        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x", padx=12, pady=(20, 0))
        clr = tk.Label(sb, text="Clear completed", font=FONT_SMALL,
                        bg=SURFACE2, fg=DANGER, cursor="hand2")
        clr.pack(anchor="w", padx=16, pady=(12, 0))
        clr.bind("<Button-1>", lambda e: self.clear_completed())

    def _sidebar_btn(self, parent, text, var, kind):
        f = tk.Frame(parent, bg=SURFACE2, cursor="hand2")
        f.pack(fill="x", padx=8, pady=1)
        lbl = tk.Label(f, text=text, font=FONT_BODY,
                       bg=SURFACE2, fg=TEXT, anchor="w", padx=10, pady=5)
        lbl.pack(fill="x")
        def refresh_filter():
            var.set(text)
            self.refresh()
        f.bind("<Button-1>", lambda e: refresh_filter())
        lbl.bind("<Button-1>", lambda e: refresh_filter())
        f.bind("<Enter>", lambda e: [w.configure(bg=BORDER) for w in (f, lbl)])
        f.bind("<Leave>", lambda e: [w.configure(bg=SURFACE2) for w in (f, lbl)])
        lbl.bind("<Enter>", lambda e: [w.configure(bg=BORDER) for w in (f, lbl)])
        lbl.bind("<Leave>", lambda e: [w.configure(bg=SURFACE2) for w in (f, lbl)])

    # ── Main pane ─────────────────────────────────────────────────────────────
    def _build_main(self, parent):
        main = tk.Frame(parent, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        # Toolbar
        tb = tk.Frame(main, bg=BG, pady=10)
        tb.pack(fill="x", padx=20)
        RoundedButton(tb, "+ Add Task", command=self.open_add_dialog,
                      bg=ACCENT, hover=ACCENT_LITE, width=130, height=36).pack(side="left")
        RoundedButton(tb, "Sort by Date", command=lambda: self.sort_tasks("date"),
                      bg=SURFACE, hover=SURFACE2, width=110, height=36).pack(side="left", padx=(8, 0))
        RoundedButton(tb, "Sort by Priority", command=lambda: self.sort_tasks("priority"),
                      bg=SURFACE, hover=SURFACE2, width=130, height=36).pack(side="left", padx=(8, 0))

        # Task list (scrollable)
        canvas_frame = tk.Frame(main, bg=BG)
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.canvas = tk.Canvas(canvas_frame, bg=BG,
                                highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical",
                                  command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.list_frame = tk.Frame(self.canvas, bg=BG)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.list_frame, anchor="nw")

        self.list_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Empty state label
        self.empty_label = tk.Label(self.list_frame,
                                    text="Nothing here — add a task to get started.",
                                    font=FONT_LABEL, bg=BG, fg=MUTED)

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Refresh / filter ─────────────────────────────────────────────────────
    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        query  = self.search_var.get().lower()
        cat    = self.filter_cat.get()
        pri    = self.filter_pri.get()
        done   = self.filter_done.get()

        visible = []
        for t in self.tasks:
            if cat  != "All" and t.get("category", "Other") != cat:  continue
            if pri  != "All" and t.get("priority", "Medium") != pri: continue
            if done == "Active" and t.get("done"):                    continue
            if done == "Done"   and not t.get("done"):                continue
            if query and query not in t.get("title", "").lower() \
                     and query not in t.get("notes", "").lower():     continue
            visible.append(t)

        if not visible:
            self.empty_label = tk.Label(self.list_frame,
                                        text="Nothing matches — try a different filter.",
                                        font=FONT_LABEL, bg=BG, fg=MUTED)
            self.empty_label.pack(pady=60)
        else:
            for task in visible:
                self._task_card(self.list_frame, task)

        total  = len(self.tasks)
        done_n = sum(1 for t in self.tasks if t.get("done"))
        self.stats_label.configure(
            text=f"{done_n}/{total} completed")

    def _task_card(self, parent, task):
        pri_color = {"High": DANGER, "Medium": ACCENT, "Low": GREEN}.get(
            task.get("priority", "Medium"), ACCENT)
        is_done = task.get("done", False)

        card = tk.Frame(parent, bg=SURFACE, pady=0, cursor="arrow")
        card.pack(fill="x", pady=4)

        # Priority bar
        bar = tk.Frame(card, bg=pri_color, width=4)
        bar.pack(side="left", fill="y")

        inner = tk.Frame(card, bg=SURFACE, padx=12, pady=10)
        inner.pack(side="left", fill="both", expand=True)

        # Top row: checkbox + title + category chip
        top = tk.Frame(inner, bg=SURFACE)
        top.pack(fill="x")

        done_var = tk.BooleanVar(value=is_done)
        cb = tk.Checkbutton(top, variable=done_var,
                            command=lambda t=task, v=done_var: self.toggle_done(t, v),
                            bg=SURFACE, activebackground=SURFACE,
                            fg=GREEN, selectcolor=SURFACE,
                            highlightthickness=0, bd=0)
        cb.pack(side="left")

        title_style = ("Segoe UI", 11, "overstrike") if is_done else ("Segoe UI", 11, "bold")
        title_color = MUTED if is_done else TEXT
        tk.Label(top, text=task.get("title", "Untitled"),
                 font=title_style, bg=SURFACE, fg=title_color).pack(side="left", padx=(4, 0))

        # Category chip
        chip = tk.Label(top, text=task.get("category", "Other"),
                        font=FONT_MONO, bg=BORDER, fg=MUTED, padx=6, pady=2)
        chip.pack(side="left", padx=(10, 0))

        # Priority chip
        tk.Label(top, text=task.get("priority", "Medium"),
                 font=FONT_MONO, bg=pri_color, fg=BG, padx=6, pady=2).pack(side="left", padx=(6, 0))

        # Notes
        notes = task.get("notes", "").strip()
        if notes:
            tk.Label(inner, text=notes, font=FONT_SMALL,
                     bg=SURFACE, fg=MUTED, anchor="w",
                     wraplength=500, justify="left").pack(fill="x", pady=(4, 0))

        # Bottom row: date + action buttons
        bot = tk.Frame(inner, bg=SURFACE)
        bot.pack(fill="x", pady=(6, 0))

        due = task.get("due", "")
        if due:
            tk.Label(bot, text=f"Due: {due}", font=FONT_MONO,
                     bg=SURFACE, fg=MUTED).pack(side="left")

        created = task.get("created", "")
        if created:
            tk.Label(bot, text=f"  ·  Created {created}", font=FONT_MONO,
                     bg=SURFACE, fg=BORDER).pack(side="left")

        # Edit / Delete buttons
        for label, color, cmd in [
            ("Edit",   ACCENT_LITE, lambda t=task: self.open_edit_dialog(t)),
            ("Delete", DANGER,      lambda t=task: self.delete_task(t)),
        ]:
            btn = tk.Label(bot, text=label, font=FONT_SMALL,
                           bg=SURFACE, fg=color, cursor="hand2")
            btn.pack(side="right", padx=(8, 0))
            btn.bind("<Button-1>", lambda e, c=cmd: c())

    # ── Task CRUD ────────────────────────────────────────────────────────────
    def open_add_dialog(self):
        TaskDialog(self, title="New Task", on_save=self._add_task)

    def open_edit_dialog(self, task):
        TaskDialog(self, title="Edit Task", task=task,
                   on_save=lambda data: self._update_task(task, data))

    def _add_task(self, data):
        data["done"]    = False
        data["created"] = datetime.now().strftime("%d %b %Y")
        self.tasks.append(data)
        save_tasks(self.tasks)
        self.refresh()

    def _update_task(self, task, data):
        task.update(data)
        save_tasks(self.tasks)
        self.refresh()

    def toggle_done(self, task, var):
        task["done"] = var.get()
        save_tasks(self.tasks)
        self.refresh()

    def delete_task(self, task):
        if messagebox.askyesno("Delete Task",
                               f"Delete \"{task.get('title')}\"?",
                               parent=self):
            self.tasks.remove(task)
            save_tasks(self.tasks)
            self.refresh()

    def clear_completed(self):
        done_count = sum(1 for t in self.tasks if t.get("done"))
        if done_count == 0:
            messagebox.showinfo("Nothing to clear", "No completed tasks found.")
            return
        if messagebox.askyesno("Clear Completed",
                               f"Remove {done_count} completed task(s)?",
                               parent=self):
            self.tasks = [t for t in self.tasks if not t.get("done")]
            save_tasks(self.tasks)
            self.refresh()

    def sort_tasks(self, key):
        if key == "date":
            def parse(t):
                try:
                    return datetime.strptime(t.get("due", ""), "%Y-%m-%d")
                except Exception:
                    return datetime.max
            self.tasks.sort(key=parse)
        elif key == "priority":
            order = {"High": 0, "Medium": 1, "Low": 2}
            self.tasks.sort(key=lambda t: order.get(t.get("priority", "Medium"), 1))
        save_tasks(self.tasks)
        self.refresh()


# ── Task dialog (add / edit) ─────────────────────────────────────────────────
class TaskDialog(tk.Toplevel):
    def __init__(self, parent, title, on_save, task=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.geometry("480x460")
        self.resizable(False, False)
        self.grab_set()
        self._on_save = on_save
        self._task    = task or {}
        self._build()

    def _build(self):
        pad = dict(padx=24, pady=6)

        tk.Label(self, text="Title *", font=FONT_SMALL, bg=BG, fg=MUTED).pack(anchor="w", **pad)
        self.title_var = tk.StringVar(value=self._task.get("title", ""))
        entry = tk.Entry(self, textvariable=self.title_var, bg=SURFACE,
                         fg=TEXT, insertbackground=TEXT, relief="flat",
                         font=FONT_LABEL, highlightbackground=BORDER,
                         highlightthickness=1)
        entry.pack(fill="x", **pad)
        entry.focus()

        tk.Label(self, text="Notes", font=FONT_SMALL, bg=BG, fg=MUTED).pack(anchor="w", **pad)
        self.notes = tk.Text(self, height=4, bg=SURFACE, fg=TEXT,
                             insertbackground=TEXT, relief="flat",
                             font=FONT_BODY, wrap="word",
                             highlightbackground=BORDER, highlightthickness=1)
        self.notes.pack(fill="x", **pad)
        self.notes.insert("1.0", self._task.get("notes", ""))

        # Row: Category + Priority
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=24, pady=6)

        col1 = tk.Frame(row, bg=BG)
        col1.pack(side="left", fill="x", expand=True)
        tk.Label(col1, text="Category", font=FONT_SMALL,
                 bg=BG, fg=MUTED).pack(anchor="w")
        self.cat_var = tk.StringVar(value=self._task.get("category", "Personal"))
        ttk.Combobox(col1, textvariable=self.cat_var,
                     values=CATEGORIES[1:], state="readonly",
                     font=FONT_BODY).pack(fill="x")

        col2 = tk.Frame(row, bg=BG)
        col2.pack(side="right", fill="x", expand=True, padx=(12, 0))
        tk.Label(col2, text="Priority", font=FONT_SMALL,
                 bg=BG, fg=MUTED).pack(anchor="w")
        self.pri_var = tk.StringVar(value=self._task.get("priority", "Medium"))
        ttk.Combobox(col2, textvariable=self.pri_var,
                     values=PRIORITIES, state="readonly",
                     font=FONT_BODY).pack(fill="x")

        tk.Label(self, text="Due date (YYYY-MM-DD)", font=FONT_SMALL,
                 bg=BG, fg=MUTED).pack(anchor="w", **pad)
        self.due_var = tk.StringVar(value=self._task.get("due", ""))
        tk.Entry(self, textvariable=self.due_var, bg=SURFACE,
                 fg=TEXT, insertbackground=TEXT, relief="flat",
                 font=FONT_BODY, highlightbackground=BORDER,
                 highlightthickness=1).pack(fill="x", **pad)

        # Buttons
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=16)
        RoundedButton(btn_row, "Save Task", command=self._save,
                      bg=ACCENT, hover=ACCENT_LITE, width=120, height=36).pack(side="left")
        RoundedButton(btn_row, "Cancel", command=self.destroy,
                      bg=SURFACE, hover=SURFACE2, width=90, height=36).pack(side="left", padx=(10, 0))

    def _save(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Missing title", "Please enter a task title.", parent=self)
            return
        self._on_save({
            "title":    title,
            "notes":    self.notes.get("1.0", "end-1c").strip(),
            "category": self.c