#!/usr/bin/env python3
import os
import pickle
import base64
import hashlib
import time
import random
import datetime
from cryptography.fernet import Fernet
from weasyprint import HTML
from colorama import Fore, Style, init
from rich.console import Console
from rich.markdown import Markdown
import markdown

init(autoreset=True)

NOTE_FILE = ".note.dat"

# Inizializza Rich console
console = Console()

# ╔═══════════════╗
# VISUAL STYLE FX
# ╚═══════════════╝

def splash():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.MAGENTA + "╔" + "═" * 62 + "╗")
    print(Fore.MAGENTA + "║" + Style.BRIGHT + "       🧠 NOTE CLI CALDRAS • Archivio Quantico Digitale       " + Fore.MAGENTA + "║")
    print(Fore.MAGENTA + "╚" + "═" * 62 + "╝" + Style.RESET_ALL)
    for i in range(3, 0, -1):
        print(Fore.CYAN + f"→ Inizializzazione modulo in {i}..." + Style.RESET_ALL)
        time.sleep(0.5)
    print(Fore.GREEN + "✓ Connessione al nodo stabilita. Sistema pronto.\n" + Style.RESET_ALL)
    time.sleep(0.5)

def access_granted():
    print(Fore.YELLOW + "\nDECODIFICA IN CORSO...")
    for i in range(0, 101, 13):
        barra = "█" * (i // 4) + "▒" * ((100 - i) // 4)
        print(f"\r{Fore.GREEN}[{barra}] {i}%", end="", flush=True)
        time.sleep(0.08 + random.uniform(0, 0.03))
    print("\n" + Fore.CYAN + "✅ ACCESSO CONCESSO\n")

def stampa_nota_cyber(titolo, contenuto, protetta=False):
    ora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stato = "🔐 CIFRATA" if protetta else "📝 LIBERA"
    print(Fore.MAGENTA + "\n╔" + "═" * 60 + "╗")
    print(f"║  ⚡ LOG: {titolo.upper():<50}{Fore.MAGENTA}║")
    print("╚" + "═" * 60 + "╝" + Style.RESET_ALL)
    print(f"{Fore.YELLOW}🕒  {ora}  •  STATO: {stato}")
    print(Fore.GREEN + "\n╭─ CONTENUTO ──────────────────────────────────────────────╮")
    for r in contenuto.strip().splitlines():
        print(f"{Fore.GREEN}│  {Fore.WHITE}{r}")
    print(f"{Fore.GREEN}╰" + "─" * 58 + "╯\n" + Style.RESET_ALL)

def stampa_nota_markdown(titolo, contenuto, protetta=False):
    """Nuova funzione per visualizzare le note in formato markdown"""
    ora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stato = "🔐 CIFRATA" if protetta else "📝 LIBERA"
    
    print(Fore.MAGENTA + "\n╔" + "═" * 60 + "╗")
    print(f"║  ⚡ LOG: {titolo.upper():<50}{Fore.MAGENTA}║")
    print("╚" + "═" * 60 + "╝" + Style.RESET_ALL)
    print(f"{Fore.YELLOW}🕒  {ora}  •  STATO: {stato}")
    print(f"{Fore.CYAN}📋 VISUALIZZAZIONE MARKDOWN\n")
    
    # Usa Rich per renderizzare il markdown
    md = Markdown(contenuto)
    console.print(md)
    print()

def codice_galattico():
    print(Fore.MAGENTA + "\n🔮 Avvio protocollo CALDRAS...")
    for i in range(0, 101, 14):
        barra = "█" * (i // 4) + "▒" * ((100 - i) // 4)
        print(f"\rDECODIFICA >> [{barra}] {i}%", end="", flush=True)
        time.sleep(0.1 + random.uniform(0, 0.05))
    print(Fore.CYAN + "\n\n✅ ACCESSO CONCESSO • CORE DECRIPTATO\n")
    citazioni = [
        "Nell'intervallo tra due battiti del cuore stellare,\nla memoria si scrive sul bordo del tempo.",
        "Solo chi attraversa l'ombra può leggere la luce delle comete.",
        "I dati non mentono, ma a volte sussurrano soltanto agli iniziati.",
        "Tra gli anelli di Caldras si cela ciò che non può essere codificato."
    ]
    scelta = random.choice(citazioni)
    codice = f"C-LDRS.{random.randint(1000,9999)}.{random.choice(['∞','Ξ','Δ'])}"
    print(Fore.MAGENTA + f"👁️‍🗨️ *Codice Galattico Caldras*\n")
    print(Fore.WHITE + f'"{scelta}"\n')
    print(Fore.YELLOW + f"🛰️  SIGILLO • {codice}\n" + Style.RESET_ALL)

# ╔════════════════════════════╗
# CIFRATURA & GESTIONE CONTENUTI
# ╚════════════════════════════╝

def get_key_from_password(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def encrypt_text(text, password):
    key = get_key_from_password(password)
    return Fernet(key).encrypt(text.encode())

def decrypt_text(ciphertext, password):
    key = get_key_from_password(password)
    return Fernet(key).decrypt(ciphertext).decode()

def load_notes():
    if os.path.exists(NOTE_FILE):
        with open(NOTE_FILE, "rb") as f:
            try:
                return pickle.load(f)
            except:
                return []
    return []

def save_notes(notes):
    with open(NOTE_FILE, "wb") as f:
        pickle.dump(notes, f)

def crea_nota(notes):
    titolo = input("Titolo: ").strip()
    print("Scrivi la nota (EOF per terminare):")
    righe = []
    while True:
        r = input()
        if r.strip().lower() == "eof":
            break
        righe.append(r)
    contenuto = "\n".join(righe).strip()
    usa_pw = input("Proteggere con password? (s/n): ").strip().lower()
    if usa_pw == "s":
        pw = input("Password: ").strip()
        contenuto = encrypt_text(contenuto, pw)
        notes.append((titolo, contenuto, pw))
    else:
        notes.append((titolo, contenuto, None))
    save_notes(notes)
    print(Fore.GREEN + f"✅ Nota '{titolo}' salvata.")

def elenca_note(notes):
    if not notes:
        print(Fore.RED + "📭 Nessuna nota disponibile.")
        return
    print(Fore.CYAN + "\n🗒️ Elenco note:")
    for i, n in enumerate(notes):
        print(f"  {i+1}. {n[0]}")
    print()

def visualizza_nota(notes):
    elenca_note(notes)
    try:
        i = int(input("Numero della nota da aprire: ")) - 1
        titolo, contenuto, *resto = notes[i]
        pw = resto[0] if resto else None
        if pw:
            inserita = input(f"🔐 Password per '{titolo}': ")
            if inserita != pw:
                print(Fore.RED + "❌ Password errata.")
                return
            access_granted()
            contenuto = decrypt_text(contenuto, pw)
        
        # Chiedi il formato di visualizzazione
        formato = input("Visualizzare come: (1) Testo normale (2) Markdown [1]: ").strip()
        if formato == "2":
            stampa_nota_markdown(titolo, contenuto, pw is not None)
        else:
            stampa_nota_cyber(titolo, contenuto, pw is not None)
    except:
        print(Fore.RED + "⚠️ Errore nella visualizzazione.")

def visualizza_nota_markdown(notes):
    """Funzione dedicata per visualizzare sempre in formato markdown"""
    elenca_note(notes)
    try:
        i = int(input("Numero della nota da aprire: ")) - 1
        titolo, contenuto, *resto = notes[i]
        pw = resto[0] if resto else None
        if pw:
            inserita = input(f"🔐 Password per '{titolo}': ")
            if inserita != pw:
                print(Fore.RED + "❌ Password errata.")
                return
            access_granted()
            contenuto = decrypt_text(contenuto, pw)
        
        stampa_nota_markdown(titolo, contenuto, pw is not None)
    except:
        print(Fore.RED + "⚠️ Errore nella visualizzazione.")

def modifica_nota(notes):
    elenca_note(notes)
    try:
        i = int(input("Numero della nota da modificare: ")) - 1
        titolo, contenuto, *resto = notes[i]
        pw = resto[0] if resto else None
        if pw:
            inserita = input(f"🔐 Password per '{titolo}': ")
            if inserita != pw:
                print("❌ Password errata.")
                return
            contenuto = decrypt_text(contenuto, pw)
        print("Scrivi il nuovo contenuto (EOF per terminare):")
        righe = []
        while True:
            r = input()
            if r.strip().lower() == "eof":
                break
            righe.append(r)
        nuovo_contenuto = "\n".join(righe).strip()
        if pw:
            nuovo_contenuto = encrypt_text(nuovo_contenuto, pw)
        notes[i] = (titolo, nuovo_contenuto, pw)
        save_notes(notes)
        print(Fore.GREEN + f"✏️ Nota '{titolo}' aggiornata.")
    except:
        print("⚠️ Errore durante la modifica.")

def elimina_nota(notes):
    elenca_note(notes)
    try:
        i = int(input("Numero della nota da eliminare: ")) - 1
        titolo = notes[i][0]
        conferma = input(f"Eliminare '{titolo}'? (s/n): ").lower()
        if conferma == "s":
            del notes[i]
            save_notes(notes)
            print(Fore.RED + f"🗑️ Nota '{titolo}' eliminata.")
    except:
        print("⚠️ Errore durante l'eliminazione.")

def aggiungi_contenuto(notes):
    elenca_note(notes)
    try:
        i = int(input("Numero della nota da aggiornare: ")) - 1
        titolo, contenuto, *resto = notes[i]
        pw = resto[0] if resto else None
        if pw:
            inserita = input(f"🔐 Password per '{titolo}': ")
            if inserita != pw:
                print("❌ Password errata.")
                return
            contenuto = decrypt_text(contenuto, pw)
        print("Scrivi il contenuto da aggiungere (EOF per terminare):")
        nuove_righe = []
        while True:
            r = input()
            if r.strip().lower() == "eof":
                break
            nuove_righe.append(r)
        da_aggiungere = "\n".join(nuove_righe).strip()
        nuovo = contenuto.strip() + "\n\n" + da_aggiungere
        if pw:
            nuovo = encrypt_text(nuovo, pw)
        notes[i] = (titolo, nuovo, pw)
        save_notes(notes)
        print(Fore.CYAN + f"📎 Aggiunta alla nota '{titolo}' completata.")
    except:
        print("⚠️ Errore nell'aggiunta.")

def esporta_pdf(notes):
    elenca_note(notes)
    try:
        i = int(input("Numero della nota da esportare: ")) - 1
        titolo, contenuto, *resto = notes[i]
        pw = resto[0] if resto else None
        if pw:
            inserita = input(f"🔐 Password per '{titolo}': ")
            if inserita != pw:
                print("❌ Password errata.")
                return
            access_granted()
            contenuto = decrypt_text(contenuto, pw)
        
        # Converti markdown in HTML per il PDF
        html_body = markdown.markdown(contenuto)
        html = f"<html><head><style>body{{font-family:sans-serif;padding:2em;}}</style></head><body><h1>{titolo}</h1>{html_body}<hr><p style='font-size:10pt;color:#999;'>🛰️ Sigillo Caldras: C-LDRS.{datetime.datetime.now().strftime('%m%d')}.∞</p></body></html>"
        filename = f"{titolo.replace(' ', '_')}.pdf"
        HTML(string=html).write_pdf(filename)
        print(Fore.GREEN + f"📤 PDF '{filename}' esportato con successo (con rendering markdown).")
    except:
        print("⚠️ Errore nell'esportazione.")

def cerca_note(notes):
    parola = input("🔍 Parola chiave: ").strip().lower()
    trovate = []
    for i, (titolo, contenuto, *resto) in enumerate(notes):
        pw = resto[0] if resto else None
        try:
            testo = decrypt_text(contenuto, pw) if pw else contenuto
            if parola in titolo.lower() or parola in testo.lower():
                trovate.append((i+1, titolo))
        except:
            pass
    if trovate:
        print(Fore.CYAN + f"\n📌 Trovate {len(trovate)} nota(e):")
        for idx, t in trovate:
            print(f"  {idx}. {t}")
    else:
        print("🔎 Nessun risultato.")

# ╔════════════════════════╗
# MENU PRINCIPALE INTERATTIVO
# ╚════════════════════════╝

def menu():
    notes = load_notes()
    splash()
    while True:
        print(Fore.MAGENTA + "\n╔═ NOTE CLI CALDRAS — Menu ─═══════════════════╗")
        print("  1. Crea nuova nota")
        print("  2. Visualizza una nota")
        print("  3. Modifica una nota")
        print("  4. Elimina una nota")
        print("  5. Esporta una nota in PDF")
        print("  6. Cerca tra le note")
        print("  7. Aggiungi contenuto a una nota")
        print("  8. Visualizza nota in Markdown")
        print("  9. Esci")
        print("╚══════════════════════════════════════════════╝")
        scelta = input(">>> ").strip()
        if scelta.lower() == "::caldras":
            codice_galattico()
        elif scelta == "1":
            crea_nota(notes)
        elif scelta == "2":
            visualizza_nota(notes)
        elif scelta == "3":
            modifica_nota(notes)
        elif scelta == "4":
            elimina_nota(notes)
        elif scelta == "5":
            esporta_pdf(notes)
        elif scelta == "6":
            cerca_note(notes)
        elif scelta == "7":
            aggiungi_contenuto(notes)
        elif scelta == "8":
            visualizza_nota_markdown(notes)
        elif scelta == "9":
            print(Fore.YELLOW + "👋 Uscita. Alla prossima.")
            break
        else:
            print(Fore.RED + "⚠️ Scelta non valida.")

# PUNTO DI INGRESSO
if __name__ == "__main__":
    menu()