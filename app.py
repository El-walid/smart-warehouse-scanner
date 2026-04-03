import streamlit as st
import pandas as pd
from pyzbar.pyzbar import decode
from PIL import Image
import os
from datetime import datetime

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================
DB_FILE = "inventory.xlsx"

def init_db():
    """Creates the Excel file if it doesn't exist yet."""
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Date_Heure", "Code_Barre", "Produit", "Quantite_Ajoutee"])
        df.to_excel(DB_FILE, index=False)

def save_to_db(barcode, name, qty):
    """Appends a new scan to the Excel ledger."""
    df = pd.read_excel(DB_FILE)
    new_row = pd.DataFrame([{
        "Date_Heure": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Code_Barre": barcode,
        "Produit": name,
        "Quantite_Ajoutee": qty
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# ==========================================
# 2. THE USER INTERFACE (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Scanner Sidi Ghanem", page_icon="📦", layout="centered")
st.title("📦 Scanner d'Entrepôt Mobile")
st.markdown("Prenez en photo un code-barres ou QR code pour mettre à jour le stock en direct.")

init_db() # Ensure database exists

# --- THE MAGIC CAMERA BUTTON ---
camera_image = st.camera_input("Scanner un article")

# ==========================================
# 3. THE COMPUTER VISION ENGINE
# ==========================================
if camera_image is not None:
    # Convert the picture into a format PyZbar can read
    image = Image.open(camera_image)
    decoded_objects = decode(image)

    # If the AI found a barcode in the picture...
    if decoded_objects:
        for obj in decoded_objects:
            barcode_data = obj.data.decode('utf-8')
            
            st.success(f"✅ Code détecté : **{barcode_data}**")
            
            # Show a form to ask the worker how many items they are adding
            # Show a form to ask the worker about the operation
            with st.form("inventory_form"):
                st.write("Détails de l'opération :")
                
                # --- THE NEW TOGGLE ---
                operation = st.radio(
                    "Type de mouvement", 
                    ["Entrée de Stock 🟢", "Sortie de Stock 🔴"], 
                    horizontal=True
                )
                
                product_name = st.text_input("Nom du produit (Optionnel)")
                quantity = st.number_input("Quantité", min_value=1, value=1, step=1)
                
                submitted = st.form_submit_button("Valider l'opération")
                
                if submitted:
                    # 🧠 The Math Logic: If it's a 'Sortie', turn the quantity into a negative number
                    final_qty = quantity if "Entrée" in operation else -quantity
                    
                    save_to_db(barcode_data, product_name, final_qty)
                    
                    # Visual feedback for the worker
                    if "Entrée" in operation:
                        st.balloons() 
                        st.success(f"✅ {quantity} unité(s) AJOUTÉE(S) au stock !")
                    else:
                        st.warning(f"📦 {quantity} unité(s) RETIRÉE(S) du stock !")
    else:
        st.error("⚠️ Aucun code-barres détecté. Rapprochez-vous et faites la mise au point.")

# ==========================================
# 4. LIVE DASHBOARD PREVIEW
# ==========================================
st.write("---")
st.subheader("📊 Dernières Entrées en Stock")
try:
    current_db = pd.read_excel(DB_FILE)
    if not current_db.empty:
        # Show the 5 most recent scans, reversed so newest is at top
        st.dataframe(current_db.tail(5).iloc[::-1], use_container_width=True)
    else:
        st.info("Le registre est vide.")
except Exception as e:
    st.error(f"Erreur de lecture : {e}")