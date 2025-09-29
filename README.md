# 🧠 Caldras

Semplice applicazione per prendere **note cifrate** da shell o interfaccia grafica, scritta in Python.

- `caldras` — versione **terminal-based**
- `caldras-gui` — versione con **interfaccia grafica console-style**
- `wcaldras.py` — versione **terminal-based** per windows
- `wcaldras-gui.py` — versione con **interfaccia grafica console-style** per windows

Entrambe usano lo stesso file dati: **`.note.dat`**

---

## 🚀 Installazione 

### 🚀 Linux
1. rendere eseguibile i file con: 'chmod +x caldras caldras-gui'
2. spostare il file note dentro bin : 'mv caldras caldras-gui /usr/local/bin/'
3. opzionale creare un file .desktop per lanciare caldras-gui senza console 

### 🚀 Windows
1. rendere eseguibile i file con interefaccia installare la dipendenza pyinstaller con: `pip install -U pyinstaller`
2. Dare il seguente comando nella cartella dove risiede lo script `pyinstaller --noconfirm --onefile --windowed --icon=icon_caldras.png wcaldras-gui.py`

---

### 🚀 Dipendenze

```bash
pip install cryptography markdown weasyprint rich
```

sotto windows : `pip install cryptography markdown colorama rich` e installare questo pacchetto [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

poi aggiungere il percorso di wkhtmltopdf nel path di sistema 

sotto endeavou os usare il comando `yay -S python-markdown python-markdown2 python-weasyprint python-cryptography tk python-rich`

**Attenzione una volta reso eseguibile lo script creerà il file dat dentro la cartella in cui punta la shell**