#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk

# Testa solo le funzioni di markdown parsing
test_markdown = """# Titolo Principale

Questo è un **testo in grassetto** e questo è in *corsivo*.

## Sottotitolo

### Terzo livello

- Lista punto 1
- Lista punto 2 con `codice inline`
- Lista punto 3

1. Elemento numerato 1
2. Elemento numerato 2

> Questa è una citazione
> su più righe

```python
def test():
    print("Hello World")
```

Testo normale con ***grassetto e corsivo*** insieme.
"""

def test_markdown_parsing():
    root = tk.Tk()
    root.title("Test Markdown Parsing")
    root.geometry("800x600")
    
    # Area di testo con il markdown
    left_frame = tk.Frame(root)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    tk.Label(left_frame, text="Markdown Source:").pack()
    text_area = tk.Text(left_frame, wrap=tk.WORD, font=("Consolas", 10))
    text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    text_area.insert(tk.END, test_markdown)
    
    # Area di anteprima
    right_frame = tk.Frame(root)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    tk.Label(right_frame, text="Formatted Preview:").pack()
    preview = tk.Text(right_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Segoe UI", 10))
    preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Configurazione dei tag per la formattazione
    preview.tag_config("h1", font=("Segoe UI", 16, "bold"), foreground="blue")
    preview.tag_config("h2", font=("Segoe UI", 14, "bold"), foreground="darkblue")
    preview.tag_config("h3", font=("Segoe UI", 12, "bold"), foreground="darkblue")
    preview.tag_config("bold", font=("Segoe UI", 10, "bold"))
    preview.tag_config("italic", font=("Segoe UI", 10, "italic"))
    preview.tag_config("code", font=("Consolas", 9), background="lightgray")
    preview.tag_config("blockquote", font=("Segoe UI", 10, "italic"), foreground="gray")
    
    def update_preview():
        import re
        
        md_text = text_area.get("1.0", tk.END)
        preview.configure(state=tk.NORMAL)
        preview.delete("1.0", tk.END)
        
        lines = md_text.split('\\n')
        
        for line in lines:
            # Headers
            if line.startswith('### '):
                preview.insert(tk.END, line[4:] + '\\n', "h3")
            elif line.startswith('## '):
                preview.insert(tk.END, line[3:] + '\\n', "h2")
            elif line.startswith('# '):
                preview.insert(tk.END, line[2:] + '\\n', "h1")
            
            # Blockquotes
            elif line.startswith('> '):
                preview.insert(tk.END, "❯ " + line[2:] + '\\n', "blockquote")
            
            # Lists
            elif re.match(r'^\\s*[-*+]\\s', line):
                content = re.sub(r'^\\s*[-*+]\\s', '• ', line)
                format_inline_text(content + '\\n', preview)
            
            # Numbered lists
            elif re.match(r'^\\s*\\d+\\.\\s', line):
                format_inline_text(line + '\\n', preview)
            
            # Code blocks
            elif line.startswith('```'):
                if hasattr(update_preview, '_in_code_block'):
                    del update_preview._in_code_block
                    preview.insert(tk.END, '\\n')
                else:
                    update_preview._in_code_block = True
            
            elif hasattr(update_preview, '_in_code_block'):
                preview.insert(tk.END, line + '\\n', "code")
            
            # Regular text
            else:
                if line.strip():
                    format_inline_text(line + '\\n', preview)
                else:
                    preview.insert(tk.END, '\\n')
        
        preview.configure(state=tk.DISABLED)
    
    def format_inline_text(text, widget):
        import re
        
        pos = 0
        
        # Process inline formatting
        for match in re.finditer(r'\\*\\*\\*(.+?)\\*\\*\\*|\\*\\*(.+?)\\*\\*|\\*(.+?)\\*|`([^`]+)`', text):
            # Insert normal text before formatting
            if match.start() > pos:
                widget.insert(tk.END, text[pos:match.start()])
            
            # Determine formatting type
            if match.group(1):  # Bold + Italic
                widget.insert(tk.END, match.group(1), ("bold", "italic"))
            elif match.group(2):  # Bold
                widget.insert(tk.END, match.group(2), "bold")
            elif match.group(3):  # Italic
                widget.insert(tk.END, match.group(3), "italic")
            elif match.group(4):  # Code
                widget.insert(tk.END, match.group(4), "code")
            
            pos = match.end()
        
        # Insert remaining text
        if pos < len(text):
            widget.insert(tk.END, text[pos:])
    
    # Aggiorna anteprima iniziale
    update_preview()
    
    # Button per aggiornare manualmente
    tk.Button(root, text="Update Preview", command=update_preview).pack()
    
    root.mainloop()

if __name__ == "__main__":
    test_markdown_parsing()