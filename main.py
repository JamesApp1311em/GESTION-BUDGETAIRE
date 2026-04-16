import streamlit as st
import pandas as pd
import os
import time
import plotly.graph_objects as go
from fpdf import FPDF
import datetime
import zipfile
from io import BytesIO
from supabase import create_client, Client 

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Gestion Budgétaire",
    page_icon="logo.png.png", # Corrigé selon ta capture GitHub
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CONNEXION SUPABASE (CLOUD) ---
try:
    URL_SUPABASE = st.secrets["SUPABASE_URL"]
    CLE_SUPABASE = st.secrets["SUPABASE_KEY"]
except Exception:
    st.error("⚠️ Erreur : Les Secrets Supabase ne sont pas configurés sur Streamlit.")
    st.stop()

@st.cache_resource
def init_connection():
    return create_client(URL_SUPABASE, CLE_SUPABASE)

supabase = init_connection()

# --- 3. NETTOYAGE TOTAL DE L'INTERFACE (STYLE PERSONNALISÉ) ---
hide_st_style = """
<style>
header {visibility: hidden !important;}
footer {visibility: hidden !important;}
#MainMenu {visibility: hidden !important;}
div[data-testid="stFooterBlockContainer"] {display: none !important;}
.stAppDeployButton, .stDeployButton, .viewerBadge {display: none !important;}
.block-container {padding-top: 2rem !important; max-width: 500px !important;}
html, body {overscroll-behavior-y: contain !important;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
st.markdown('<link rel="apple-touch-icon" href="https://raw.githubusercontent.com/JacquesSandjamba/Projet-Jacques/main/logo.png.png">', unsafe_allow_html=True)

# --- 4. INITIALISATION DU SESSION STATE ---
if "page" not in st.session_state:
    st.session_state.page = "ACCEUIL"

states = ["inputs_locked", "confirm_exit", "show_extend_table", "current_user", "show_menu", "dev_mode"]
for s in states:
    if s not in st.session_state:
        st.session_state[s] = True if s == "inputs_locked" else False

# --- 5. FONCTIONS DE LECTURE/ÉCRITURE CLOUD (SUPABASE) ---

def charger_table(nom_table):
    """Récupère les données depuis Supabase"""
    try:
        response = supabase.table(nom_table).select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur de lecture Cloud ({nom_table}): {e}")
        return pd.DataFrame()

def sauvegarder_ligne(nom_table, dictionnaire_donnees):
    """Enregistre une nouvelle ligne dans Supabase"""
    try:
        supabase.table(nom_table).insert(dictionnaire_donnees).execute()
        return True
    except Exception as e:
        st.error(f"Erreur d'écriture Cloud ({nom_table}): {e}")
        return False

# --- AJOUTE LES ICI ---

def mettre_a_jour_statut(nom_utilisateur, nouveau_statut):
    """Change le statut dans Supabase"""
    try:
        supabase.table("clients").update({"status": nouveau_statut}).eq("name", nom_utilisateur).execute()
        return True
    except Exception as e:
        st.error(f"Erreur de mise à jour: {e}")
        return False

def supprimer_utilisateur(nom_utilisateur):
    """Supprime un utilisateur de Supabase"""
    try:
        supabase.table("clients").delete().eq("name", nom_utilisateur).execute()
        return True
    except Exception as e:
        st.error(f"Erreur de suppression: {e}")
        return False

# --- 6. FONCTION PDF (COMPLÈTE) ---
def create_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête
    pdf.set_font("Arial", "B", 16)
    pdf.set_fill_color(164, 198, 228)
    pdf.cell(190, 12, "BULLETIN DES DEPENSES MENSUELLES", 1, 1, "C", True)

    # Période
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(45, 10, "PERIODE", 1, 0, "L", True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(70, 10, f"{row['Mois']}", 1, 0, "C")
    pdf.cell(75, 10, f"{row['Annee']}", 1, 1, "C")

    # Revenu
    pdf.set_font("Arial", "B", 12)
    pdf.cell(45, 10, "REVENU MENSUEL($)", 1, 0, "L", True)
    pdf.cell(10, 10, "$", 1, 0, "C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(100, 10, f"{float(row['Revenu']):,.2f}", 1, 0, "R")
    pdf.cell(35, 10, "100%", 1, 1, "C")

    # Détails
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "DETAIL DES DEPENSES ($)", 1, 1, "C", True)

    rev = float(row["Revenu"]) if float(row["Revenu"]) > 0 else 1
    items = [
        ("LOYER", row["Loyer"]),
        ("SCOLARITE", row["Scolarite"]),
        ("RATION", row["Ration"]),
        ("DETTE", row["Dette"]),
        ("ARGENT DE POCHE", row["Poche"]),
        ("ASSISTANCE", row["Assistance"]),
        ("AUTRES DEPENSES", row["Autres"]),
    ]

    pdf.set_font("Arial", "", 11)
    for label, val in items:
        perc = (float(val) / rev) * 100
        pdf.cell(45, 9, label, 1, 0, "L")
        pdf.cell(10, 9, "$", 1, 0, "C")
        pdf.cell(100, 9, f"{float(val):,.2f}", 1, 0, "R")
        pdf.cell(35, 9, f"{perc:.1f}%", 1, 1, "C")

    # Totaux
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(45, 10, "TOTAL DEPENSES", 1, 0, "L", True)
    pdf.cell(10, 10, "$", 1, 0, "C")
    pdf.cell(100, 10, f"{float(row['Total_Depenses']):,.2f}", 1, 0, "R")
    pdf.cell(35, 10, f"{(float(row['Total_Depenses']) / rev) * 100:.1f}%", 1, 1, "C")

    pdf.cell(45, 10, "EPARGNE", 1, 0, "L", True)
    pdf.cell(10, 10, "$", 1, 0, "C")
    pdf.cell(100, 10, f"{float(row['Epargne']):,.2f}", 1, 0, "R")
    pdf.cell(35, 10, f"{(float(row['Epargne']) / rev) * 100:.1f}%", 1, 1, "C")

    # Pied de page
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(190, 5, f"Généré le {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, "R")

    pdf_output = pdf.output(dest="S")
    if isinstance(pdf_output, str):
        return pdf_output.encode("latin-1")
    return bytes(pdf_output)

# --- 7. NAVIGATION ET PAGES ---
# Ici tu pourras ajouter tes blocs : if st.session_state.page == "ACCEUIL": ...


# --- LOGIQUE DES PAGES (A SUIVRE...) ---
# --- 4. LOGIQUE DE FERMETURE (QUITTER L'APP) ---
if st.session_state.confirm_exit:
    with st.container(border=True):
        st.warning("⚠️ Êtes-vous sûr de vouloir fermer l'application ?")
        c1, c2 = st.columns(2)
        if c1.button("✅ Oui, Quitter"):
            st.stop()
        if c2.button("↩️ Annuler"):
            st.session_state.confirm_exit = False
            st.rerun()

# --- 5. PAGE : ACCEUIL ---
elif st.session_state.page == "ACCEUIL":
    # --- BLOCAGE MAINTENANCE ---
    if is_maintenance:
        st.error("🚨 L'APPLICATION EST SOUS MAINTENANCE VEUILLEZ PATIENTER S'IL VOUS PLAIT")

    with st.container(border=True):
        st.markdown(
            "<h1 class='main-title' style='text-align: center;'>🔐 ACCÈS AU SYSTÈME</h1>", 
            unsafe_allow_html=True
        )
        u_n = st.text_input("USER NAME", placeholder="Entrez votre nom...", disabled=is_maintenance)
        u_p = st.text_input("PASSWORD (OPEN APP / MODIFY)", type="password", disabled=is_maintenance)

        if st.button("🚀 OPEN APP", use_container_width=True, disabled=is_maintenance):
            df = pd.read_csv(FILE_CLIENTS, dtype=str).fillna("")
            user_match = df[df["name"].str.strip() == str(u_n).strip()]

            if (
                not user_match.empty
                and user_match.iloc[0]["pw_open_modify"] == str(u_p).strip()
            ):
                if user_match.iloc[0]["status"].lower() in ["true", "active"]:
                    st.session_state.update(
                        {
                            "current_user": u_n,
                            "user_pw_open": str(u_p).strip(),
                            "user_pw_adm_extra": user_match.iloc[0][
                                "pw_adm_print_prog"
                            ],
                            "page": "MAIN_APP",
                        }
                    )
                    st.rerun()
                else:
                    st.error("⚠️ Votre compte est bloqué. Contactez l'administrateur.")
            else:
                st.error("❌ Nom d'utilisateur ou mot de passe incorrect.")

        st.write("---")
        st.write("### Autres options d'accès")
        col_nav1, col_nav2, col_nav3 = st.columns(3)
        if col_nav1.button("🔑 LOGIN", use_container_width=True, disabled=is_maintenance):
            st.session_state.page = "LOGIN"
            st.rerun()
        if col_nav2.button("🛡️ APP ADM", use_container_width=True):
            st.session_state.page = "VERIF_ADM"
            st.rerun()
        if col_nav3.button("👤 USER ADM", use_container_width=True, disabled=is_maintenance):
            st.session_state.page = "VERIF_USER_ADM"
            st.rerun()

    # Message de fin de maintenance
    if "just_restored" in st.session_state and st.session_state.just_restored:
        st.balloons()
        st.success("✅ Merci de Votre Patience...")
        st.session_state.just_restored = False

# --- 6. PAGE : LOGIN (CRÉATION DE COMPTE) ---
elif st.session_state.page == "LOGIN":
    if is_maintenance:
        st.error("🚨 MAINTENANCE EN COURS")
        if st.button("RETOUR"):
            st.session_state.page = "ACCEUIL"
            st.rerun()
        st.stop()

    with st.container(border=True):
        st.markdown(
            "<h2 style='text-align: center;'>⚙️ CRÉATION DE NOUVEAU COMPTE</h2>",
            unsafe_allow_html=True,
        )
        st.info(
            "Veuillez définir vos informations d'identification selon la nomenclature du système."
        )

        new_n = st.text_input("USER NAME")
        new_p1 = st.text_input("PASSWORD (OPEN APP / MODIFY)", type="password")
        new_p2 = st.text_input("PASSWORD (ADM / PRINT / PROGRESS)", type="password")
        new_p3 = st.text_input("PASSWORD (USER ADM)", type="password")

        # --- SUPPRIME LA LIGNE "if st.button(" QUI ÉTAIT ICI ---

if st.button("💾 ENREGISTRER L'UTILISATEUR", use_container_width=True, type="primary"):
    if new_n and new_p1 and new_p2 and new_p3:
        # 1. On récupère la liste des clients depuis le Cloud
        df_clients = charger_table("clients")
        
        # 2. On vérifie si le nom existe déjà dans la base
        if not df_clients.empty and new_n in df_clients["name"].values:
            st.error("❌ Ce nom d'utilisateur existe déjà sur le Cloud.")
        else:
            # 3. Préparation des données
            new_entry = {
                "name": new_n,
                "pw_open_modify": new_p1,
                "pw_adm_print_prog": new_p2,
                "pw_user_adm": new_p3,
                "status": "Active",
            }
            # ... suite de ton code (appel à sauvegarder_ligne par exemple)
                    
                    # 4. Envoi vers Supabase via ta fonction
                    succes = sauvegarder_ligne("clients", new_entry)
                    
                    if succes:
                        st.success(f"✅ Compte pour '{new_n}' créé avec succès sur le Cloud !")
                        time.sleep(2) # On laisse le temps de lire le message
                        st.session_state.page = "ACCEUIL"
                        st.rerun()
            else:
                st.warning("⚠️ Veuillez remplir tous les champs obligatoires.")

        if st.button("⬅️ RETOUR À L'ACCUEIL", use_container_width=True):
            st.session_state.page = "ACCEUIL"
            st.rerun()

# --- 7. PAGE : VERIF ADMIN ---
elif st.session_state.page == "VERIF_ADM":
    with st.container(border=True):
        st.subheader("Authentification Administrateur Système")
        code_adm = st.text_input("Entrez le code maître (Master Code)", type="password")
        if st.button("VALIDER L'ACCÈS", use_container_width=True):
            if code_adm == "G1711E":
                st.session_state.page = "APP_ADM"
                st.rerun()
            else:
                st.error("Code incorrect.")
        if st.button("⬅️ RETOUR"):
            st.session_state.page = "ACCEUIL"
            st.rerun()

# --- 8. PAGE : APP ADM (ADMINISTRATION) ---
elif st.session_state.page == "APP_ADM":
    with st.container(border=True):
        st.markdown(
            "<h2 style='text-align: center;'>🖥️ ADMINISTRATION GÉNÉRALE</h2>",
            unsafe_allow_html=True,
        )
        st.write("Gestion des comptes utilisateurs et accès système.")

        # --- AJOUT DES BOUTONS EXPORT ET IMPORT ---
        col_ext, col_dev, col_exp, col_imp = st.columns(4)

        with col_ext:
            if st.button("📂 EXTEND", use_container_width=True):
                st.session_state.show_extend_table = not st.session_state.get(
                    "show_extend_table", False
                )

        with col_dev:
            label_dev = (
                "🔒 CACHER MENUS"
                if st.session_state.get("dev_mode")
                else "🔓 OPTIONS DEV"
            )
            if st.button(label_dev, use_container_width=True):
                st.session_state.dev_mode = not st.session_state.get("dev_mode", False)
                st.rerun()

        with col_exp:
            # Fonction pour créer le ZIP (Modifiée pour inclure les retraits)
            def get_all_data_zip():
                buf = BytesIO()
                with zipfile.ZipFile(buf, "w") as z:
                    # On ajoute FILE_DEP_EPARGNE à la liste des fichiers à sauvegarder
                    for f in [FILE_CLIENTS, FILE_DATA, FILE_DEP_EPARGNE]:
                        if os.path.exists(f):
                            z.write(f)
                return buf.getvalue()

            if st.download_button(
                label="📥 Export",
                data=get_all_data_zip(),
                file_name=f"Backup_{datetime.datetime.now().strftime('%d_%m_%Y')}.zip",
                mime="application/zip",
                use_container_width=True
            ):
                # Création du verrou de maintenance
                with open(FILE_MAINTENANCE, "w") as f:
                    f.write("MAINTENANCE_ACTIVE")
                st.session_state.page = "ACCEUIL"
                st.rerun()

        # --- SECTION IMPORT (SORTIE DES COLONNES POUR LE MOBILE) ---
        st.write("---") # Petite ligne de séparation
        uploaded_backup = st.file_uploader("Sélectionner le backup ZIP pour restaurer", type="zip")
        
        if uploaded_backup:
            # 🟢 On affiche un message de succès pour forcer le rafraîchissement sur mobile
            st.success(f"✅ Fichier détecté : {uploaded_backup.name}")
            
            # Le bouton prend toute la largeur pour être facile à cliquer sur mobile
            if st.button("📤 LANCER L'IMPORTATION", use_container_width=True, type="primary"):
                with st.spinner("Restauration en cours..."):
                    with zipfile.ZipFile(uploaded_backup, 'r') as z:
                        z.extractall('.')
                    
                    # Suppression du verrou de maintenance
                    if os.path.exists(FILE_MAINTENANCE):
                        os.remove(FILE_MAINTENANCE)
                    
                    st.session_state.just_restored = True
                    st.session_state.page = "ACCEUIL"
                    st.rerun()

        if st.session_state.get("show_extend_table"):
            st.write("### Base de données complète des utilisateurs")
            df_full = pd.read_csv(FILE_CLIENTS, dtype=str)
            st.dataframe(df_full, use_container_width=True)
            st.write("---")

        st.subheader("Liste des comptes et Status")
        df_adm = pd.read_csv(FILE_CLIENTS, dtype=str).fillna("")

        # --- Dans la boucle d'affichage des utilisateurs ---
        for idx, row in df_adm.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                
                # Nom de l'utilisateur
                c1.write(f"👤 **{row['name']}**")

                # Déterminer l'état actuel (sécurité contre les majuscules/minuscules)
                is_active = str(row["status"]).lower() in ["true", "active"]
                status_label = "ACTIVE" if is_active else "BLOCKED"

                # Changement de statut via Checkbox (Action Cloud)
                if c2.checkbox(f"Statut: {status_label}", value=is_active, key=f"chk_{idx}") != is_active:
                    n_statut = "Active" if not is_active else "Blocked"
                    if mettre_a_jour_statut(row['name'], n_statut):
                        st.success(f"Statut de {row['name']} mis à jour !")
                        st.rerun()

                # Suppression de l'utilisateur (Action Cloud)
                if c3.button("🗑️", key=f"btn_del_{idx}"):
                    if supprimer_utilisateur(row['name']):
                        st.warning(f"Utilisateur {row['name']} supprimé.")
                        st.rerun()
        if st.button("⬅️ QUITTER L'ADMINISTRATION", use_container_width=True):
            st.session_state.page = "ACCEUIL"
            st.rerun()
# --- 9. PAGE : MAIN APP (APPLICATION PRINCIPALE) ---
elif st.session_state.page == "MAIN_APP":
    # MODIFICATION CLOUD : On récupère les données depuis Supabase au lieu du CSV
    df_h = charger_table("donnees_depenses") 
    
    if not df_h.empty:
        user_recs = df_h[df_h["Utilisateur"] == st.session_state.current_user].copy()
    else:
        user_recs = pd.DataFrame()

    # --- BOUTON DE CONTRÔLE (MENU / RETOUR / DÉCONNEXION) ---
    if not st.session_state.show_menu:
        col_nav1, col_nav2 = st.columns([0.7, 0.3])
        with col_nav1:
            if st.button("➡️ OUVRIR LE MENU", use_container_width=True):
                st.session_state.show_menu = True
                st.rerun()
        with col_nav2:
            if st.button("🟦 DÉCONNEXION", use_container_width=True):
                st.session_state.clear()
                st.rerun()
    else:
        if st.button("⬅️ RETOUR AU BULLETIN", use_container_width=True):
            st.session_state.show_menu = False
            st.session_state.show_print_pwd = False
            st.session_state.show_admin_pwd = False
            st.rerun()

    st.write("---")

    # --- LOGIQUE D'AFFICHAGE EXCLUSIF ---
    if st.session_state.show_menu:
        st.markdown(
            "<h2 style='color: #1E88E5; text-align: center;'>📋 MENU DE GESTION</h2>",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        # --- COLONNE 1 : SÉLECTION DU MOIS ---
        with col1:
            if st.button("📅 SELECT MONTH", use_container_width=True):
                st.session_state.show_date_picker = not st.session_state.get("show_date_picker", False)

            if st.session_state.get("show_date_picker"):
                with st.container(border=True):
                    m_list = [
                        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
                    ]
                    m_c = st.selectbox("Mois", m_list)
                    a_c = st.selectbox("Année", [str(a) for a in range(2024, 2100)])

                    versions = pd.DataFrame()
                    if not user_recs.empty:
                        versions = user_recs[
                            (user_recs["Mois"].str.startswith(m_c))
                            & (user_recs["Annee"].astype(str) == a_c)
                        ]

                    if not versions.empty:
                        v_choisie = st.selectbox(
                            "Versions existantes", versions["Mois"].tolist()
                        )

                    if st.button("✅ CONSULTER / CRÉER NOUVEAU"):
                        st.session_state.update({
                            "sel_mois_base": m_c,
                            "sel_annee": a_c,
                            "show_date_picker": False,
                            "show_menu": False,
                        })
                        if not versions.empty:
                            v_to_load = v_choisie if "v_choisie" in locals() else versions["Mois"].iloc[0]
                            target = versions[versions["Mois"] == v_to_load].iloc[0]
                            st.session_state.update({
                                "sel_mois_affiche": target["Mois"],
                                "n_rev": target["Revenu"],
                                "n_loy": target["Loyer"],
                                "n_sco": target["Scolarite"],
                                "n_rat": target["Ration"],
                                "n_det": target["Dette"],
                                "n_poc": target["Poche"],
                                "n_ast": target["Assistance"],
                                "n_aut": target["Autres"],
                                "inputs_locked": True,
                            })
                        else:
                            st.session_state.update({"sel_mois_affiche": m_c, "inputs_locked": False})
                            for k in ["n_rev", "n_loy", "n_sco", "n_rat", "n_det", "n_poc", "n_ast", "n_aut"]:
                                st.session_state[k] = 0
                        st.rerun()

        # --- COLONNE 2 : PRINT SÉCURISÉ ---
        with col2:
            if st.button("🖨️ PRINT (BULLETIN)", use_container_width=True):
                st.session_state.show_print_pwd = not st.session_state.get("show_print_pwd", False)
                st.session_state.show_print_ui = False

            if st.session_state.get("show_print_pwd"):
                with st.container(border=True):
                    p_print = st.text_input("Code Print requis", type="password", key="p_print")
                    if st.button("🔓 VALIDER PRINT"):
                        if p_print == st.session_state.get("user_pw_adm_extra"):
                            st.session_state.show_print_ui = True
                            st.session_state.show_print_pwd = False
                            st.rerun()
                        else:
                            st.error("Code incorrect")

            if st.session_state.get("show_print_ui"):
                with st.container(border=True):
                    if not user_recs.empty:
                        list_mois = user_recs.sort_values("Date_Enregistrement", ascending=False)["Mois"].tolist()
                        choix_pdf = st.selectbox("Choisir la version à imprimer", list_mois)

                        if choix_pdf:
                            row_selected = user_recs[user_recs["Mois"] == choix_pdf].iloc[0]
                            pdf_bytes = create_pdf(row_selected)
                            st.download_button(
                                label="📥 Télécharger PDF",
                                data=pdf_bytes,
                                file_name=f"Bulletin_{choix_pdf}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                            )

        # --- ADMIN & PROGRESSION ---
        c_adm, c_prog = st.columns(2)
        with c_adm:
            if st.button("🛡️ ADMIN DATA", use_container_width=True):
                st.session_state.show_admin_pwd = not st.session_state.get("show_admin_pwd", False)

            if st.session_state.get("show_admin_pwd"):
                with st.container(border=True):
                    p_admin = st.text_input("Code Admin requis", type="password", key="p_admin")
                    if st.button("🔓 ACCÉDER À LA BASE"):
                        if p_admin == st.session_state.get("user_pw_adm_extra"):
                            st.session_state.page = "VIEW_BASE"
                            st.rerun()
                        else:
                            st.error("Code incorrect")

        with c_prog:
            if st.button("📈 PROGRESSION", use_container_width=True):
                st.session_state.page = "PROGRESS"
                st.rerun()

    else:
        # --- INTERFACE 2 : LE BULLETIN DE DÉPENSES ---
        with st.container(border=True):
            st.markdown(
                "<h1 style='text-align: center; color: #2E7D32;'>💰 BULLETIN DES DEPENSES</h1>",
                unsafe_allow_html=True,
            )

            sel_m_base = st.session_state.get("sel_mois_base")
            L = st.session_state.get("inputs_locked", True)

            if sel_m_base and L:
                versions_du_mois = pd.DataFrame()
                if not user_recs.empty:
                    versions_du_mois = user_recs[
                        (user_recs["Mois"].str.startswith(sel_m_base))
                        & (user_recs["Annee"].astype(str) == st.session_state.get("sel_annee"))
                    ]

                def ext_v(n):
                    return int(n.split("Mod")[-1]) if "Mod" in n else 0

                show_modify_button = False
                
                if versions_du_mois.empty:
                    show_modify_button = True
                    btn_label = "📝 SAISIR LES DONNÉES"
                else:
                    max_v = versions_du_mois["Mois"].apply(ext_v).max()
                    cur_v = ext_v(st.session_state.get("sel_mois_affiche", ""))
                    
                    if cur_v == max_v:
                        show_modify_button = True
                        btn_label = "📝 MODIFIER LA DERNIÈRE VERSION"
                    else:
                        st.warning(f"⚠️ Lecture seule : Version Mod {max_v} disponible.")

                if show_modify_button:
                    if st.button(btn_label, key="btn_mod_unique", use_container_width=True):
                        st.session_state.ask_lock_pwd = True

                    if st.session_state.get("ask_lock_pwd"):
                        with st.container(border=True):
                            pwd_bulletin = st.text_input(
                                "Entrez le PASSWORD (MODIFY)", type="password", key="pwd_mod_field"
                            )
                            if st.button("🔓 DÉVERROUILLER", key="btn_unlock_final"):
                                if pwd_bulletin == st.session_state.get("user_pw_open"):
                                    st.session_state.inputs_locked = False
                                    st.session_state.ask_lock_pwd = False
                                    st.success("Accès autorisé")
                                    st.rerun()
                                else:
                                    st.error("Mot de passe incorrect.")

            # --- AFFICHAGE DES CHAMPS ---
            col_m, col_a = st.columns(2)
            col_m.text_input("MOIS EN COURS", value=st.session_state.get("sel_mois_affiche", ""), disabled=True, key="disp_m")
            col_a.text_input("ANNÉE", value=st.session_state.get("sel_annee", ""), disabled=True, key="disp_a")

            st.session_state.n_rev = st.number_input("REVENU GLOBAL ($)", value=int(st.session_state.get("n_rev", 0)), disabled=L)

            c1, c2 = st.columns(2)
            st.session_state.n_loy = c1.number_input("LOYER", value=int(st.session_state.get("n_loy", 0)), disabled=L)
            st.session_state.n_sco = c1.number_input("SCOLARITÉ", value=int(st.session_state.get("n_sco", 0)), disabled=L)
            st.session_state.n_rat = c1.number_input("RATION", value=int(st.session_state.get("n_rat", 0)), disabled=L)
            st.session_state.n_det = c2.number_input("DETTES", value=int(st.session_state.get("n_det", 0)), disabled=L)
            st.session_state.n_poc = c2.number_input("POCHE", value=int(st.session_state.get("n_poc", 0)), disabled=L)
            st.session_state.n_ast = c2.number_input("ASSISTANCE", value=int(st.session_state.get("n_ast", 0)), disabled=L)
            st.session_state.n_aut = st.number_input("AUTRES", value=int(st.session_state.get("n_aut", 0)), disabled=L)

            if st.button("🚀 CALCULER", use_container_width=True, type="primary"):
                if not st.session_state.get("sel_mois_base"):
                    st.warning("Sélectionnez d'abord un mois dans le MENU.")
                else:
                    st.session_state.total_dep = sum([
                        st.session_state.n_loy, st.session_state.n_sco,
                        st.session_state.n_rat, st.session_state.n_det,
                        st.session_state.n_poc, st.session_state.n_ast,
                        st.session_state.n_aut,
                    ])
                    st.session_state.epargne = st.session_state.n_rev - st.session_state.total_dep
                    st.session_state.page = "RESULTATS"
                    st.rerun()
# --- 10. PAGE : RÉSULTATS ---
elif st.session_state.page == "RESULTATS":
    with st.container(border=True):
        nom_mois_base = st.session_state.get("sel_mois_base", "MOIS")
        annee_sel = str(st.session_state.get("sel_annee", "2024"))

        st.markdown(
            f"<h2 style='text-align: center;'>📊 BILAN : {nom_mois_base} {annee_sel}</h2>",
            unsafe_allow_html=True,
        )

        rev_val = float(st.session_state.get("n_rev", 0))
        rev_pour_calcul = rev_val if rev_val > 0 else 1
        ratio_epargne = (st.session_state.get("epargne", 0) / rev_pour_calcul) * 100

        col_res1, col_res2 = st.columns(2)
        col_res1.metric("TOTAL DÉPENSES", f"{st.session_state.get('total_dep', 0)} $")
        col_res2.metric(
            "ÉPARGNE NETTE",
            f"{st.session_state.get('epargne', 0)} $",
            delta=f"{ratio_epargne:.1f}%",
        )

        if st.session_state.get("epargne", 0) >= 0:
            st.success(f"Félicitations ! Épargne de {ratio_epargne:.1f}% du revenu.")
        else:
            st.error(f"Déficit de {abs(st.session_state.get('epargne', 0))} $.")

        # --- BOUTON SAUVEGARDE CLOUD ---
        if st.button("💾 SAUVEGARDER CETTE VERSION", use_container_width=True):
            # 1. On récupère l'historique depuis Supabase
            df_hist = charger_table("donnees_depenses")
            current_user = st.session_state.current_user

            # 2. Logique de détection de doublons (exactement comme avant)
            doublon_exact = pd.DataFrame()
            if not df_hist.empty:
                doublon_exact = df_hist[
                    (df_hist["Utilisateur"] == current_user)
                    & (df_hist["Annee"].astype(str) == annee_sel)
                    & (df_hist["Revenu"].astype(float) == float(st.session_state.get("n_rev", 0)))
                    & (df_hist["Loyer"].astype(float) == float(st.session_state.get("n_loy", 0)))
                    & (df_hist["Scolarite"].astype(float) == float(st.session_state.get("n_sco", 0)))
                    & (df_hist["Ration"].astype(float) == float(st.session_state.get("n_rat", 0)))
                    & (df_hist["Dette"].astype(float) == float(st.session_state.get("n_det", 0)))
                    & (df_hist["Poche"].astype(float) == float(st.session_state.get("n_poc", 0)))
                    & (df_hist["Assistance"].astype(float) == float(st.session_state.get("n_ast", 0)))
                    & (df_hist["Autres"].astype(float) == float(st.session_state.get("n_aut", 0)))
                    & (df_hist["Mois"].str.contains(nom_mois_base))
                ]

            if not doublon_exact.empty:
                st.warning("⚠️ Données déjà présentes. Aucune modification détectée.")
            else:
                # 3. Calcul de la version (Mod0, Mod1...)
                base_combinee = f"{nom_mois_base}{annee_sel}"
                nom_version = base_combinee
                
                if not df_hist.empty:
                    exist_versions = df_hist[
                        (df_hist["Utilisateur"] == current_user)
                        & (df_hist["Mois"].str.startswith(base_combinee))
                    ]
                    if not exist_versions.empty:
                        nom_version = f"{base_combinee}Mod{len(exist_versions)}"

                # 4. Préparation du dictionnaire pour Supabase
                new_row = {
                    "Utilisateur": current_user,
                    "Mois": nom_version,
                    "Annee": annee_sel,
                    "Revenu": float(st.session_state.get("n_rev", 0)),
                    "Loyer": float(st.session_state.get("n_loy", 0)),
                    "Scolarite": float(st.session_state.get("n_sco", 0)),
                    "Ration": float(st.session_state.get("n_rat", 0)),
                    "Dette": float(st.session_state.get("n_det", 0)),
                    "Poche": float(st.session_state.get("n_poc", 0)),
                    "Assistance": float(st.session_state.get("n_ast", 0)),
                    "Autres": float(st.session_state.get("n_aut", 0)),
                    "Total_Depenses": float(st.session_state.get("total_dep", 0)),
                    "Epargne": float(st.session_state.get("epargne", 0)),
                    "Date_Enregistrement": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                }

                # 5. Envoi au Cloud
                if sauvegarder_ligne("donnees_depenses", new_row):
                    st.success(f"✅ Enregistré dans le Cloud : {nom_version}")
                    time.sleep(1)
                    st.session_state.page = "MAIN_APP"
                    st.rerun()

        if st.button("⬅️ RETOUR"):
            st.session_state.page = "MAIN_APP"
            st.rerun()
# --- 11. PAGE : VIEW BASE (ACCÈS COMPLET AUX DONNÉES) ---
elif st.session_state.page == "VIEW_BASE":
    with st.container(border=True):
        st.title("🔓 GESTION DE L'HISTORIQUE")
        
        # MODIFICATION CLOUD : Lecture depuis Supabase
        df_full_h = charger_table("donnees_depenses")
        
        if not df_full_h.empty:
            user_data = df_full_h[df_full_h["Utilisateur"] == st.session_state.current_user]
        else:
            user_data = pd.DataFrame()

        st.write(f"Enregistrements pour : {st.session_state.current_user}")
        st.dataframe(user_data, use_container_width=True)

        st.write("---")
        st.subheader("Supprimer une entrée")
        
        # On vérifie s'il y a des données à supprimer
        list_versions = ["---"]
        if not user_data.empty:
            list_versions += user_data["Mois"].tolist()
            
        target_del = st.selectbox(
            "Sélectionner la version à effacer", list_versions
        )

        if target_del != "---":
            if st.button("🗑️ CONFIRMER LA SUPPRESSION", type="secondary"):
                try:
                    # MODIFICATION CLOUD : Suppression ciblée dans Supabase
                    supabase.table("donnees_depenses")\
                        .delete()\
                        .eq("Utilisateur", st.session_state.current_user)\
                        .eq("Mois", target_del)\
                        .execute()
                    
                    st.warning(f"Version {target_del} supprimée du Cloud.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de la suppression : {e}")

        if st.button("⬅️ RETOUR"):
            st.session_state.page = "MAIN_APP"
            st.rerun()
# --- 12. PAGE : PROGRESSION (TRI PRÉCIS DATE + HEURE) ---
elif st.session_state.page == "PROGRESS":
    import time
    import plotly.graph_objects as go

    # Initialisation de la variable d'état pour la confirmation de suppression
    if "delete_confirm_idx" not in st.session_state:
        st.session_state.delete_confirm_idx = None

    with st.container(border=True):
        if not st.session_state.get("prog_access_granted", False):
            st.title("📈 ANALYSE DE PROGRESSION")
            pwd_input = st.text_input("PASSWORD", type="password")
            if st.button("🔓 VALIDER L'ACCÈS", use_container_width=True):
                if pwd_input == st.session_state.get("user_pw_adm_extra"):
                    st.session_state.prog_access_granted = True
                    st.rerun()
                else:
                    st.error("Code incorrect.")
            if st.button("⬅️ RETOUR"):
                st.session_state.page = "MAIN_APP"
                st.rerun()

        else:
            is_mode_2 = st.session_state.get("mode_prog2", False)
            col_nav_titre, col_nav_btn = st.columns([2, 1])
            with col_nav_btn:
                if st.button(
                    "📈 1st FONCTION" if is_mode_2 else "🔄 2nd FONCTION",
                    use_container_width=True,
                ):
                    st.session_state.mode_prog2 = not is_mode_2
                    st.rerun()
            with col_nav_titre:
                st.title("📈 PROGRESSION 2" if is_mode_2 else "📈 PROGRESSION 1")

            # --- RÉCUPÉRATION DES DONNÉES CLOUD ---
            df_p = charger_table("donnees_depenses")
            data_user = pd.DataFrame()
            if not df_p.empty:
                data_user = df_p[df_p["Utilisateur"] == st.session_state.current_user].copy()

            if not data_user.empty:
                # 1. Extraction de la base du mois
                data_user["Mois_Base"] = data_user["Mois"].str.split("Mod").str[0]

                # 2. CONVERSION PRÉCISE (Date + Heure)
                data_user["Date_Enregistrement"] = pd.to_datetime(
                    data_user["Date_Enregistrement"], dayfirst=True, errors="coerce"
                )
                data_user = data_user.dropna(subset=["Date_Enregistrement"])

                # 3. TRI CHRONOLOGIQUE ET FILTRAGE DERNIÈRE VERSION
                data_user = data_user.sort_values(by="Date_Enregistrement", ascending=True)
                data_final = data_user.drop_duplicates(subset=["Mois_Base", "Annee"], keep="last")

                # --- 🟢 INTERFACE 1 : GRAPHIQUES ---
                if not is_mode_2:
                    c_f1, c_f2, c_f3 = st.columns(3)
                    type_graph = c_f1.selectbox("Type", ["Courbe", "Barre", "Aire", "Points"])
                    periode = c_f2.selectbox("Période", ["Par Mois", "Par Année"])
                    intervalle = c_f3.selectbox("Échelle", [50, 100, 200, 500, 1000], index=3)

                    if periode == "Par Année":
                        df_plot = data_final.groupby("Annee")[["Epargne", "Total_Depenses", "Revenu"]].sum().reset_index()
                        x_axis_label = "Annee"
                    else:
                        df_plot = data_final.copy()
                        x_axis_label = "Mois_Base"

                    val_max = float(df_plot[["Epargne", "Total_Depenses", "Revenu"]].max().max() if not df_plot.empty else 100)
                    y_limit_fixe = ((val_max // intervalle) + 2) * intervalle

                    st.write(f"### Évolution de l'Épargne")
                    fig1 = go.Figure()
                    color_epargne = "#2e7d32"

                    if type_graph == "Barre":
                        fig1.add_trace(go.Bar(x=df_plot[x_axis_label], y=df_plot["Epargne"], marker_color=color_epargne))
                    elif type_graph == "Aire":
                        fig1.add_trace(go.Scatter(x=df_plot[x_axis_label], y=df_plot["Epargne"], fill="tozeroy", line=dict(color=color_epargne)))
                    elif type_graph == "Points":
                        fig1.add_trace(go.Scatter(x=df_plot[x_axis_label], y=df_plot["Epargne"], mode="markers", marker=dict(size=12, color=color_epargne)))
                    else:
                        fig1.add_trace(go.Scatter(x=df_plot[x_axis_label], y=df_plot["Epargne"], mode="lines+markers", line=dict(color=color_epargne, width=3)))

                    fig1.update_layout(yaxis=dict(range=[0, y_limit_fixe], dtick=intervalle), height=400)
                    st.plotly_chart(fig1, use_container_width=True)

                # --- 🟠 INTERFACE 2 : GESTION DES DÉPENSES ---
                else:
                    total_ep_cumulee = data_final["Epargne"].astype(float).sum()
                    
                    # RÉCUPÉRATION DES RETRAITS DEPUIS SUPABASE
                    df_dep_cloud = charger_table("depenses_epargne")
                    user_deps = pd.DataFrame()
                    if not df_dep_cloud.empty:
                        user_deps = df_dep_cloud[df_dep_cloud["Utilisateur"] == st.session_state.current_user].reset_index(drop=True)
                    
                    total_sorties = user_deps["Montant"].astype(float).sum() if not user_deps.empty else 0
                    solde_actuel = total_ep_cumulee - total_sorties

                    c1, c2 = st.columns(2)
                    with c1:
                        st.info(f"TOTAL ÉPARGNE : {total_ep_cumulee:,.2f} $")
                    with c2:
                        st.success(f"SOLDE ACTUEL : {solde_actuel:,.2f} $")

                    if st.button("💸 ENREGISTRER UN RETRAIT", use_container_width=True):
                        st.session_state.show_f = not st.session_state.get("show_f", False)
                        st.rerun()

                    if st.session_state.get("show_f"):
                        with st.form("form_dep_epargne", clear_on_submit=True):
                            f_rai = st.text_input("Raison")
                            f_mon = st.number_input("Montant ($)", min_value=0.0)
                            if st.form_submit_button("✅ CONFIRMER LE RETRAIT"):
                                if f_rai and f_mon > 0:
                                    if f_mon > solde_actuel:
                                        st.error("Solde insuffisant")
                                    else:
                                        row_retrait = {
                                            "Utilisateur": st.session_state.current_user,
                                            "Raison": f_rai,
                                            "Montant": float(f_mon),
                                            "Date": pd.Timestamp.now().strftime("%d/%m/%Y")
                                        }
                                        if sauvegarder_ligne("depenses_epargne", row_retrait):
                                            st.success("Retrait enregistré au Cloud.")
                                            time.sleep(1)
                                            st.rerun()

                    st.write("### 📂 Historique des retraits")
                    if not user_deps.empty:
                        # On crée une liste pour le selectbox (Utilise l'ID Supabase si présent, sinon l'index)
                        list_display = [f"{i+1}. {r['Raison']} | {r['Montant']}$" for i, r in user_deps.iterrows()]
                        sel_idx = st.selectbox("Sélectionner", range(len(list_display)), format_func=lambda x: list_display[x])

                        if st.button("🗑️ SUPPRIMER CE RETRAIT", use_container_width=True):
                            st.session_state.delete_confirm_idx = sel_idx
                            st.rerun()

                        if st.session_state.get("delete_confirm_idx") == sel_idx:
                            with st.container(border=True):
                                st.warning("Confirmer la suppression ?")
                                if st.button("❌ OUI, SUPPRIMER"):
                                    # Suppression Cloud par Raison et Montant (ou ID si tu en as un)
                                    row_to_del = user_deps.iloc[sel_idx]
                                    supabase.table("depenses_epargne").delete()\
                                        .eq("Utilisateur", st.session_state.current_user)\
                                        .eq("Raison", row_to_del["Raison"])\
                                        .eq("Montant", row_to_del["Montant"]).execute()
                                    
                                    st.session_state.delete_confirm_idx = None
                                    st.success("Supprimé.")
                                    time.sleep(1)
                                    st.rerun()
                    else:
                        st.info("Aucun retrait.")

            else:
                st.warning("Données insuffisantes.")

            st.write("---")
            if st.button("🔒 VERROUILLER ET QUITTER", use_container_width=True):
                st.session_state.prog_access_granted = False
                st.session_state.page = "MAIN_APP"
                st.rerun()

# --- 13. PAGE : VERIF USER ADM ---
elif st.session_state.page == "VERIF_USER_ADM":
    with st.container(border=True):
        st.subheader("Accès Modification Profil")
        u_check = st.text_input("Nom de l'utilisateur")
        p_check = st.text_input("Mot de Passe USER ADM", type="password")

        if st.button("VÉRIFIER LES DROITS", use_container_width=True):
            # MODIFICATION CLOUD : On vérifie directement dans la table des utilisateurs
            df_c = charger_table("utilisateurs") # Assure-toi que le nom de la table est correct
            
            if not df_c.empty:
                # On cherche la correspondance (on s'assure que tout est en texte pour comparer)
                match = df_c[
                    (df_c["name"].astype(str) == u_check) & 
                    (df_c["pw_user_adm"].astype(str) == p_check)
                ]
                
                if not match.empty:
                    # On stocke les infos trouvées pour la page d'édition
                    st.session_state.temp_user = match.iloc[0].to_dict()
                    st.session_state.page = "EDIT_PROFIL"
                    st.success("Droits vérifiés avec succès !")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Identifiants ADM incorrects.")
            else:
                st.error("Base de données utilisateurs vide ou inaccessible.")

        if st.button("⬅️ RETOUR"):
            st.session_state.page = "ACCEUIL"
            st.rerun()
# --- 14. PAGE : EDIT PROFIL ---
elif st.session_state.page == "EDIT_PROFIL":
    with st.container(border=True):
        st.title("✏️ MODIFICATION DES CODES")
        usr = st.session_state.temp_user
        st.write(f"Utilisateur : **{usr['name']}**")

        new_p1 = st.text_input("NOUVEAU PW (OPEN/MODIFY)", value=usr["pw_open_modify"])
        new_p2 = st.text_input(
            "NOUVEAU PW (ADM/PRINT/PROG)", value=usr["pw_adm_print_prog"]
        )
        new_p3 = st.text_input("NOUVEAU PW (USER ADM)", value=usr["pw_user_adm"])

        if st.button("💾 ENREGISTRER LES MODIFICATIONS", use_container_width=True):
            # Vérification si des changements ont été apportés
            if (
                new_p1 == usr["pw_open_modify"]
                and new_p2 == usr["pw_adm_print_prog"]
                and new_p3 == usr["pw_user_adm"]
            ):
                st.info("Aucune modification n'a été effectuée.")
            else:
                try:
                    # MODIFICATION CLOUD : Mise à jour directe dans Supabase
                    supabase.table("utilisateurs")\
                        .update({
                            "pw_open_modify": new_p1,
                            "pw_adm_print_prog": new_p2,
                            "pw_user_adm": new_p3
                        })\
                        .eq("name", usr["name"])\
                        .execute()

                    # Mise à jour de l'état temporaire session
                    st.session_state.temp_user.update({
                        "pw_open_modify": new_p1,
                        "pw_adm_print_prog": new_p2,
                        "pw_user_adm": new_p3,
                    })

                    st.success("✅ Mise à jour réussie dans le Cloud !")
                    time.sleep(1)
                except Exception as e:
                    st.error(f"Erreur lors de la mise à jour : {e}")

        if st.button("⬅️ RETOUR"):
            st.session_state.page = "ACCEUIL"
            st.rerun()
