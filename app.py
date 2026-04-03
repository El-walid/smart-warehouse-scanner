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
def get_current_stock(barcode):
    """Calculates the current stock for a specific barcode."""
    try:
        df = pd.read_excel(DB_FILE)
        df["Code_Barre"] = df["Code_Barre"].astype(str)
        return df[df["Code_Barre"] == str(barcode)]["Quantite_Ajoutee"].sum()
    except:
        return 0

if camera_image is not None:
    image = Image.open(camera_image)
    decoded_objects = decode(image)

    if decoded_objects:
        for obj in decoded_objects:
            barcode_data = obj.data.decode('utf-8')
            
            # 🧠 1. Calculate stock BEFORE showing the form
            current_stock = get_current_stock(barcode_data)
            
            st.success(f"✅ Code détecté : **{barcode_data}**")
            st.info(f"📦 Stock actuel disponible : **{current_stock}** unités")
            
            with st.form("inventory_form"):
                st.write("Détails de l'opération :")
                
                operation = st.radio(
                    "Type de mouvement", 
                    ["Entrée de Stock 🟢", "Sortie de Stock 🔴"], 
                    horizontal=True
                )
                
                product_name = st.text_input("Nom du produit (Optionnel)")
                quantity = st.number_input("Quantité", min_value=1, value=1, step=1)
                
                submitted = st.form_submit_button("Valider l'opération")
                
                if submitted:
                    if "Sortie" in operation:
                        # 🛡️ 2. Safety Checks for Outbound Stock!
                        if current_stock <= 0:
                            st.error("❌ Impossible : Ce produit n'est pas en stock (Stock = 0).")
                        elif quantity > current_stock:
                            st.error(f"❌ Stock insuffisant ! Vous essayez de retirer {quantity}, mais il n'y en a que {current_stock}.")
                        else:
                            save_to_db(barcode_data, product_name, -quantity)
                            st.warning(f"📦 {quantity} unité(s) RETIRÉE(S) du stock !")
                            st.rerun() # Refresh the page instantly to show new stock
                    else:
                        # Inbound Stock (Normal)
                        save_to_db(barcode_data, product_name, quantity)
                        st.balloons() 
                        st.success(f"✅ {quantity} unité(s) AJOUTÉE(S) au stock !")
                        st.rerun() # Refresh the page instantly
    else:
        st.error("⚠️ Aucun code-barres détecté. Rapprochez-vous et faites la mise au point.")

# ==========================================
# 4. LIVE DASHBOARD PREVIEW
# ==========================================
st.write("---")
st.subheader("📊 État du Stock en Temps Réel")

try:
    current_db = pd.read_excel(DB_FILE)
    if not current_db.empty:
        # Group by barcode and name to get the TRUE total stock
        resume_stock = current_db.groupby(["Code_Barre", "Produit"])["Quantite_Ajoutee"].sum().reset_index()
        resume_stock.columns = ["Code Barre", "Produit", "Stock Total"]
        
        # Only show items that actually have stock (> 0)
        resume_stock = resume_stock[resume_stock["Stock Total"] > 0]
        
        # Display the clean aggregated table
        st.dataframe(resume_stock, use_container_width=True)
        
        # Hide the messy transaction log inside a dropdown!
        with st.expander("Voir l'historique des transactions"):
            st.dataframe(current_db.tail(10).iloc[::-1], use_container_width=True)
    else:
        st.info("Le registre est vide.")
except Exception as e:
    st.error(f"Erreur de lecture : {e}")