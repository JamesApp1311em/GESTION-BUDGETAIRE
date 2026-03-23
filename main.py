import streamlit as st
import pandas as pd
import os
import time
from fpdf import FPDF
import datetime

# --- 1. DÉFINITION DES CONSTANTES (INDISPENSABLE ICI POUR ÉVITER LE NAMEERROR) ---
FILE_CLIENTS = "clients.csv"
FILE_DATA = "historique_complet.csv"

# --- 2. GESTION INTELLIGENTE DE LA BASE DE DONNÉES ---
class FakeDB(dict):
    """Simule Replit DB sur Streamlit Cloud avec la fonction .prefix()"""
    def prefix(self, p):
        return [k for k in self.keys() if k.startswith(p)]

try:
    from replit import db
    use_replit_db = True
except (ImportError, ModuleNotFoundError):
    # Initialisation de la base factice
    db = FakeDB()
    use_replit_db = False

    # Chargement initial depuis le CSV pour éviter les mots de passe "None"
    if os.path.exists(FILE_CLIENTS):
        try:
            df_init = pd.read_csv(FILE_CLIENTS)
            for _, row in df_init.iterrows():
                # On remplit la DB interne avec les infos du fichier
                db[f"user_profile_{row['name']}"] = {
                    "pw_open_modify": str(row["pw_open_modify"]),
                    "pw_adm_print_prog": str(row["pw_adm_print_prog"]),
                    "pw_user_adm": str(row["pw_user_adm"]),
                    "status": str(row["status"])
                }
        except Exception:
            pass

