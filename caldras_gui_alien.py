#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import pickle, os, base64, hashlib, markdown, json, tempfile, subprocess
from cryptography.fernet import Fernet

# 🛰️ Supporto PDF automatico
try:
    from weasyprint import HTML
    PDF_ENGINE = "weasyprint"
except ImportError:
    PDF_ENGINE = "wkhtmltopdf"

CONFIG_FILE = ".caldras.conf"
NOTE_FILE = ".note.dat"
FONT_CONSOLE = ("Cascadia Code", 11)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"theme": "alien-dark"}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def get_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def encrypt_text(text, password):
    return Fernet(get_key(password)).encrypt(text.encode())

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

def generate_pdf(content_md, filename):
    html_body = markdown.markdown(content_md)
    style = """
    <meta charset="utf-8">
    <style>
    body { font-family: 'Segoe UI', 'Arial', sans-serif; padding:2em; color:#1c1c23; }
    h1, h2 { color:#6fc3df; }
    </style>
    """
    full_html = f"<html><head>{style}</head><body>{html_body}</body></html>"
    try:
        if PDF_ENGINE == "weasyprint" and HTML:
            HTML(string=full_html).write_pdf(filename)
            return True, "WeasyPrint"
        else:
            with tempfile.NamedTemporaryFile('w', delete=False, suffix=".html", encoding='utf-8') as fhtml:
                fhtml.write(full_html)
                html_path = fhtml.name
            result = subprocess.run(["wkhtmltopdf", html_path, filename], capture_output=True)
            return (result.returncode == 0), "wkhtmltopdf"
    except Exception as e:
        return False, str(e)

def splash():
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry("440x220+500+320")
    root.configure(bg="#0e0f12")
    label = tk.Label(root, text="🛸 Avvio Stazione Aliena Caldras...", font=("Segoe UI", 14),
                     fg="#76f6ff", bg="#0e0f12")
    label.pack(expand=True)
    dots = tk.Label(root, text="Caricamento", font=("Consolas", 10), fg="#b9e3ff", bg="#0e0f12")
    dots.pack()
    def animate(i=[0]):
        dots.config(text="Caricamento" + "." * (i[0] % 4))
        i[0] += 1
        if i[0] < 10:
            root.after(300, animate)
        else:
            root.destroy()
    animate()
    root.mainloop()
class CaldrasApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 Stazione Orbitale Caldras")
        self.geometry("1000x600")
        self.minsize(800, 480)

        self.config = load_config()
        self.theme = self.config.get("theme", "alien-dark")
        self.notes = load_notes()
        self.current_index = None

        self.setup_ui()
        self.apply_theme()
        self.refresh_list()

    def setup_ui(self):
        pane_main = tk.Frame(self, bg="#0e0f12")
        pane_main.pack(fill=tk.BOTH, expand=True)

        search_frame = tk.Frame(pane_main, bg="#0e0f12")
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 0))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=FONT_CONSOLE, bg="#16232f", fg="#c6f6ff",
                                insertbackground="#76f6ff", relief=tk.FLAT)
        search_entry.pack(fill=tk.X, padx=2)
        self.search_var.trace("w", lambda *args: self.refresh_list())

        self.note_list = tk.Listbox(pane_main, width=30, font=FONT_CONSOLE,
                                    bg="#16232f", fg="#c6f6ff", selectbackground="#76f6ff",
                                    selectforeground="#0e0f12", relief=tk.FLAT)
        self.note_list.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.note_list.bind("<<ListboxSelect>>", self.on_select)

        right = tk.Frame(pane_main, bg="#0e0f12")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        pane_editor = tk.PanedWindow(right, orient=tk.HORIZONTAL, bg="#0e0f12")
        pane_editor.pack(fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(pane_editor, wrap=tk.WORD, font=FONT_CONSOLE,
                                 bg="#16232f", fg="#c6f6ff", insertbackground="#76f6ff",
                                 relief=tk.FLAT)
        pane_editor.add(self.text_area)

        self.preview = tk.Text(pane_editor, wrap=tk.WORD, state=tk.DISABLED,
                               font=FONT_CONSOLE, bg="#16232f", fg="#c6f6ff",
                               relief=tk.FLAT)
        pane_editor.add(self.preview)

        self.bottom = tk.Frame(self, height=50, bg="#0e0f12")
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
            btn.bind("<Enter>", self.on_hover)
            btn.bind("<Leave>", self.on_leave)
    def toggle_theme(self):
        self.theme = "alien-light" if self.theme == "alien-dark" else "alien-dark"
        self.config["theme"] = self.theme
        save_config(self.config)
        self.apply_theme()
        self.update_preview()

    def apply_theme(self):
        if self.theme == "alien-dark":
            bg, fg, edt = "#0e0f12", "#c6f6ff", "#16232f"
            accent = "#76f6ff"
        else:
            bg, fg, edt = "#f8f9fc", "#28323a", "#ffffff"
            accent = "#37a3c6"

        self.configure(bg=bg)
        self.note_list.configure(bg=edt, fg=fg, selectbackground=accent, selectforeground=bg)
        self.text_area.configure(bg=edt, fg=fg, insertbackground=accent)
        self.preview.configure(bg=edt, fg=fg, state=tk.DISABLED)
        self.bottom.configure(bg=bg)

        for btn in self.buttons:
            btn.configure(bg=edt, fg=fg,
                          activebackground=accent,
                          activeforeground=bg,
                          relief=tk.FLAT,
                          borderwidth=0,
                          font=FONT_CONSOLE)

    def on_hover(self, event):
        event.widget.configure(bg="#76f6ff", fg="#0e0f12")

    def on_leave(self, event):
        fg = "#c6f6ff" if self.theme == "alien-dark" else "#28323a"
        bg = "#16232f" if self.theme == "alien-dark" else "#ffffff"
        event.widget.configure(bg=bg, fg=fg)

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
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                            filetypes=[("PDF files", "*.pdf")],
                            title="Esporta PDF",
                            initialfile=f"{titolo}.pdf")
        if file_path:
            success, engine = generate_pdf(content, file_path)
            if success:
                messagebox.showinfo("✅ PDF Esportato", f"PDF salvato con {engine}:\n{file_path}")
            else:
                messagebox.showerror("Errore PDF", f"Errore durante l'esportazione:\n{engine}")
    def refresh_list(self):
        self.note_list.delete(0, tk.END)
        keyword = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        for note in self.notes:
            title = note[0] if len(note) >= 1 else "Senza titolo"
            if keyword in title.lower():
                label = title + (" 🔒" if len(note) == 3 and note[2] else "")
                self.note_list.insert(tk.END, label)

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