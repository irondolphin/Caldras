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
        self.pane_main = tk.Frame(self, bg="#0e0f12")
        self.pane_main.pack(fill=tk.BOTH, expand=True)

        self.search_frame = tk.Frame(self.pane_main, bg="#0e0f12")
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 0))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var,
                                     font=FONT_CONSOLE, bg="#16232f", fg="#c6f6ff",
                                     insertbackground="#76f6ff", relief=tk.FLAT)
        self.search_entry.pack(fill=tk.X, padx=2)
        self.search_var.trace("w", lambda *args: self.refresh_list())

        self.note_list = tk.Listbox(self.pane_main, width=30, font=FONT_CONSOLE,
                                    bg="#16232f", fg="#c6f6ff", selectbackground="#76f6ff",
                                    selectforeground="#0e0f12", relief=tk.FLAT)
        self.note_list.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.note_list.bind("<<ListboxSelect>>", self.on_select)

        self.right_frame = tk.Frame(self.pane_main, bg="#0e0f12")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        pane_editor = tk.PanedWindow(self.right_frame, orient=tk.HORIZONTAL, bg="#0e0f12")
        pane_editor.pack(fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(pane_editor, wrap=tk.WORD, font=FONT_CONSOLE,
                                 bg="#16232f", fg="#c6f6ff", insertbackground="#76f6ff",
                                 relief=tk.FLAT)
        # Bind per aggiornamento automatico anteprima
        self.text_area.bind("<KeyRelease>", self.update_preview)
        self.text_area.bind("<ButtonRelease>", self.update_preview)
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

        # Finestra principale e frame
        self.configure(bg=bg)
        self.pane_main.configure(bg=bg)
        self.search_frame.configure(bg=bg)
        self.right_frame.configure(bg=bg)
        self.bottom.configure(bg=bg)
        
        # Barra di ricerca
        self.search_entry.configure(bg=edt, fg=fg, insertbackground=accent)
        
        # Lista note
        self.note_list.configure(bg=edt, fg=fg, selectbackground=accent, selectforeground=bg)
        
        # Area di testo e anteprima
        self.text_area.configure(bg=edt, fg=fg, insertbackground=accent)
        self.preview.configure(bg=edt, fg=fg, state=tk.DISABLED)

        # Pulsanti
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
        md_text = self.text_area.get("1.0", tk.END)
        self.preview.configure(state=tk.NORMAL)
        self.preview.delete("1.0", tk.END)
        
        # Configura i tag per la formattazione
        self.setup_preview_tags()
        
        # Renderizza il markdown con formattazione
        self.render_markdown_to_text(md_text)
        
        self.preview.configure(state=tk.DISABLED)

    def setup_preview_tags(self):
        """Configura i tag per la formattazione del testo nell'anteprima"""
        if self.theme == "alien-dark":
            fg_normal = "#c6f6ff"
            fg_header = "#76f6ff"
            fg_bold = "#ffffff"
            fg_italic = "#b9e3ff"
            fg_code = "#ffb347"
        else:
            fg_normal = "#28323a"
            fg_header = "#37a3c6"
            fg_bold = "#000000"
            fg_italic = "#555555"
            fg_code = "#d63384"
            
        # Header styles
        self.preview.tag_config("h1", foreground=fg_header, font=("Cascadia Code", 16, "bold"))
        self.preview.tag_config("h2", foreground=fg_header, font=("Cascadia Code", 14, "bold"))
        self.preview.tag_config("h3", foreground=fg_header, font=("Cascadia Code", 12, "bold"))
        
        # Text styles
        self.preview.tag_config("bold", foreground=fg_bold, font=("Cascadia Code", 11, "bold"))
        self.preview.tag_config("italic", foreground=fg_italic, font=("Cascadia Code", 11, "italic"))
        self.preview.tag_config("code", foreground=fg_code, font=("Consolas", 10), background="#2d2d2d" if self.theme == "alien-dark" else "#f5f5f5")
        self.preview.tag_config("blockquote", foreground=fg_italic, font=("Cascadia Code", 11, "italic"))
        
    def render_markdown_to_text(self, md_text):
        """Converte markdown in testo formattato per tkinter"""
        import re
        
        lines = md_text.split('\n')
        
        for line_num, line in enumerate(lines):
            # Headers
            if line.startswith('### '):
                self.preview.insert(tk.END, line[4:] + '\n', "h3")
            elif line.startswith('## '):
                self.preview.insert(tk.END, line[3:] + '\n', "h2")
            elif line.startswith('# '):
                self.preview.insert(tk.END, line[2:] + '\n', "h1")
            
            # Blockquotes
            elif line.startswith('> '):
                self.preview.insert(tk.END, "❯ " + line[2:] + '\n', "blockquote")
            
            # Lists
            elif re.match(r'^\s*[-*+]\s', line):
                indent = len(line) - len(line.lstrip())
                bullet = "  " * (indent // 2) + "• "
                content = re.sub(r'^\s*[-*+]\s', '', line)
                self.preview.insert(tk.END, bullet)
                self.format_inline_text(content + '\n')
            
            # Numbered lists
            elif re.match(r'^\s*\d+\.\s', line):
                indent = len(line) - len(line.lstrip())
                prefix = "  " * (indent // 2)
                match = re.match(r'^\s*(\d+)\.\s(.*)$', line)
                if match:
                    num, content = match.groups()
                    self.preview.insert(tk.END, f"{prefix}{num}. ")
                    self.format_inline_text(content + '\n')
            
            # Code blocks
            elif line.startswith('```'):
                if hasattr(self, '_in_code_block'):
                    del self._in_code_block
                    self.preview.insert(tk.END, '\n')
                else:
                    self._in_code_block = True
                    lang = line[3:].strip()
                    if lang:
                        self.preview.insert(tk.END, f"[{lang}]\n", "code")
            
            elif hasattr(self, '_in_code_block'):
                self.preview.insert(tk.END, line + '\n', "code")
            
            # Regular text
            else:
                if line.strip():  # Non-empty line
                    self.format_inline_text(line + '\n')
                else:  # Empty line
                    self.preview.insert(tk.END, '\n')
    
    def format_inline_text(self, text):
        """Formatta il testo inline (bold, italic, code)"""
        import re
        
        # Split text into segments for formatting
        pos = 0
        
        # Find and format inline code first
        for match in re.finditer(r'`([^`]+)`', text):
            # Insert normal text before code
            if match.start() > pos:
                self.format_bold_italic(text[pos:match.start()])
            
            # Insert code
            self.preview.insert(tk.END, match.group(1), "code")
            pos = match.end()
        
        # Insert remaining text
        if pos < len(text):
            self.format_bold_italic(text[pos:])
    
    def format_bold_italic(self, text):
        """Formatta grassetto e corsivo"""
        import re
        
        pos = 0
        
        # Process bold and italic
        for match in re.finditer(r'\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*|\*(.+?)\*', text):
            # Insert normal text before formatting
            if match.start() > pos:
                self.preview.insert(tk.END, text[pos:match.start()])
            
            # Determine formatting type
            if match.group(1):  # Bold + Italic (***text***)
                self.preview.insert(tk.END, match.group(1), ("bold", "italic"))
            elif match.group(2):  # Bold (**text**)
                self.preview.insert(tk.END, match.group(2), "bold")
            elif match.group(3):  # Italic (*text*)
                self.preview.insert(tk.END, match.group(3), "italic")
            
            pos = match.end()
        
        # Insert remaining normal text
        if pos < len(text):
            self.preview.insert(tk.END, text[pos:])

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