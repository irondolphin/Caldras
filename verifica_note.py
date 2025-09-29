#!/usr/bin/env python3
import os
import pickle

def verifica_note_esistenti():
    note_file = ".note.dat"
    
    if not os.path.exists(note_file):
        print("❌ Nessun file di note trovato.")
        return
    
    try:
        with open(note_file, "rb") as f:
            notes = pickle.load(f)
        
        print(f"✅ File note caricato correttamente! Trovate {len(notes)} note:")
        print()
        
        for i, note in enumerate(notes, 1):
            title = note[0] if len(note) > 0 else "Senza titolo"
            has_password = len(note) == 3 and note[2] is not None
            status = "🔒 Protetta" if has_password else "📝 Libera"
            
            print(f"{i}. {title} [{status}]")
            
            # Mostra anteprima del contenuto (solo per note non protette)
            if not has_password and len(note) > 1:
                content = note[1][:100] + "..." if len(note[1]) > 100 else note[1]
                print(f"   Anteprima: {content}")
            
            print()
        
    except Exception as e:
        print(f"❌ Errore nel caricamento delle note: {e}")

if __name__ == "__main__":
    verifica_note_esistenti()