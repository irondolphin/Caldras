#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import pickle, os, base64, hashlib, markdown, subprocess, tempfile
from cryptography.fernet import Fernet
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    HTML = None
    WEASYPRINT_AVAILABLE = False


font_console = ("Cascadia Code", 11)  # fallback: ("Courier New", 11)
NOTE_FILE = ".note.dat"

def get_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def encrypt_text(text, password):
    return Fernet(get_key(password)).encrypt(text.encode())

def generate_pdf(content_md, filename):
        try:
            html_body = markdown.markdown(content_md)
            style = """
            <style>
            @page { size: A4; margin: 2cm; }
            body {
            font-family: 'Segoe UI', 'Arial', sans-serif;
                padding: 2em;
                color: #1c1c23;
            }
            h1, h2 { color: #6fc3df; }
            </style>
        """

            full_html = f"""
            <html>
              <head>
                <meta charset="utf-8">
                {style}
              </head>
              <body>{html_body}</body>
            </html>
        """

            if WEASYPRINT_AVAILABLE:
                HTML(string=full_html).write_pdf(filename)
                return True, "WeasyPrint"
            else:
                with tempfile.NamedTemporaryFile('w', delete=False, suffix=".html", encoding='utf-8') as fhtml:
                    fhtml.write(full_html)
                    html_path = fhtml.name

                result = subprocess.run(["wkhtmltopdf", html_path, filename], capture_output=True)
                if result.returncode == 0:
                    return True, "wkhtmltopdf"
                else:
                    return False, result.stderr.decode()
        except Exception as e:
            return False, str(e)

def decrypt_text(ciphertext, password):
    return Fernet(get_key(password)).decrypt(ciphertext).decode()

def load_notes():
    if os.path.exists(NOTE_FILE):
        with open(NOTE_FILE, "rb") as f:
            try: return pickle.load(f)
            except: return []
    return []

def save_notes(notes):
    with open(NOTE_FILE, "wb") as f:
        pickle.dump(notes, f)
def splash():
    splash_root = tk.Tk()
    splash_root.overrideredirect(True)
    splash_root.geometry("400x200+500+300")
    splash_root.configure(bg="#0f0f13")
    label = tk.Label(splash_root, text="🚀 Avvio Archivio Caldras...", font=("Segoe UI", 14),
                     fg="#6fc3df", bg="#0f0f13")
    label.pack(expand=True)
    splash_root.after(1500, splash_root.destroy)
    splash_root.mainloop()

class CaldrasApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Console Caldras — Archivio Orbitale")
        self.geometry("1000x600")
        self.minsize(800, 480)

        self.theme = "dark"
        self.notes = load_notes()
        self.current_index = None

        self.setup_ui()
        self.apply_theme()
        self.refresh_list()
    def setup_ui(self):
        pane_main = tk.Frame(self, bg="#0f0f13")
        pane_main.pack(fill=tk.BOTH, expand=True)

        # 🔍 Barra di ricerca
        search_frame = tk.Frame(pane_main, bg="#0f0f13")
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 0))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=font_console, bg="#1c1c23", fg="#c3c7d1",
                                insertbackground="#6fc3df", relief=tk.FLAT, borderwidth=0)
        search_entry.pack(fill=tk.X, padx=2)
        self.search_var.trace("w", lambda *args: self.refresh_list())

        # 📋 Lista delle note
        self.note_list = tk.Listbox(pane_main, width=30, font=font_console,
                                    bg="#1c1c23", fg="#c3c7d1", selectbackground="#6fc3df",
                                    selectforeground="#0f0f13", relief=tk.FLAT, borderwidth=0)
        self.note_list.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.note_list.bind("<<ListboxSelect>>", self.on_select)

        # ✍️ Editor + Preview
        right = tk.Frame(pane_main, bg="#0f0f13")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        pane_editor = tk.PanedWindow(right, orient=tk.HORIZONTAL, bg="#0f0f13")
        pane_editor.pack(fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(pane_editor, wrap=tk.WORD, font=font_console,
                                 bg="#1c1c23", fg="#c3c7d1", insertbackground="#6fc3df",
                                 relief=tk.FLAT, borderwidth=0)
        pane_editor.add(self.text_area)

        self.preview = tk.Text(pane_editor, wrap=tk.WORD, state=tk.DISABLED,
                               font=font_console, bg="#1c1c23", fg="#c3c7d1",
                               relief=tk.FLAT, borderwidth=0)
        pane_editor.add(self.preview)

        # 🔘 Pulsanti stile flat orbitale
        self.bottom = tk.Frame(self, height=50, bg="#0f0f13")
        self.bottom.pack(side=tk.BOTTOM, fill=tk.X)

        self.buttons = [
            tk.Button(self.bottom, text="📝 Nuova", command=self.new_note),
            tk.Button(self.bottom, text="💾 Salva", command=self.save_current),
            tk.Button(self.bottom, text="❌ Elimina", command=self.delete_note),
            tk.Button(self.bottom, text="🔐 Password", command=self.set_password),
            tk.Button(self.bottom, text="📤 PDF", command=self.export_to_pdf),
            tk.Button(self.bottom, text="🌗 Tema", command=self.toggle_theme)
        ]
        for btn in self.buttons:
            btn.pack(side=tk.LEFT, padx=6, pady=8)
    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()
        self.update_preview()

    def apply_theme(self):
        if self.theme == "dark":
            bg, fg, edt = "#0f0f13", "#c3c7d1", "#1c1c23"
            accent = "#6fc3df"
        else:
            bg, fg, edt = "#fdfdfd", "#2e2e2e", "#ffffff"
            accent = "#89b4fa"

        self.configure(bg=bg)
        self.note_list.configure(bg=edt, fg=fg, selectbackground=accent, selectforeground=bg,
                                 font=font_console, relief=tk.FLAT, borderwidth=0)
        self.text_area.configure(bg=edt, fg=fg, insertbackground=accent,
                                 font=font_console, relief=tk.FLAT, borderwidth=0)
        self.preview.configure(bg=edt, fg=fg, state=tk.DISABLED,
                               font=font_console, relief=tk.FLAT, borderwidth=0)
        self.bottom.configure(bg=bg)

        for btn in self.buttons:
            btn.configure(
                bg=edt, fg=fg,
                activebackground=accent,
                activeforeground=bg,
                relief=tk.FLAT,
                borderwidth=0,
                font=font_console
            )

    def update_preview(self, event=None):
        md = self.text_area.get("1.0", tk.END)
        html = markdown.markdown(md)
        clean = self.clean_html(html)
        self.preview.configure(state=tk.NORMAL)
        self.preview.delete("1.0", tk.END)
        self.preview.insert(tk.END, clean)
        self.preview.configure(state=tk.DISABLED)

    def clean_html(self, html):
        import re
        return re.sub(r"<[^>]+>", "", html)
    
    def export_to_pdf(self):
        if self.current_index is None:
            messagebox.showinfo("Nessuna nota", "Seleziona una nota da esportare.")
            return

        titolo = self.notes[self.current_index][0]
        content = self.text_area.get("1.0", tk.END)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Esporta PDF",
            initialfile=f"{titolo}.pdf"
        )

        if file_path:
            success, engine = generate_pdf(content, file_path)
            if success:
                messagebox.showinfo("✅ Esportato", f"PDF salvato con {engine}:\n{file_path}")
            else:
                messagebox.showerror("Errore PDF", f"Errore durante l'esportazione:\n{engine}")

    def refresh_list(self):
        self.note_list.delete(0, tk.END)
        keyword = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        for note in self.notes:
            title = note[0] if len(note) >= 1 else "Senza titolo"
            if keyword in title.lower():
                self.note_list.insert(tk.END, title)

    def new_note(self):
        titolo = simpledialog.askstring("Nuova Nota", "Titolo:", parent=self)
        if titolo:
            self.notes.append((titolo, "", None))
            save_notes(self.notes)
            self.refresh_list()

    def on_select(self, event):
        sel = self.note_list.curselection()
        if not sel: return
        i = sel[0]
        matches = [note for note in self.notes if self.search_var.get().lower() in note[0].lower()]
        if i >= len(matches): return
        self.current_index = self.notes.index(matches[i])
        titolo, contenuto, password = self.notes[self.current_index] if len(self.notes[self.current_index]) == 3 else (*self.notes[self.current_index], None)
        if password:
            pw = simpledialog.askstring("🔐 Password richiesta", f"Inserisci password per '{titolo}':", show='*')
            if pw != password:
                messagebox.showerror("Errore", "Password errata.")
                self.text_area.delete("1.0", tk.END)
                self.preview.configure(state=tk.NORMAL)
                self.preview.delete("1.0", tk.END)
                self.preview.configure(state=tk.DISABLED)
                return
            try: contenuto = decrypt_text(contenuto, password)
            except: contenuto = ""
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, contenuto)
        self.update_preview()

    def save_current(self):
        if self.current_index is None: return
        titolo, _, password = self.notes[self.current_index] if len(self.notes[self.current_index]) == 3 else (*self.notes[self.current_index], None)
        new_content = self.text_area.get("1.0", tk.END).strip()
        if password:
            try: new_content = encrypt_text(new_content, password)
            except:
                messagebox.showerror("Errore", "Errore nella cifratura.")
                return
        self.notes[self.current_index] = (titolo, new_content, password)
        save_notes(self.notes)
        messagebox.showinfo("Salvata", f"La nota '{titolo}' è stata salvata.")

    def delete_note(self):
        if self.current_index is not None:
            titolo = self.notes[self.current_index][0]
            if messagebox.askyesno("Eliminare", f"Eliminare '{titolo}'?"):
                del self.notes[self.current_index]
                save_notes(self.notes)
                self.text_area.delete("1.0", tk.END)
                self.preview.configure(state=tk.NORMAL)
                self.preview.delete("1.0", tk.END)
                self.preview.configure(state=tk.DISABLED)
                self.refresh_list()
                self.current_index = None

    def set_password(self):
        if self.current_index is None: return
        pw = simpledialog.askstring("🔐 Password", "Nuova password (vuoto per rimuovere):", show='*', parent=self)
        titolo, contenuto, old_pw = self.notes[self.current_index] if len(self.notes[self.current_index]) == 3 else (*self.notes[self.current_index], None)
        if old_pw:
            try: contenuto = decrypt_text(contenuto, old_pw)
            except:
                messagebox.showerror("Errore", "Password errata.")
                return
        if pw:
            contenuto = encrypt_text(contenuto, pw)
            self.notes[self.current_index] = (titolo, contenuto, pw)
        else:
            self.notes[self.current_index] = (titolo, contenuto, None)
        save_notes(self.notes)
        messagebox.showinfo("🔒 Password", f"La password per '{titolo}' è stata aggiornata.")

if __name__ == "__main__":
    splash()
    CaldrasApp().mainloop()
