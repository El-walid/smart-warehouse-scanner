import streamlit as st
import pandas as pd
from pyzbar.pyzbar import decode
from PIL import Image
import os
from datetime import datetime

# ==========================================
# 0. APP CONFIGURATION & GLUE
# ==========================================
st.set_page_config(page_title="Scanner Sidi Ghanem", page_icon="📦", layout="centered")

DB_FILE = "inventory.xlsx"

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================
def init_db():
    """Creates the Enterprise Excel file with TWO sheets if it doesn't exist."""
    if not os.path.exists(DB_FILE):
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            # Sheet 1: The Clean Dashboard
            pd.DataFrame(columns=["Derniere_Mise_A_Jour", "Code_Barre", "Produit", "Stock_Total"]).to_excel(writer, sheet_name="Stock_Actuel", index=False)
            # Sheet 2: The Security Audit Trail
            pd.DataFrame(columns=["Date_Heure", "Code_Barre", "Produit", "Mouvement"]).to_excel(writer, sheet_name="Historique_Securite", index=False)

def get_current_stock(barcode):
    """Calculates the current stock from the clean dashboard sheet."""
    try:
        df = pd.read_excel(DB_FILE, sheet_name="Stock_Actuel")
        clean_barcode = str(barcode).lstrip('0')
        df["Code_Barre_Clean"] = df["Code_Barre"].astype(str).str.lstrip('0')
        
        # If the item exists, return its exact Stock_Total
        if clean_barcode in df["Code_Barre_Clean"].values:
            return df[df["Code_Barre_Clean"] == clean_barcode]["Stock_Total"].iloc[0]
        return 0
    except:
        return 0

def save_to_db(barcode, name, qty_change):
    """Updates BOTH the stateful dashboard and the immutable security ledger."""
    # Read both sheets into memory
    stock_df = pd.read_excel(DB_FILE, sheet_name="Stock_Actuel")
    history_df = pd.read_excel(DB_FILE, sheet_name="Historique_Securite")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_barcode = str(barcode).lstrip('0')
    
    # ==========================================
    # 1. UPDATE THE SECURITY LEDGER (Append-only)
    # ==========================================
    new_history_row = pd.DataFrame([{
        "Date_Heure": now,
        "Code_Barre": str(barcode),
        "Produit": name,
        "Mouvement": qty_change
    }])
    history_df = pd.concat([history_df, new_history_row], ignore_index=True)
    history_df["Code_Barre"] = history_df["Code_Barre"].astype(str) # Force text
    
    # ==========================================
    # 2. UPDATE THE DASHBOARD (Stateful Update)
    # ==========================================
    stock_df["Code_Barre"] = stock_df["Code_Barre"].astype(str)
    stock_df["Code_Barre_Clean"] = stock_df["Code_Barre"].str.lstrip('0')
    
    if clean_barcode in stock_df["Code_Barre_Clean"].values:
        # It exists: Overwrite the total and date
        row_idx = stock_df.index[stock_df['Code_Barre_Clean'] == clean_barcode][0]
        stock_df.at[row_idx, "Stock_Total"] += qty_change
        stock_df.at[row_idx, "Derniere_Mise_A_Jour"] = now
        if name and pd.isna(stock_df.at[row_idx, "Produit"]):
            stock_df.at[row_idx, "Produit"] = name
    else:
        # It does not exist: Create a new row
        new_stock_row = pd.DataFrame([{
            "Derniere_Mise_A_Jour": now,
            "Code_Barre": str(barcode),
            "Produit": name,
            "Stock_Total": qty_change
        }])
        stock_df = pd.concat([stock_df, new_stock_row], ignore_index=True)
        
    stock_df = stock_df.drop(columns=["Code_Barre_Clean"], errors='ignore')
    stock_df["Code_Barre"] = stock_df["Code_Barre"].astype(str) # Force text
    
    # ==========================================
    # 3. SAVE BOTH SHEETS BACK TO EXCEL
    # ==========================================
    with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
        stock_df.to_excel(writer, sheet_name="Stock_Actuel", index=False)
        history_df.to_excel(writer, sheet_name="Historique_Securite", index=False)

# ==========================================
# 2. APP INITIALIZATION & UI FRONTEND
# ==========================================
init_db() # Run the database creator

st.title("📦 Scanner d'Entrepôt Mobile")
st.markdown("Prenez en photo un code-barres ou QR code pour mettre à jour le stock en direct.")

camera_image = st.camera_input("Scanner un article")

# ==========================================
# 3. THE COMPUTER VISION ENGINE
# ==========================================
if camera_image is not None:
    image = Image.open(camera_image)
    decoded_objects = decode(image)

    if decoded_objects:
        for obj in decoded_objects:
            barcode_data = obj.data.decode('utf-8')
            
            # 🧠 Calculate stock BEFORE showing the form
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
                        # 🛡️ Safety Checks for Outbound Stock!
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
    stock_db = pd.read_excel(DB_FILE, sheet_name="Stock_Actuel")
    history_db = pd.read_excel(DB_FILE, sheet_name="Historique_Securite")
    
    if not stock_db.empty:
        # Display the clean, stateful totals table
        stock_db = stock_db.sort_values(by="Derniere_Mise_A_Jour", ascending=False)
        st.dataframe(stock_db, use_container_width=True)
        
        # Display the hidden Security Ledger!
        with st.expander("🔒 Voir le registre de sécurité (Audit Trail)"):
            history_copy = history_db.tail(10).iloc[::-1].copy()
            st.dataframe(history_copy, use_container_width=True)
            st.caption("Ce registre est immuable et conserve toutes les entrées et sorties pour des raisons de sécurité.")
    else:
        st.info("Le registre est vide.")
except Exception as e:
    st.error(f"Erreur de lecture : {e}")