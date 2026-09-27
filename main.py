import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

DB_NAME = "notes.db"

KV = r"""
#:import dp kivy.metrics.dp

<NoteItem@BoxLayout>:
    orientation: "vertical"
    size_hint_y: None
    height: dp(86)
    padding: dp(12)
    spacing: dp(3)
    canvas.before:
        Color:
            rgba: app.card_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10),]
    Label:
        text: root.title_text
        color: app.text_color
        font_size: "17sp"
        bold: True
        halign: "right"
        valign: "middle"
        text_size: self.width, None
        shorten: True
        shorten_from: "left"
    Label:
        text: root.date_text
        color: app.secondary_text_color
        font_size: "12sp"
        halign: "right"
        text_size: self.width, None

<MainScreen>:
    name: "main"
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: app.background_color
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(8)
            Label:
                text: "یادداشت‌های من"
                color: app.text_color
                font_size: "23sp"
                bold: True
                halign: "right"
                valign: "middle"
                text_size: self.size
            Button:
                text: "☾" if not app.dark_mode else "☀"
                size_hint_x: None
                width: dp(48)
                on_release: app.toggle_theme()

        TextInput:
            id: search
            size_hint_y: None
            height: dp(48)
            hint_text: "جست‌وجوی یادداشت..."
            multiline: False
            halign: "right"
            font_size: "16sp"
            padding: dp(12), dp(12)
            on_text: root.refresh(self.text)

        ScrollView:
            do_scroll_x: False
            GridLayout:
                id: notes_box
                cols: 1
                spacing: dp(8)
                padding: 0, dp(4)
                size_hint_y: None
                height: self.minimum_height

        Button:
            text: "＋  یادداشت جدید"
            size_hint_y: None
            height: dp(52)
            font_size: "17sp"
            on_release: root.new_note()

<EditScreen>:
    name: "edit"
    BoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: app.background_color
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(8)
            Button:
                text: "‹ بازگشت"
                size_hint_x: None
                width: dp(95)
                on_release: root.back()
            Label:
                text: "ویرایش یادداشت" if root.editing else "یادداشت جدید"
                color: app.text_color
                font_size: "20sp"
                bold: True
                halign: "right"
                text_size: self.size

        TextInput:
            id: title
            hint_text: "عنوان"
            multiline: False
            halign: "right"
            size_hint_y: None
            height: dp(52)
            font_size: "18sp"
            padding: dp(12), dp(12)

        TextInput:
            id: body
            hint_text: "متن یادداشت را بنویسید..."
            halign: "right"
            valign: "top"
            font_size: "16sp"
            padding: dp(12), dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(52)
            spacing: dp(8)
            Button:
                text: "ذخیره"
                on_release: root.save_note()
            Button:
                text: "حذف" if root.editing else "انصراف"
                on_release: root.delete_or_cancel()

"""

class DB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def all(self, query=""):
        if query.strip():
            q = f"%{query.strip()}%"
            return self.conn.execute(
                "SELECT id,title,body,updated_at FROM notes "
                "WHERE title LIKE ? OR body LIKE ? ORDER BY id DESC", (q, q)
            ).fetchall()
        return self.conn.execute(
            "SELECT id,title,body,updated_at FROM notes ORDER BY id DESC"
        ).fetchall()

    def get(self, note_id):
        return self.conn.execute(
            "SELECT id,title,body,updated_at FROM notes WHERE id=?", (note_id,)
        ).fetchone()

    def insert(self, title, body):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.conn.execute(
            "INSERT INTO notes(title,body,updated_at) VALUES(?,?,?)",
            (title, body, now)
        )
        self.conn.commit()

    def update(self, note_id, title, body):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.conn.execute(
            "UPDATE notes SET title=?, body=?, updated_at=? WHERE id=?",
            (title, body, now, note_id)
        )
        self.conn.commit()

    def delete(self, note_id):
        self.conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
        self.conn.commit()

class MainScreen(Screen):
    def on_pre_enter(self):
        self.refresh()

    def refresh(self, query=""):
        box = self.ids.notes_box
        box.clear_widgets()
        rows = App.get_running_app().db.all(query)
        for note_id, title, body, updated in rows:
            from kivy.uix.button import Button
            btn = Button(
                text=f"{title or 'بدون عنوان'}\n{updated}",
                size_hint_y=None,
                height=86,
                halign="right",
                valign="middle",
                text_size=(0, None),
                font_size="16sp",
            )
            btn.bind(on_release=lambda b, nid=note_id: self.open_note(nid))
            box.add_widget(btn)

    def new_note(self):
        edit = self.manager.get_screen("edit")
        edit.load_note(None)
        self.manager.current = "edit"

    def open_note(self, note_id):
        edit = self.manager.get_screen("edit")
        edit.load_note(note_id)
        self.manager.current = "edit"

class EditScreen(Screen):
    note_id = NumericProperty(0)
    editing = BooleanProperty(False)

    def load_note(self, note_id):
        self.note_id = note_id or 0
        self.editing = bool(note_id)
        if note_id:
            row = App.get_running_app().db.get(note_id)
            if row:
                self.ids.title.text = row[1]
                self.ids.body.text = row[2]
        else:
            self.ids.title.text = ""
            self.ids.body.text = ""

    def save_note(self):
        title = self.ids.title.text.strip()
        body = self.ids.body.text.strip()
        if not title and not body:
            self.back()
            return
        db = App.get_running_app().db
        if self.editing:
            db.update(self.note_id, title or "بدون عنوان", body)
        else:
            db.insert(title or "بدون عنوان", body)
        self.back()

    def delete_or_cancel(self):
        if self.editing:
            App.get_running_app().db.delete(self.note_id)
        self.back()

    def back(self):
        self.manager.current = "main"

class NotesApp(App):
    dark_mode = BooleanProperty(False)

    @property
    def background_color(self):
        return (0.07, 0.08, 0.10, 1) if self.dark_mode else (0.96, 0.96, 0.97, 1)

    @property
    def card_color(self):
        return (0.13, 0.14, 0.17, 1) if self.dark_mode else (1, 1, 1, 1)

    @property
    def text_color(self):
        return (0.95, 0.95, 0.97, 1) if self.dark_mode else (0.10, 0.10, 0.12, 1)

    @property
    def secondary_text_color(self):
        return (0.65, 0.66, 0.70, 1) if self.dark_mode else (0.40, 0.40, 0.45, 1)

    def build(self):
        self.title = "یادداشت‌های من"
        self.db = DB()
        Window.softinput_mode = "below_target"
        Builder.load_string(KV)
        return ScreenManagerRoot()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.root.get_screen("main").refresh(self.root.get_screen("main").ids.search.text)

class ScreenManagerRoot(__import__("kivy.uix.screenmanager", fromlist=["ScreenManager"]).ScreenManager):
    pass

if __name__ == "__main__":
    NotesApp().run()