# --- 1. CONFIGURATION DE LA PAGE ---
# Garde bien ceci juste APRÈS les imports et la définition de FakeDB
st.set_page_config(
    page_title="Gestionnaire de Dépenses",
    page_icon="💰", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. INITIALISATION DU SESSION STATE ---
if "page" not in st.session_state:
    st.session_state.page = "ACCEUIL"
if "inputs_locked" not in st.session_state:
    st.session_state.inputs_locked = True
if "confirm_exit" not in st.session_state:
    st.session_state.confirm_exit = False
if "show_extend_table" not in st.session_state:
    st.session_state.show_extend_table = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "show_menu" not in st.session_state:
    st.session_state.show_menu = False
if "dev_mode" not in st.session_state:
    st.session_state.dev_mode = False

# --- 3. GESTION DYNAMIQUE DU STYLE CSS ---
visibility = "hidden" if not st.session_state.dev_mode else "visible"
display_mode = "none" if not st.session_state.dev_mode else "block"

hide_st_style = f"""
    <style>
    /* Masquage des menus standards */
    header {{ visibility: {visibility} !important; }}
    footer {{ visibility: {visibility} !important; }}
    #MainMenu {{ visibility: {visibility} !important; }}

    /* --- CIBLE L'IMAGE 1 (Ordinateur : Manage App) --- */
    [data-testid="stStatusWidget"], 
    .stAppDeployButton,
    div[class*="st-emotion-cache-1ky0h6e"],
    div[data-testid="stToolbar"] {{
        display: {display_mode} !important;
    }}

    /* --- CIBLE L'IMAGE 2 (Android : Fork, Crown, etc.) --- */
    /* On utilise un sélecteur qui attrape tous les conteneurs flottants de Streamlit */
    div[class*="viewerBadge"],
    div[class*="st-emotion-cache-kgp75f"],
    div[class*="st-emotion-cache-15z92p2"],
    div[class*="st-emotion-cache-1647p8l"],
    .stDeployButton {{
        display: {display_mode} !important;
        visibility: {visibility} !important;
    }}

    /* Empêcher le pull-to-refresh et fixer l'écran */
    html, body {{
        overscroll-behavior-y: contain !important;
        overflow: hidden !important;
    }}
    
    .stMain {{ 
        overflow-y: auto !important; 
    }}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
# --- 4. INITIALISATION DES BASES DE DONNÉES ---
FILE_CLIENTS = "clients.csv"
FILE_DATA = "historique_complet.csv"


def init_db():
    if not os.path.exists(FILE_CLIENTS) or os.stat(FILE_CLIENTS).st_size == 0:
        columns_clients = [
            "name",
            "pw_open_modify",
            "pw_adm_print_prog",
            "pw_user_adm",
            "status",
        ]
        pd.DataFrame(columns=columns_clients).to_csv(FILE_CLIENTS, index=False)

    if not os.path.exists(FILE_DATA) or os.stat(FILE_DATA).st_size == 0:
        columns_data = [
            "Utilisateur",
            "Mois",
            "Annee",
            "Revenu",
            "Loyer",
            "Scolarite",
            "Ration",
            "Dette",
            "Poche",
            "Assistance",
            "Autres",
            "Total_Depenses",
            "Epargne",
            "Date_Enregistrement",
        ]
        pd.DataFrame(columns=columns_data).to_csv(FILE_DATA, index=False)


init_db()
# --- AJOUTER CES FONCTIONS ICI ---


def sauvegarder_utilisateur_db(username, pw_open, pw_adm, pw_user_adm, status="Active"):
    """Enregistre ou met à jour un profil utilisateur dans Replit DB et CSV"""
    # 1. Sauvegarde dans Replit DB
    db[f"user_profile_{username}"] = {
        "pw_open_modify": pw_open,
        "pw_adm_print_prog": pw_adm,
        "pw_user_adm": pw_user_adm,
        "status": status,
    }
    
    # 2. Sauvegarde miroir dans le CSV (pour accès téléphone)
    new_user = pd.DataFrame([[username, pw_open, pw_adm, pw_user_adm, status]], 
                            columns=["name", "pw_open_modify", "pw_adm_print_prog", "pw_user_adm", "status"])
    new_user.to_csv(FILE_CLIENTS, mode='a', header=False, index=False)


def sauvegarder_data_db(username, mois, annee, revenu, depenses_dict, total, epargne):
    """Enregistre une entrée budgétaire dans Replit DB et CSV"""
    date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    key = f"data_{username}_{mois}_{annee}"
    
    # 1. Sauvegarde dans Replit DB
    db[key] = {
        "Utilisateur": username,
        "Mois": mois,
        "Annee": annee,
        "Revenu": revenu,
        "Depenses": depenses_dict,
        "Total_Depenses": total,
        "Epargne": epargne,
        "Date": date_now,
    }
    
    # 2. Sauvegarde miroir dans le CSV (pour historique téléphone)
    new_data = pd.DataFrame([[
        username, mois, annee, revenu, 
        depenses_dict.get("Loyer", 0), depenses_dict.get("Scolarite", 0),
        depenses_dict.get("Ration", 0), depenses_dict.get("Dette", 0),
        depenses_dict.get("Poche", 0), depenses_dict.get("Assistance", 0),
        depenses_dict.get("Autres", 0), total, epargne, date_now
    ]], columns=[
        "Utilisateur", "Mois", "Annee", "Revenu", "Loyer", "Scolarite", 
        "Ration", "Dette", "Poche", "Assistance", "Autres", 
        "Total_Depenses", "Epargne", "Date_Enregistrement"
    ])
    new_data.to_csv(FILE_DATA, mode='a', header=False, index=False)


def recuperer_historique_db(username):
    """Récupère toutes les données d'un utilisateur depuis Replit DB ou CSV"""
    historique = []
    
    # Priorité à Replit DB si disponible et non vide
    keys = db.prefix(f"data_{username}")
    if keys:
        for key in keys:
            historique.append(db[key])
        return pd.DataFrame(historique)
    
    # Sinon (cas du téléphone), lecture depuis le CSV
    elif os.path.exists(FILE_DATA):
        df_all = pd.read_csv(FILE_DATA)
        return df_all[df_all["Utilisateur"] == username]
    
    return pd.DataFrame()
# --- 5. FONCTIONS TECHNIQUES ---


def create_pdf(row):
    """Génère le bulletin de paie au format PDF"""
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

    # Détails des dépenses
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

    # Observation
    obs = "GOOD" if float(row["Epargne"]) > 0 else "BAD"
    pdf.ln(5)
    pdf.cell(45, 10, "OBSERVATION", 1, 0, "L", True)
    if obs == "GOOD":
        pdf.set_fill_color(144, 238, 144)  # Vert
    else:
        pdf.set_fill_color(255, 99, 71)  # Rouge
    pdf.cell(145, 10, obs, 1, 1, "C", True)

    # Pied de page
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(
        190,
        5,
        f"Document généré le {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
        0,
        1,
        "R",
    )

    # RETOUR BINAIRE CORRECT
    return pdf.output(dest="S").encode("latin-1")


# --- LOGIQUE DES PAGES (A SUIVRE...) ---
# --- . LOGIQUE DE FERMETURE (QUITTER L'APP) ---
if st.session_state.confirm_exit:
    with st.container(border=True):
        st.warning("⚠️ Êtes-vous sûr de vouloir fermer l'application ?")
        c1, c2 = st.columns(2)
        if c1.button("✅ Oui, Quitter"):
            st.stop()
        if c2.button("↩️ Annuler"):
            st.session_state.confirm_exit = False
            st.rerun()

# --- 6. PAGE : ACCEUIL ---
elif st.session_state.page == "ACCEUIL":
    with st.container(border=True):
        st.markdown(
            "<h1 class='main-title'>🔐 ACCÈS AU SYSTÈME</h1>", unsafe_allow_html=True
        )
        u_n = st.text_input("USER NAME", placeholder="Entrez votre nom...")
        u_p = st.text_input("PASSWORD (OPEN APP / MODIFY)", type="password")

        if st.button("🚀 OPEN APP", use_container_width=True):
            user_key = f"user_profile_{u_n}"
            user_data = None
            user_found = False

            # 1. ON CHERCHE D'ABORD DANS LA DB (Replit)
            if user_key in db:
                user_data = db[user_key]
                user_found = True
            
            # 2. SINON ON CHERCHE DANS LE CSV (Pour le téléphone)
            elif os.path.exists(FILE_CLIENTS):
                df_c = pd.read_csv(FILE_CLIENTS)
                match = df_c[df_c['name'] == u_n]
                if not match.empty:
                    user_data = match.iloc[0].to_dict()
                    user_found = True

            # --- LOGIQUE DE VÉRIFICATION ---
            if user_found:
                # Vérification du mot de passe
                if str(user_data["pw_open_modify"]) == str(u_p).strip():
                    # Vérification du statut
                    if str(user_data["status"]).lower() in ["true", "active"]:
                        st.session_state.update(
                            {
                                "current_user": u_n,
                                "user_pw_open": str(u_p).strip(),
                                "user_pw_adm_extra": user_data["pw_adm_print_prog"],
                                "page": "MAIN_APP",
                            }
                        )
                        st.rerun()
                    else:
                        st.error("⚠️ Compte bloqué.")
                else:
                    st.error("❌ Mot de passe incorrect.")
            else:
                st.error("❌ Utilisateur inexistant dans la base persistante.")

        st.write("---")
        st.write("### Autres options d'accès")
        col_nav1, col_nav2, col_nav3 = st.columns(3)
        if col_nav1.button("🔑 LOGIN", use_container_width=True):
            st.session_state.page = "LOGIN"
            st.rerun()
        if col_nav2.button("🛡️ APP ADM", use_container_width=True):
            st.session_state.page = "VERIF_ADM"
            st.rerun()
        if col_nav3.button("👤 USER ADM", use_container_width=True):
            st.session_state.page = "VERIF_USER_ADM"
            st.rerun()

        st.write("---")

# --- 7. PAGE : LOGIN (CRÉATION DE COMPTE) ---
elif st.session_state.page == "LOGIN":
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

        if st.button("💾 ENREGISTRER L'UTILISATEUR", use_container_width=True):
            if new_n and new_p1 and new_p2 and new_p3:
                user_key = f"user_profile_{new_n}"
                if user_key in db:
                    st.error("Ce nom d'utilisateur existe déjà.")
                else:
                    # SAUVEGARDE PERSISTANTE DANS REPLIT DB
                    sauvegarder_utilisateur_db(new_n, new_p1, new_p2, new_p3)
                    st.success(f"Compte pour '{new_n}' créé avec succès !")
                    st.session_state.page = "ACCEUIL"
                    st.rerun()
            else:
                st.warning("Veuillez remplir tous les champs obligatoires.")

        if st.button("⬅️ RETOUR À L'ACCUEIL", use_container_width=True):
            st.session_state.page = "ACCEUIL"
            st.rerun()

# --- 8. PAGE : VERIF ADMIN ---
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

# --- 9. PAGE : APP ADM (ADMINISTRATION) ---
elif st.session_state.page == "APP_ADM":
    with st.container(border=True):
        st.markdown(
            "<h2 style='text-align: center;'>🖥️ ADMINISTRATION GÉNÉRALE</h2>",
            unsafe_allow_html=True,
        )
        st.write("Gestion des comptes utilisateurs et accès système.")

        # --- LIGNE DE BOUTONS ---
        col_ext, col_dev = st.columns(2)

        with col_ext:
            if st.button("📂 EXTEND", use_container_width=True):
                st.session_state.show_extend_table = not st.session_state.get("show_extend_table", False)

        with col_dev:
            label_dev = "🔒 CACHER MENUS" if st.session_state.get("dev_mode") else "🔓 OPTIONS DEV"
            if st.button(label_dev, use_container_width=True):
                st.session_state.dev_mode = not st.session_state.get("dev_mode", False)
                st.rerun()

        # --- RÉCUPÉRATION DES DONNÉES ---
        all_users = []
        
        # On utilise le db (qui contient maintenant les données du CSV grâce au nouveau FakeDB)
        keys = db.prefix("user_profile_")
        for key in keys:
            user_data = db[key]
            username = key.replace("user_profile_", "")
            all_users.append({
                "name": username,
                "status": user_data.get("status", "Active"),
                "pw_open": user_data.get("pw_open_modify"),
                "pw_adm": user_data.get("pw_adm_print_prog"),
                "pw_user_adm": user_data.get("pw_user_adm")
            })
        
        df_adm = pd.DataFrame(all_users)

        # Affichage de la table EXTEND
        if st.session_state.get("show_extend_table") and not df_adm.empty:
            st.write("### Base de données complète des utilisateurs")
            st.dataframe(df_adm, use_container_width=True)
            st.write("---")

        st.subheader("Liste des comptes et Status")
        
        if df_adm.empty:
            st.warning("Aucun utilisateur trouvé dans la base de données.")
        else:
            for idx, row in df_adm.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(f"👤 **{row['name']}**")

                    is_active = str(row["status"]).lower() in ["active", "true"]
                    status_label = "ACTIVE" if is_active else "BLOCKED"

                    if c2.checkbox(f"Statut: {status_label}", value=is_active, key=f"chk_{row['name']}"):
                        if not is_active:
                            new_status = "Active"
                            db[f"user_profile_{row['name']}"]["status"] = new_status
                            df_upd = pd.read_csv(FILE_CLIENTS)
                            df_upd.loc[df_upd['name'] == row['name'], 'status'] = new_status
                            df_upd.to_csv(FILE_CLIENTS, index=False)
                            st.rerun()
                    else:
                        if is_active:
                            new_status = "Blocked"
                            db[f"user_profile_{row['name']}"]["status"] = new_status
                            df_upd = pd.read_csv(FILE_CLIENTS)
                            df_upd.loc[df_upd['name'] == row['name'], 'status'] = new_status
                            df_upd.to_csv(FILE_CLIENTS, index=False)
                            st.rerun()

                    if c3.button("🗑️", key=f"btn_del_{row['name']}"):
                        if f"user_profile_{row['name']}" in db:
                            del db[f"user_profile_{row['name']}"]
                        df_upd = pd.read_csv(FILE_CLIENTS)
                        df_upd = df_upd[df_upd['name'] != row['name']]
                        df_upd.to_csv(FILE_CLIENTS, index=False)
                        st.rerun()

        if st.button("⬅️ QUITTER L'ADMINISTRATION", use_container_width=True):
            st.session_state.page = "ACCEUIL"
            st.rerun()

# --- 10. PAGE : VERIF USER ADM (ACCÈS AU PROFIL) ---
elif st.session_state.page == "VERIF_USER_ADM":
    with st.container(border=True):
        st.subheader("Authentification Profil Utilisateur")
        u_name = st.text_input("NOM D'UTILISATEUR")
        u_pass_adm = st.text_input("MOT DE PASSE (USER ADM)", type="password")
        
        if st.button("ACCÉDER AU PROFIL", use_container_width=True):
            user_key = f"user_profile_{u_name}"
            user_found = False
            user_data = None

            # Vérification Replit DB
            if user_key in db:
                user_data = db[user_key]
                user_found = True
            # Vérification CSV
            elif os.path.exists(FILE_CLIENTS):
                df_c = pd.read_csv(FILE_CLIENTS)
                match = df_c[df_c['name'] == u_name]
                if not match.empty:
                    user_data = match.iloc[0].to_dict()
                    user_found = True

            if user_found:
                if str(user_data.get("pw_user_adm")) == str(u_pass_adm):
                    st.session_state.temp_user = u_name
                    st.session_state.page = "EDIT_PROFILE"
                    st.rerun()
                else:
                    st.error("Mot de passe USER ADM incorrect.")
            else:
                st.error("Utilisateur introuvable.")
        
        if st.button("⬅️ RETOUR"):
            st.session_state.page = "ACCEUIL"
            st.rerun()
# --- 10. PAGE : MAIN APP (APPLICATION PRINCIPALE) ---
elif st.session_state.page == "MAIN_APP":
    # 1. Chargement des données AU DÉBUT du bloc
    df_h = pd.read_csv(FILE_DATA)
    user_recs = df_h[df_h["Utilisateur"] == st.session_state.current_user].copy()

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
                st.session_state.show_date_picker = not st.session_state.get(
                    "show_date_picker", False
                )

            if st.session_state.get("show_date_picker"):
                with st.container(border=True):
                    m_list = [
                        "Janvier",
                        "Février",
                        "Mars",
                        "Avril",
                        "Mai",
                        "Juin",
                        "Juillet",
                        "Août",
                        "Septembre",
                        "Octobre",
                        "Novembre",
                        "Décembre",
                    ]
                    m_c = st.selectbox("Mois", m_list)
                    a_c = st.selectbox("Année", [str(a) for a in range(2024, 2100)])

                    versions = user_recs[
                        (user_recs["Mois"].str.startswith(m_c))
                        & (user_recs["Annee"].astype(str) == a_c)
                    ]

                    if not versions.empty:
                        v_choisie = st.selectbox(
                            "Versions existantes", versions["Mois"].tolist()
                        )

                    if st.button("✅ CONSULTER / CRÉER NOUVEAU"):
                        st.session_state.update(
                            {
                                "sel_mois_base": m_c,
                                "sel_annee": a_c,
                                "show_date_picker": False,
                                "show_menu": False,
                            }
                        )
                        if not versions.empty:
                            v_to_load = (
                                v_choisie
                                if "v_choisie" in locals()
                                else versions["Mois"].iloc[0]
                            )
                            target = versions[versions["Mois"] == v_to_load].iloc[0]
                            st.session_state.update(
                                {
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
                                }
                            )
                        else:
                            st.session_state.update(
                                {"sel_mois_affiche": m_c, "inputs_locked": False}
                            )
                            for k in [
                                "n_rev",
                                "n_loy",
                                "n_sco",
                                "n_rat",
                                "n_det",
                                "n_poc",
                                "n_ast",
                                "n_aut",
                            ]:
                                st.session_state[k] = 0
                        st.rerun()

        # --- COLONNE 2 : PRINT SÉCURISÉ ---
        with col2:
            if st.button("🖨️ PRINT (BULLETIN)", use_container_width=True):
                st.session_state.show_print_pwd = not st.session_state.get(
                    "show_print_pwd", False
                )
                st.session_state.show_print_ui = False

            if st.session_state.get("show_print_pwd"):
                with st.container(border=True):
                    p_print = st.text_input(
                        "Code Print requis", type="password", key="p_print"
                    )
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
                        list_mois = user_recs.sort_values(
                            "Date_Enregistrement", ascending=False
                        )["Mois"].tolist()
                        choix_pdf = st.selectbox(
                            "Choisir la version à imprimer", list_mois
                        )

                        if choix_pdf:
                            row_selected = user_recs[
                                user_recs["Mois"] == choix_pdf
                            ].iloc[0]

                            # On génère les bytes directement
                            pdf_bytes = create_pdf(row_selected)

                            # On passe pdf_bytes directement à data
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
                st.session_state.show_admin_pwd = not st.session_state.get(
                    "show_admin_pwd", False
                )

            if st.session_state.get("show_admin_pwd"):
                with st.container(border=True):
                    p_admin = st.text_input(
                        "Code Admin requis", type="password", key="p_admin"
                    )
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
            L = st.session_state.get("inputs_locked", False)

            if sel_m_base and L:
                versions_du_mois = user_recs[
                    (user_recs["Mois"].str.startswith(sel_m_base))
                    & (
                        user_recs["Annee"].astype(str)
                        == st.session_state.get("sel_annee")
                    )
                ]
                if not versions_du_mois.empty:

                    def ext_v(n):
                        return int(n.split("Mod")[-1]) if "Mod" in n else 0

                    max_v = versions_du_mois["Mois"].apply(ext_v).max()
                    cur_v = ext_v(st.session_state.get("sel_mois_affiche", ""))

                    if cur_v == max_v:
                        # LE BOUTON AVEC LA BONNE VARIABLE : user_pw_open
                        if st.button(
                            "📝 MODIFIER LA DERNIÈRE VERSION", use_container_width=True
                        ):
                            st.session_state.ask_lock_pwd = True

                        if st.session_state.get("ask_lock_pwd"):
                            with st.container(border=True):
                                pwd_bulletin = st.text_input(
                                    "Entrez le PASSWORD (MODIFY)", type="password"
                                )
                                if st.button("🔓 DÉVERROUILLER"):
                                    # Correction ici : on utilise la clé exacte de ton bloc ACCEUIL
                                    if pwd_bulletin == st.session_state.get(
                                        "user_pw_open"
                                    ):
                                        st.session_state.inputs_locked = False
                                        st.session_state.ask_lock_pwd = False
                                        st.success("Accès autorisé")
                                        st.rerun()
                                    else:
                                        st.error("Mot de passe incorrect.")
                    else:
                        st.warning(f"⚠️ Lecture seule : Version Mod {max_v} disponible.")
                else:
                    if st.button("📝 MODIFIER LES DONNÉES", use_container_width=True):
                        st.session_state.inputs_locked = False
                        st.rerun()

            # --- AFFICHAGE DES CHAMPS ---
            col_m, col_a = st.columns(2)
            col_m.text_input(
                "MOIS EN COURS",
                value=st.session_state.get("sel_mois_affiche", ""),
                disabled=True,
            )
            col_a.text_input(
                "ANNÉE", value=st.session_state.get("sel_annee", ""), disabled=True
            )

            st.session_state.n_rev = st.number_input(
                "REVENU GLOBAL ($)",
                value=int(st.session_state.get("n_rev", 0)),
                disabled=L,
            )

            c1, c2 = st.columns(2)
            st.session_state.n_loy = c1.number_input(
                "LOYER", value=int(st.session_state.get("n_loy", 0)), disabled=L
            )
            st.session_state.n_sco = c1.number_input(
                "SCOLARITÉ", value=int(st.session_state.get("n_sco", 0)), disabled=L
            )
            st.session_state.n_rat = c1.number_input(
                "RATION", value=int(st.session_state.get("n_rat", 0)), disabled=L
            )
            st.session_state.n_det = c2.number_input(
                "DETTES", value=int(st.session_state.get("n_det", 0)), disabled=L
            )
            st.session_state.n_poc = c2.number_input(
                "POCHE", value=int(st.session_state.get("n_poc", 0)), disabled=L
            )
            st.session_state.n_ast = c2.number_input(
                "ASSISTANCE", value=int(st.session_state.get("n_ast", 0)), disabled=L
            )
            st.session_state.n_aut = st.number_input(
                "AUTRES", value=int(st.session_state.get("n_aut", 0)), disabled=L
            )

            if st.button("🚀 CALCULER", use_container_width=True, type="primary"):
                if not st.session_state.get("sel_mois_base"):
                    st.warning("Sélectionnez d'abord un mois dans le MENU.")
                else:
                    st.session_state.total_dep = sum(
                        [
                            st.session_state.n_loy,
                            st.session_state.n_sco,
                            st.session_state.n_rat,
                            st.session_state.n_det,
                            st.session_state.n_poc,
                            st.session_state.n_ast,
                            st.session_state.n_aut,
                        ]
                    )
                    st.session_state.epargne = (
                        st.session_state.n_rev - st.session_state.total_dep
                    )
                    st.session_state.page = "RESULTATS"
                    st.rerun()

# --- 11. PAGE : RÉSULTATS ---
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

        if st.button("💾 SAUVEGARDER CETTE VERSION", use_container_width=True):
            import time
            import os

            if not os.path.exists(FILE_DATA):
                pd.DataFrame(
                    columns=[
                        "Utilisateur",
                        "Mois",
                        "Annee",
                        "Revenu",
                        "Loyer",
                        "Scolarite",
                        "Ration",
                        "Dette",
                        "Poche",
                        "Assistance",
                        "Autres",
                        "Total_Depenses",
                        "Epargne",
                        "Date_Enregistrement",
                    ]
                ).to_csv(FILE_DATA, index=False)

            df_hist = pd.read_csv(FILE_DATA)
            current_user = st.session_state.current_user

            doublon_exact = df_hist[
                (df_hist["Utilisateur"] == current_user)
                & (df_hist["Annee"].astype(str) == annee_sel)
                & (
                    df_hist["Revenu"].astype(float)
                    == float(st.session_state.get("n_rev", 0))
                )
                & (
                    df_hist["Loyer"].astype(float)
                    == float(st.session_state.get("n_loy", 0))
                )
                & (
                    df_hist["Scolarite"].astype(float)
                    == float(st.session_state.get("n_sco", 0))
                )
                & (
                    df_hist["Ration"].astype(float)
                    == float(st.session_state.get("n_rat", 0))
                )
                & (
                    df_hist["Dette"].astype(float)
                    == float(st.session_state.get("n_det", 0))
                )
                & (
                    df_hist["Poche"].astype(float)
                    == float(st.session_state.get("n_poc", 0))
                )
                & (
                    df_hist["Assistance"].astype(float)
                    == float(st.session_state.get("n_ast", 0))
                )
                & (
                    df_hist["Autres"].astype(float)
                    == float(st.session_state.get("n_aut", 0))
                )
                & (df_hist["Mois"].str.contains(nom_mois_base))
            ]

            if not doublon_exact.empty:
                st.warning(f"⚠️ Données déjà présentes. Aucune modification détectée.")
            else:
                base_combinee = f"{nom_mois_base}{annee_sel}"
                exist_versions = df_hist[
                    (df_hist["Utilisateur"] == current_user)
                    & (df_hist["Mois"].str.startswith(base_combinee))
                ]

                nom_version = (
                    f"{base_combinee}Mod{len(exist_versions)}"
                    if not exist_versions.empty
                    else base_combinee
                )

                new_row = {
                    "Utilisateur": current_user,
                    "Mois": nom_version,
                    "Annee": annee_sel,
                    "Revenu": st.session_state.get("n_rev", 0),
                    "Loyer": st.session_state.get("n_loy", 0),
                    "Scolarite": st.session_state.get("n_sco", 0),
                    "Ration": st.session_state.get("n_rat", 0),
                    "Dette": st.session_state.get("n_det", 0),
                    "Poche": st.session_state.get("n_poc", 0),
                    "Assistance": st.session_state.get("n_ast", 0),
                    "Autres": st.session_state.get("n_aut", 0),
                    "Total_Depenses": st.session_state.get("total_dep", 0),
                    "Epargne": st.session_state.get("epargne", 0),
                    "Date_Enregistrement": pd.Timestamp.now().strftime(
                        "%d/%m/%Y %H:%M"
                    ),
                }

                pd.concat([df_hist, pd.DataFrame([new_row])], ignore_index=True).to_csv(
                    FILE_DATA, index=False
                )
                st.success(f"✅ Enregistré : {nom_version}")
                time.sleep(1)
                st.session_state.page = "MAIN_APP"
                st.rerun()

        if st.button("⬅️ RETOUR"):
            st.session_state.page = "MAIN_APP"
            st.rerun()
# --- 12. PAGE : VIEW BASE (ACCÈS COMPLET AUX DONNÉES) ---
elif st.session_state.page == "VIEW_BASE":
    with st.container(border=True):
        st.title("🔓 GESTION DE L'HISTORIQUE")
        df_full_h = pd.read_csv(FILE_DATA)
        user_data = df_full_h[df_full_h["Utilisateur"] == st.session_state.current_user]

        st.write(f"Enregistrements pour : {st.session_state.current_user}")
        st.dataframe(user_data, use_container_width=True)

        st.write("---")
        st.subheader("Supprimer une entrée")
        target_del = st.selectbox(
            "Sélectionner la version à effacer", ["---"] + user_data["Mois"].tolist()
        )

        if target_del != "---":
            if st.button("🗑️ CONFIRMER LA SUPPRESSION", type="secondary"):
                df_full_h = df_full_h[
                    ~(
                        (df_full_h["Utilisateur"] == st.session_state.current_user)
                        & (df_full_h["Mois"] == target_del)
                    )
                ]
                df_full_h.to_csv(FILE_DATA, index=False)
                st.warning(f"Version {target_del} supprimée.")
                st.rerun()

        if st.button("⬅️ RETOUR"):
            st.session_state.page = "MAIN_APP"
            st.rerun()

# --- 13. PAGE : PROGRESSION (TRI PRÉCIS DATE + HEURE) ---
elif st.session_state.page == "PROGRESS":
    import time

    FILE_DATA = "historique_complet.csv"
    FILE_DEP_EPARGNE = "depenses_epargne.csv"

    # Initialisation de la variable d'état pour la confirmation de suppression
    if "delete_confirm_idx" not in st.session_state:
        st.session_state.delete_confirm_idx = None

    if not os.path.exists(FILE_DEP_EPARGNE):
        pd.DataFrame(columns=["ID", "Utilisateur", "Raison", "Montant", "Date"]).to_csv(
            FILE_DEP_EPARGNE, index=False
        )

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
                st.title(
                    "📈 ANALYSE DE PROGRESSION 2"
                    if is_mode_2
                    else "📈 ANALYSE DE PROGRESSION 1"
                )

            df_p = pd.read_csv(FILE_DATA)
            data_user = df_p[
                df_p["Utilisateur"] == st.session_state.current_user
            ].copy()

            if not data_user.empty:
                # 1. Extraction de la base du mois (ex: JANVIER2024)
                data_user["Mois_Base"] = data_user["Mois"].str.split("Mod").str[0]

                # 2. CONVERSION PRÉCISE (Date + Heure)
                data_user["Date_Enregistrement"] = pd.to_datetime(
                    data_user["Date_Enregistrement"], dayfirst=True, errors="coerce"
                )
                data_user = data_user.dropna(subset=["Date_Enregistrement"])

                # 3. TRI CHRONOLOGIQUE PAR SECONDE
                data_user = data_user.sort_values(
                    by="Date_Enregistrement", ascending=True
                )

                # 4. FILTRAGE : On ne garde que la dernière version (keep='last')
                data_final = data_user.drop_duplicates(
                    subset=["Mois_Base", "Annee"], keep="last"
                )

                # --- 🟢 INTERFACE 1 : GRAPHIQUES ---
                if not is_mode_2:
                    import altair as alt

                    c_f1, c_f2, c_f3 = st.columns(3)
                    type_graph = c_f1.selectbox(
                        "Type de graphique", ["Courbe", "Barre", "Aire", "Points"]
                    )
                    periode = c_f2.selectbox(
                        "Période d'analyse", ["Par Mois", "Par Année"]
                    )
                    step_scale = c_f3.selectbox(
                        "Échelle (Palier)", [50, 100, 200, 500, 1000], index=4
                    )

                    # Préparation des données (on reset l'index pour Altair)
                    if periode == "Par Année":
                        df_plot = data_final.groupby("Annee")[["Epargne", "Total_Depenses"]].sum().reset_index()
                        x_col = "Annee"
                    else:
                        df_plot = data_final.copy().reset_index()
                        x_col = "Mois_Base"

                    # --- CALCUL RIGOUREUX DE L'ÉCHELLE FIXE (VOTRE LOGIQUE) ---
                    if not df_plot.empty:
                        val_max_absolue = df_plot[["Epargne", "Total_Depenses"]].max().max()
                        nb_paliers = int(val_max_absolue // step_scale) + 3
                        y_limit_fixe = nb_paliers * step_scale
                    else:
                        y_limit_fixe = 1000

                    st.write(f"### Évolution de l'Épargne ({periode})")

                    # Création du graphique principal avec l'axe Y bloqué à y_limit_fixe
                    base = alt.Chart(df_plot).encode(
                        x=alt.X(f"{x_col}:N", title=periode)
                    )

                    if type_graph == "Courbe":
                        chart = base.mark_line(color="#2e7d32", point=True)
                    elif type_graph == "Barre":
                        chart = base.mark_bar(color="#2e7d32")
                    elif type_graph == "Aire":
                        chart = base.mark_area(color="#2e7d32", opacity=0.5)
                    else:
                        chart = base.mark_point(color="#2e7d32", size=80)

                    # Application de l'échelle fixe de 0 à y_limit_fixe
                    final_chart = chart.encode(
                        y=alt.Y("Epargne:Q", scale=alt.Scale(domain=[0, y_limit_fixe]), title="Montant $")
                    ).properties(height=400)

                    st.altair_chart(final_chart, use_container_width=True)

                    st.write("### Comparaison Épargne vs Dépenses")
                    
                    # Graphique de comparaison groupé (fixe également)
                    comp_df = df_plot.melt(id_vars=[x_col], value_vars=["Epargne", "Total_Depenses"])
                    
                    comp_chart = alt.Chart(comp_df).mark_bar().encode(
                        x=alt.X("variable:N", title=None),
                        y=alt.Y("value:Q", scale=alt.Scale(domain=[0, y_limit_fixe]), title="Montant $"),
                        color=alt.Color("variable:N", scale=alt.Scale(range=["#2e7d32", "#1976d2"])),
                        column=alt.Column(f"{x_col}:N", title=periode)
                    ).properties(width=80, height=300)

                    st.altair_chart(comp_chart)
                    
                    st.write("---")

                    if st.button("🔒 VERROUILLER ET QUITTER", use_container_width=True):
                        st.session_state.prog_access_granted = False
                        st.session_state.page = "MAIN_APP"
                        st.rerun()
                # --- 🟠 INTERFACE 2 : GESTION DES DÉPENSES ---
                else:
                    total_ep_cumulee = data_final["Epargne"].astype(float).sum()
                    df_dep_file = pd.read_csv(FILE_DEP_EPARGNE)
                    user_deps = df_dep_file[
                        df_dep_file["Utilisateur"] == st.session_state.current_user
                    ].reset_index(drop=True)
                    total_sorties = user_deps["Montant"].sum()
                    solde_actuel = total_ep_cumulee - total_sorties

                    c1, c2 = st.columns(2)
                    with c1:
                        # MODIFICATION 1 : Couleur Bleu Foncé et texte Blanc
                        st.markdown(
                            f"""<div style="background-color:#0d47a1; color:white; padding:10px; border-radius:5px; border-left:5px solid #1565c0;">
                            <small>TOTAL ÉPARGNE CUMULÉE</small><br><span style="font-size:20px; font-weight:bold;">{total_ep_cumulee:,.2f} $</span></div>""",
                            unsafe_allow_html=True,
                        )
                    with c2:
                        # MODIFICATION 1 : Couleur Vert Foncé et texte Blanc
                        st.markdown(
                            f"""<div style="background-color:#1b5e20; color:white; padding:10px; border-radius:5px; border-left:5px solid #2e7d32;">
                            <small>SOLDE ACTUEL</small><br><span style="font-size:20px; font-weight:bold;">{solde_actuel:,.2f} $</span></div>""",
                            unsafe_allow_html=True,
                        )

                    st.write("")
                    if st.button(
                        "💸 ENREGISTRER UNE DÉPENSE SUR ÉPARGNE",
                        use_container_width=True,
                    ):
                        st.session_state.show_f = not st.session_state.get(
                            "show_f", False
                        )
                        # Réinitialiser la confirmation de suppression si on ouvre le formulaire
                        st.session_state.delete_confirm_idx = None
                        st.rerun()

                    if st.session_state.get("show_f"):
                        with st.form(
                            "form_dep_epargne",
                            clear_on_submit=st.session_state.get("form_success", False),
                        ):
                            st.subheader("Saisie du retrait")
                            f_rai = st.text_input(
                                "Raison", placeholder="Saisir le motif"
                            )
                            f_mon = st.number_input(
                                "Montant ($)", min_value=0.0, step=1.0
                            )
                            submit = st.form_submit_button("✅ CONFIRMER LE RETRAIT")

                            if submit:
                                if f_rai and f_mon > 0:
                                    if f_mon > solde_actuel:
                                        st.error(f"❌ Solde insuffisant")
                                        st.session_state.form_success = False
                                    else:
                                        st.session_state.form_success = True
                                        new_id = int(time.time())
                                        new_d = pd.DataFrame(
                                            [
                                                {
                                                    "ID": new_id,
                                                    "Utilisateur": st.session_state.current_user,
                                                    "Raison": f_rai,
                                                    "Montant": f_mon,
                                                    "Date": pd.Timestamp.now().strftime(
                                                        "%d/%m/%Y"
                                                    ),
                                                }
                                            ]
                                        )
                                        pd.concat(
                                            [df_dep_file, new_d], ignore_index=True
                                        ).to_csv(FILE_DEP_EPARGNE, index=False)
                                        st.success("Retrait enregistré.")
                                        time.sleep(1)
                                        st.rerun()
                                else:
                                    st.warning("Veuillez remplir tous les champs.")
                                    st.session_state.form_success = False

                    st.write("### 📂 Historique des retraits")
                    if not user_deps.empty:
                        list_display = [
                            f"{i + 1}. {r['Raison']} | {r['Montant']}$ | {r['Date']}"
                            for i, r in user_deps.iterrows()
                        ]
                        sel_idx = st.selectbox(
                            "Sélectionner un retrait",
                            range(len(list_display)),
                            format_func=lambda x: list_display[x],
                        )

                        # MODIFICATION 2 : Logique de confirmation de suppression

                        # Création de deux colonnes pour aligner les boutons de suppression
                        col_del1, col_del2 = st.columns([1, 1])

                        with col_del1:
                            # Bouton principal qui déclenche la phase de confirmation
                            if st.button(
                                "🗑️ SUPPRIMER CE RETRAIT", use_container_width=True
                            ):
                                # On mémorise l'index qu'on veut supprimer
                                st.session_state.delete_confirm_idx = sel_idx
                                st.rerun()  # Recharger pour afficher la case à cocher

                        # Zone d'action conditionnelle si un index est en attente de suppression
                        if st.session_state.get("delete_confirm_idx") == sel_idx:
                            with st.container(border=True):
                                st.warning(
                                    f"⚠️ Voulez-vous réellement supprimer le retrait n°{sel_idx + 1} ?"
                                )

                                # La case à cocher pour valider
                                confirm_check = st.checkbox(
                                    "Cocher pour VALIDER la suppression",
                                    key="check_del_val",
                                )

                                c_confirm_btn1, c_confirm_btn2 = st.columns(2)

                                with c_confirm_btn1:
                                    if confirm_check:
                                        # Le bouton de suppression finale n'apparaît que si la case est cochée
                                        if st.button(
                                            "❌ CONFIRMER DÉFINITIVEMENT",
                                            type="primary",
                                            use_container_width=True,
                                        ):
                                            real_id = user_deps.iloc[sel_idx]["ID"]
                                            df_dep_file = pd.read_csv(FILE_DEP_EPARGNE)
                                            df_dep_file = df_dep_file[
                                                df_dep_file["ID"] != real_id
                                            ]
                                            df_dep_file.to_csv(
                                                FILE_DEP_EPARGNE, index=False
                                            )

                                            # Réinitialisation des états
                                            st.session_state.delete_confirm_idx = None
                                            st.success("Retrait supprimé.")
                                            time.sleep(1)
                                            st.rerun()

                                with c_confirm_btn2:
                                    # Bouton d'annulation (équivalent à décocher)
                                    if st.button("↩️ ANNULER", use_container_width=True):
                                        st.session_state.delete_confirm_idx = None
                                        st.rerun()

                    else:
                        st.info("Aucun retrait effectué.")
            else:
                st.warning("Données insuffisantes.")
# --- 14. PAGE : VERIF USER ADM ---
elif st.session_state.page == "VERIF_USER_ADM":
    with st.container(border=True):
        st.subheader("Accès Modification Profil")
        u_check = st.text_input("Nom de l'utilisateur")
        p_check = st.text_input("Mot de Passe USER ADM", type="password")

        if st.button("VÉRIFIER LES DROITS"):
            df_c = pd.read_csv(FILE_CLIENTS, dtype=str)
            match = df_c[(df_c["name"] == u_check) & (df_c["pw_user_adm"] == p_check)]
            if not match.empty:
                st.session_state.temp_user = match.iloc[0].to_dict()
                st.session_state.page = "EDIT_PROFIL"
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
        if st.button("⬅️ RETOUR"):
            st.session_state.page = "ACCEUIL"
            st.rerun()

# --- 15. PAGE : EDIT PROFIL ---
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

        if st.button("💾 ENREGISTRER LES MODIFICATIONS"):
            # Vérification si des changements ont été apportés
            if (
                new_p1 == usr["pw_open_modify"]
                and new_p2 == usr["pw_adm_print_prog"]
                and new_p3 == usr["pw_user_adm"]
            ):
                st.info("Aucune modification n'a été effectuée.")
            else:
                # Procéder à la sauvegarde
                df_clients = pd.read_csv(FILE_CLIENTS, dtype=str)
                df_clients.loc[
                    df_clients["name"] == usr["name"],
                    ["pw_open_modify", "pw_adm_print_prog", "pw_user_adm"],
                ] = [new_p1, new_p2, new_p3]
                df_clients.to_csv(FILE_CLIENTS, index=False)

                # Mise à jour de l'état temporaire pour refléter les nouveaux changements
                st.session_state.temp_user.update(
                    {
                        "pw_open_modify": new_p1,
                        "pw_adm_print_prog": new_p2,
                        "pw_user_adm": new_p3,
                    }
                )

                st.success("Mise à jour réussie ! Cliquez sur RETOUR pour quitter.")
                # Note : On ne redirige plus ici, l'utilisateur reste sur la page.

        if st.button("⬅️ RETOUR"):
            st.session_state.page = "ACCEUIL"
            st.rerun()
