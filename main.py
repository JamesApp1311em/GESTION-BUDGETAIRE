import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Gestionnaire de Dépenses", layout="centered", initial_sidebar_state="expanded")

# --- STYLE CSS PERSONNALISÉ ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .st-emotion-cache-zq5wms {visibility: visible !important;}
            /* Désactiver le scroll excessif sur mobile */
            body { overscroll-behavior-y: contain; }
            html { overscroll-behavior-y: contain; }
            /* Personnalisation des conteneurs */
            div.stButton > button:first-child {
                border-radius: 8px;
            }
            .main-title {
                text-align: center;
                color: #1E88E5;
                font-family: 'Arial Black', sans-serif;
                margin-bottom: 20px;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 1. INITIALISATION DES BASES DE DONNÉES ---
FILE_CLIENTS = 'clients.csv'
FILE_DATA = 'historique_complet.csv'

def init_db():
    # Base des utilisateurs
    if not os.path.exists(FILE_CLIENTS) or os.stat(FILE_CLIENTS).st_size == 0:
        columns_clients = ['name', 'pw_open_modify', 'pw_adm_print_prog', 'pw_user_adm', 'status']
        pd.DataFrame(columns=columns_clients).to_csv(FILE_CLIENTS, index=False)
    
    # Base de l'historique des dépenses
    if not os.path.exists(FILE_DATA) or os.stat(FILE_DATA).st_size == 0:
        columns_data = [
            'Utilisateur', 'Mois', 'Annee', 'Revenu', 'Loyer', 'Scolarite', 
            'Ration', 'Dette', 'Poche', 'Assistance', 'Autres', 
            'Total_Depenses', 'Epargne', 'Date_Enregistrement'
        ]
        pd.DataFrame(columns=columns_data).to_csv(FILE_DATA, index=False)

init_db()

# --- 2. FONCTIONS TECHNIQUES ---

def create_pdf(row):
    """Génère le bulletin de paie au format PDF"""
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête
    pdf.set_font("Arial", "B", 16)
    pdf.set_fill_color(164, 198, 228)
    pdf.cell(190, 12, "BULLETIN DES DEPENSES MENSUELLES", 1, 1, 'C', True)
    
    # Période
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(45, 10, "PERIODE", 1, 0, 'L', True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(70, 10, f"{row['Mois']}", 1, 0, 'C')
    pdf.cell(75, 10, f"{row['Annee']}", 1, 1, 'C')
    
    # Revenu
    pdf.set_font("Arial", "B", 12)
    pdf.cell(45, 10, "REVENU MENSUEL($)", 1, 0, 'L', True)
    pdf.cell(10, 10, "$", 1, 0, 'C')
    pdf.set_font("Arial", "", 12)
    pdf.cell(100, 10, f"{float(row['Revenu']):,.2f}", 1, 0, 'R')
    pdf.cell(35, 10, "100%", 1, 1, 'C')
    
    # Détails des dépenses
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "DETAIL DES DEPENSES ($)", 1, 1, 'C', True)
    
    rev = float(row['Revenu']) if float(row['Revenu']) > 0 else 1
    items = [
        ("LOYER", row['Loyer']),
        ("SCOLARITE", row['Scolarite']),
        ("RATION", row['Ration']),
        ("DETTE", row['Dette']),
        ("ARGENT DE POCHE", row['Poche']),
        ("ASSISTANCE", row['Assistance']),
        ("AUTRES DEPENSES", row['Autres'])
    ]
    
    pdf.set_font("Arial", "", 11)
    for label, val in items:
        perc = (float(val)/rev)*100
        pdf.cell(45, 9, label, 1, 0, 'L')
        pdf.cell(10, 9, "$", 1, 0, 'C')
        pdf.cell(100, 9, f"{float(val):,.2f}", 1, 0, 'R')
        pdf.cell(35, 9, f"{perc:.1f}%", 1, 1, 'C')
    
    # Totaux
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    
    pdf.cell(45, 10, "TOTAL DEPENSES", 1, 0, 'L', True)
    pdf.cell(10, 10, "$", 1, 0, 'C')
    pdf.cell(100, 10, f"{float(row['Total_Depenses']):,.2f}", 1, 0, 'R')
    pdf.cell(35, 10, f"{(float(row['Total_Depenses'])/rev)*100:.1f}%", 1, 1, 'C')
    
    pdf.cell(45, 10, "EPARGNE", 1, 0, 'L', True)
    pdf.cell(10, 10, "$", 1, 0, 'C')
    pdf.cell(100, 10, f"{float(row['Epargne']):,.2f}", 1, 0, 'R')
    pdf.cell(35, 10, f"{(float(row['Epargne'])/rev)*100:.1f}%", 1, 1, 'C')
    
    # Observation
    obs = "GOOD" if float(row['Epargne']) > 0 else "BAD"
    pdf.ln(5)
    pdf.cell(45, 10, "OBSERVATION", 1, 0, 'L', True)
    if obs == "GOOD":
        pdf.set_fill_color(144, 238, 144) # Vert
    else:
        pdf.set_fill_color(255, 99, 71)   # Rouge
    pdf.cell(145, 10, obs, 1, 1, 'C', True)
    
    # Pied de page
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(190, 5, f"Document généré le {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'R')
    
    return pdf.output()

# --- 3. GESTION DU SESSION STATE (MÉMOIRE DE L'APP) ---
if 'page' not in st.session_state: st.session_state.page = "ACCEUIL"
if 'inputs_locked' not in st.session_state: st.session_state.inputs_locked = True 
if 'confirm_exit' not in st.session_state: st.session_state.confirm_exit = False
if 'show_extend_table' not in st.session_state: st.session_state.show_extend_table = False
if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'show_menu' not in st.session_state: st.session_state.show_menu = False
if 'access_admin_granted' not in st.session_state:
    st.session_state.access_admin_granted = False
if 'access_print_granted' not in st.session_state:
    st.session_state.access_print_granted = False
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
    with st.container(border=True):
        st.markdown("<h1 class='main-title'>🔐 ACCÈS AU SYSTÈME</h1>", unsafe_allow_html=True)
        u_n = st.text_input("USER NAME", placeholder="Entrez votre nom...")
        u_p = st.text_input("PASSWORD (OPEN APP / MODIFY)", type="password")
        
        if st.button("🚀 OPEN APP", use_container_width=True):
            df = pd.read_csv(FILE_CLIENTS, dtype=str).fillna("")
            user_match = df[df['name'].str.strip() == str(u_n).strip()]
            
            if not user_match.empty and user_match.iloc[0]['pw_open_modify'] == str(u_p).strip():
                if user_match.iloc[0]['status'].lower() in ['true', 'active']:
                    st.session_state.update({
                        'current_user': u_n,
                        'user_pw_open': str(u_p).strip(),
                        'user_pw_adm_extra': user_match.iloc[0]['pw_adm_print_prog'],
                        'page': "MAIN_APP"
                    })
                    st.rerun()
                else:
                    st.error("⚠️ Votre compte est bloqué. Contactez l'administrateur.")
            else:
                st.error("❌ Nom d'utilisateur ou mot de passe incorrect.")

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

        # Le bouton "QUITTER L'APP" a été supprimé ici.
        st.write("---")

# --- 6. PAGE : LOGIN (CRÉATION DE COMPTE) ---
elif st.session_state.page == "LOGIN":
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center;'>⚙️ CRÉATION DE NOUVEAU COMPTE</h2>", unsafe_allow_html=True)
        st.info("Veuillez définir vos informations d'identification selon la nomenclature du système.")
        
        new_n = st.text_input("USER NAME")
        new_p1 = st.text_input("PASSWORD (OPEN APP / MODIFY)", type="password")
        new_p2 = st.text_input("PASSWORD (ADM / PRINT / PROGRESS)", type="password")
        new_p3 = st.text_input("PASSWORD (USER ADM)", type="password")
        
        if st.button("💾 ENREGISTRER L'UTILISATEUR", use_container_width=True, type="primary"):
            if new_n and new_p1 and new_p2 and new_p3:
                df_clients = pd.read_csv(FILE_CLIENTS, dtype=str)
                if new_n in df_clients['name'].values:
                    st.error("Ce nom d'utilisateur existe déjà.")
                else:
                    new_entry = {
                        'name': new_n, 
                        'pw_open_modify': new_p1, 
                        'pw_adm_print_prog': new_p2, 
                        'pw_user_adm': new_p3, 
                        'status': "Active"
                    }
                    pd.concat([df_clients, pd.DataFrame([new_entry])], ignore_index=True).to_csv(FILE_CLIENTS, index=False)
                    st.success(f"Compte pour '{new_n}' créé avec succès !")
                    st.session_state.page = "ACCEUIL"
                    st.rerun()
            else:
                st.warning("Veuillez remplir tous les champs obligatoires.")
        
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
        st.markdown("<h2 style='text-align: center;'>🖥️ ADMINISTRATION GÉNÉRALE</h2>", unsafe_allow_html=True)
        st.write("Gestion des comptes utilisateurs et accès système.")
        
        # --- LOGIQUE EXTEND ---
        if st.button("📂 EXTEND", use_container_width=True):
            st.session_state.show_extend_table = not st.session_state.show_extend_table
        
        if st.session_state.show_extend_table:
            st.write("### Base de données complète des utilisateurs")
            df_full = pd.read_csv(FILE_CLIENTS, dtype=str)
            st.dataframe(df_full, use_container_width=True)
            st.write("---")

        st.subheader("Liste des comptes et Status")
        df_adm = pd.read_csv(FILE_CLIENTS, dtype=str).fillna("")
        
        for idx, row in df_adm.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"👤 **{row['name']}**")
                
                is_active = row['status'].lower() in ['true', 'active']
                status_label = "ACTIVE" if is_active else "BLOCKED"
                
                if c2.checkbox(f"Statut: {status_label}", value=is_active, key=f"chk_{idx}") != is_active:
                    df_adm.at[idx, 'status'] = "Active" if not is_active else "Blocked"
                    df_adm.to_csv(FILE_CLIENTS, index=False)
                    st.rerun()
                
                if c3.button("🗑️", key=f"btn_del_{idx}"):
                    df_adm.drop(idx).to_csv(FILE_CLIENTS, index=False)
                    st.rerun()
        
        if st.button("⬅️ QUITTER L'ADMINISTRATION", use_container_width=True):
            st.session_state.page = "ACCEUIL"
            st.rerun()

# --- 9. PAGE : MAIN APP (APPLICATION PRINCIPALE) ---
elif st.session_state.page == "MAIN_APP":
    df_h = pd.read_csv(FILE_DATA)
    user_recs = df_h[df_h['Utilisateur'] == st.session_state.current_user]
    
    # --- BOUTON DE CONTRÔLE (MENU / RETOUR) ---
    if not st.session_state.show_menu:
        if st.button("➡️ OUVRIR LE MENU"):
            st.session_state.show_menu = True
            st.rerun()
    else:
        if st.button("⬅️ RETOUR AU BULLETIN"):
            st.session_state.show_menu = False
            st.rerun()

    st.write("---")

# --- LOGIQUE D'AFFICHAGE EXCLUSIF ---
    if st.session_state.show_menu:
        # --- TOUT CE BLOC EST MAINTENANT DÉCALÉ À DROITE ---
        st.markdown("<h2 style='color: #1E88E5;'>📋 MENU DE GESTION</h2>", unsafe_allow_html=True)
        st.info(f"Utilisateur connecté : {st.session_state.current_user}")

        col1, col2 = st.columns(2)

        # --- COLONNE 1 : SÉLECTION DU MOIS ---
        with col1:
            if st.button("📅 SELECT MONTH", use_container_width=True):
                st.session_state.show_date_picker = not st.session_state.get('show_date_picker', False)
            
            if st.session_state.get('show_date_picker'):
                with st.container(border=True):
                    m_list = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
                    m_c = st.selectbox("Mois", m_list)
                    a_c = st.selectbox("Année", [str(a) for a in range(2024, 2036)])
                    versions = user_recs[(user_recs['Mois'].str.startswith(m_c)) & (user_recs['Annee'].astype(str) == a_c)]
                    v_choisie = st.selectbox("Versions", versions['Mois'].tolist()) if not versions.empty and len(versions) > 1 else m_c
                    
                    if st.button("✅ CONFIRMER"):
                        st.session_state.update({'sel_mois_base': m_c, 'sel_annee': a_c, 'show_date_picker': False, 'show_menu': False})
                        if not versions.empty:
                            target = versions[versions['Mois'] == v_choisie].iloc[0]
                            st.session_state.update({
                                'sel_mois_affiche': target['Mois'], 'n_rev': target['Revenu'], 
                                'n_loy': target['Loyer'], 'n_sco': target['Scolarite'], 
                                'n_rat': target['Ration'], 'n_det': target['Dette'], 
                                'n_poc': target['Poche'], 'n_ast': target['Assistance'], 
                                'n_aut': target['Autres'], 'inputs_locked': True
                            })
                        else:
                            st.session_state.update({'sel_mois_affiche': m_c, 'inputs_locked': False})
                            for k in ["n_rev", "n_loy", "n_sco", "n_rat", "n_det", "n_poc", "n_ast", "n_aut"]: st.session_state[k] = 0
                        st.rerun()

        # --- COLONNE 2 : PRINT PROTÉGÉ ---
        with col2:
            if st.button("🖨️ PRINT (BULLETIN)", use_container_width=True):
                st.session_state.show_print_pwd = not st.session_state.get('show_print_pwd', False)
                st.session_state.show_print_ui = False

            if st.session_state.get('show_print_pwd'):
                with st.container(border=True):
                    pwd_p = st.text_input("Code Print", type="password", key="p_print")
                    if st.button("🔓 OK PRINT"):
                        if pwd_p == st.session_state.get('user_pw_adm_extra'):
                            st.session_state.show_print_ui = True
                            st.session_state.show_print_pwd = False
                        else:
                            st.error("Code incorrect")

            if st.session_state.get('show_print_ui'):
                with st.container(border=True):
                    choix_pdf = st.selectbox("Version à imprimer", user_recs['Mois'].tolist()) if not user_recs.empty else None
                    if choix_pdf:
                        pdf_bytes = create_pdf(user_recs[user_recs['Mois'] == choix_pdf].iloc[0])
                        st.download_button("📥 Télécharger", pdf_bytes, f"Bulletin_{choix_pdf}.pdf", "application/pdf")

        st.write("---")

        # --- BOUTONS DU BAS ---
        c_adm, c_prog, c_deco = st.columns(3)

        # Admin Data
        if c_adm.button("🛡️ ADMIN DATA", use_container_width=True):
            st.session_state.show_admin_pwd = not st.session_state.get('show_admin_pwd', False)

        if st.session_state.get('show_admin_pwd'):
            with st.container(border=True):
                pwd_a = st.text_input("Code Admin", type="password", key="p_admin")
                if st.button("🔓 OK ADMIN"):
                    if pwd_a == st.session_state.get('user_pw_adm_extra'):
                        st.session_state.page = "VIEW_BASE"
                        st.rerun()
                    else:
                        st.error("Code incorrect")

        # Progression
        if c_prog.button("📈 PROGRESSION", use_container_width=True):
            st.session_state.page = "PROGRESS"
            st.rerun()

        # Déconnexion
        if c_deco.button("🟦 DÉCONNEXION", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    else:
        # --- INTERFACE 2 : LE BULLETIN DE DÉPENSES ---
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #2E7D32;'>💰 BULLETIN DES DEPENSES</h1>", unsafe_allow_html=True)
            
            sel_m_base = st.session_state.get('sel_mois_base')
            L = st.session_state.inputs_locked

            # --- Gestion du déverrouillage Intelligente ---
            sel_m_base = st.session_state.get('sel_mois_base')
            L = st.session_state.inputs_locked

            if sel_m_base and L:
                # 1. On récupère toutes les versions existantes pour ce mois/année
                # user_recs a déjà été filtré par utilisateur au début de la page
                versions_du_mois = user_recs[
                    (user_recs['Mois'].str.startswith(sel_m_base)) & 
                    (user_recs['Annee'].astype(str) == st.session_state.get('sel_annee'))
                ]

                # 2. On détermine quelle est la version la plus récente (le nombre de "Mod")
                # Si vide, c'est une nouvelle saisie, donc on peut modifier.
                if not versions_du_mois.empty:
                    # On cherche le nombre maximum après "Mod"
                    def extraire_version(nom_mois):
                        if "Mod" in nom_mois:
                            try:
                                return int(nom_mois.split("Mod")[-1])
                            except:
                                return 0
                        return 0

                    max_version_nombre = versions_du_mois['Mois'].apply(extraire_version).max()
                    current_version_nom = st.session_state.get('sel_mois_affiche', '')
                    current_version_nombre = extraire_version(current_version_nom)

                    # 3. Comparaison : On n'affiche le bouton que si c'est la version MAX
                    if current_version_nombre == max_version_nombre:
                        if st.button("📝 MODIFIER LA DERNIÈRE VERSION", use_container_width=True):
                            st.session_state.inputs_locked = False
                            st.rerun()
                    else:
                        st.warning(f"⚠️ Lecture seule : Une version plus récente existe (Mod {max_version_nombre}).")
                else:
                    # Si aucune donnée n'existe encore pour ce mois, on peut modifier
                    if st.button("📝 MODIFIER LES DONNÉES", use_container_width=True):
                        st.session_state.inputs_locked = False
                        st.rerun()

            col_m, col_a = st.columns(2)
            col_m.text_input("MOIS EN COURS", value=st.session_state.get('sel_mois_affiche',''), disabled=True)
            col_a.text_input("ANNÉE", value=st.session_state.get('sel_annee',''), disabled=True)
            
            st.write("### Entrées financières")
            st.session_state.n_rev = st.number_input("REVENU GLOBAL ($)", value=int(st.session_state.get('n_rev',0)), disabled=L)
            
            st.write("### Les dépenses")
            c1, c2 = st.columns(2)
            st.session_state.n_loy = c1.number_input("LOYER", value=int(st.session_state.get('n_loy',0)), disabled=L)
            st.session_state.n_sco = c1.number_input("SCOLARITÉ", value=int(st.session_state.get('n_sco',0)), disabled=L)
            st.session_state.n_rat = c1.number_input("RATION", value=int(st.session_state.get('n_rat',0)), disabled=L)
            st.session_state.n_det = c2.number_input("DETTES", value=int(st.session_state.get('n_det',0)), disabled=L)
            st.session_state.n_poc = c2.number_input("POCHE", value=int(st.session_state.get('n_poc',0)), disabled=L)
            st.session_state.n_ast = c2.number_input("ASSISTANCE", value=int(st.session_state.get('n_ast',0)), disabled=L)
            
            st.session_state.n_aut = st.number_input("AUTRES", value=int(st.session_state.get('n_aut',0)), disabled=L)
            
            if st.button("🚀 CALCULER", use_container_width=True, type="primary"):
                if not st.session_state.get('sel_mois_base'):
                    st.warning("Veuillez d'abord sélectionner un mois dans le MENU.")
                else:
                    st.session_state.total_dep = sum([
                        st.session_state.n_loy, st.session_state.n_sco, st.session_state.n_rat, 
                        st.session_state.n_det, st.session_state.n_poc, st.session_state.n_ast, 
                        st.session_state.n_aut
                    ])
                    st.session_state.epargne = st.session_state.n_rev - st.session_state.total_dep
                    st.session_state.page = 'RESULTATS'
                    st.rerun()
# --- 10. PAGE : RÉSULTATS ---
elif st.session_state.page == "RESULTATS":
    with st.container(border=True):
        st.markdown(f"<h2 style='text-align: center;'>📊 BILAN : {st.session_state.get('sel_mois_affiche', 'Non sélectionné')}</h2>", unsafe_allow_html=True)
        
        rev = st.session_state.n_rev if st.session_state.n_rev > 0 else 1
        ratio_epargne = (st.session_state.epargne / rev) * 100
        
        col_res1, col_res2 = st.columns(2)
        col_res1.metric("TOTAL DÉPENSES", f"{st.session_state.total_dep} $")
        col_res2.metric("ÉPARGNE NETTE", f"{st.session_state.epargne} $", delta=f"{ratio_epargne:.1f}%")
        
        if st.session_state.epargne >= 0:
            st.success(f"Félicitations ! Vous avez une épargne positive de {ratio_epargne:.1f}% de votre revenu.")
        else:
            st.error(f"Attention ! Vous êtes en déficit de {abs(st.session_state.epargne)} $.")
            
        if st.button("💾 SAUVEGARDER CETTE VERSION", use_container_width=True):
            df_hist = pd.read_csv(FILE_DATA)
            
            # 1. On prépare les données actuelles pour la comparaison
            # On convertit tout en float/str pour éviter les problèmes de type lors du check
            current_vals = {
                'Utilisateur': st.session_state.current_user,
                'Annee': str(st.session_state.sel_annee),
                'Revenu': float(st.session_state.n_rev),
                'Loyer': float(st.session_state.n_loy),
                'Scolarite': float(st.session_state.n_sco),
                'Ration': float(st.session_state.n_rat),
                'Dette': float(st.session_state.n_det),
                'Poche': float(st.session_state.n_poc),
                'Assistance': float(st.session_state.n_ast),
                'Autres': float(st.session_state.n_aut)
            }

            # 2. On vérifie s'il existe une ligne identique dans l'historique
            # (On ne vérifie pas la colonne 'Mois' car elle peut s'appeler 'Janvier' ou 'JanvierMod1')
            doublon = df_hist[
                (df_hist['Utilisateur'] == current_vals['Utilisateur']) &
                (df_hist['Annee'].astype(str) == current_vals['Annee']) &
                (df_hist['Revenu'].astype(float) == current_vals['Revenu']) &
                (df_hist['Loyer'].astype(float) == current_vals['Loyer']) &
                (df_hist['Scolarite'].astype(float) == current_vals['Scolarite']) &
                (df_hist['Ration'].astype(float) == current_vals['Ration']) &
                (df_hist['Dette'].astype(float) == current_vals['Dette']) &
                (df_hist['Poche'].astype(float) == current_vals['Poche']) &
                (df_hist['Assistance'].astype(float) == current_vals['Assistance']) &
                (df_hist['Autres'].astype(float) == current_vals['Autres'])
            ]

            if not doublon.empty:
                st.warning("⚠️ Une version ayant les mêmes données existe déjà dans votre Historique de Base de données.")
            else:
                # 3. Si pas de doublon, on gère le nom de la version (Mod1, Mod2...)
                exist = df_hist[
                    (df_hist['Utilisateur'] == st.session_state.current_user) & 
                    (df_hist['Mois'].str.startswith(st.session_state.sel_mois_base)) & 
                    (df_hist['Annee'].astype(str) == st.session_state.sel_annee)
                ]
                
                nom_version = f"{st.session_state.sel_mois_base}Mod{len(exist)}" if not exist.empty else st.session_state.sel_mois_base
                
                new_data = {
                    'Utilisateur': st.session_state.current_user, 
                    'Mois': nom_version, 
                    'Annee': st.session_state.sel_annee, 
                    'Revenu': st.session_state.n_rev, 
                    'Loyer': st.session_state.n_loy, 
                    'Scolarite': st.session_state.n_sco, 
                    'Ration': st.session_state.n_rat, 
                    'Dette': st.session_state.n_det, 
                    'Poche': st.session_state.n_poc, 
                    'Assistance': st.session_state.n_ast, 
                    'Autres': st.session_state.n_aut, 
                    'Total_Depenses': st.session_state.total_dep, 
                    'Epargne': st.session_state.epargne, 
                    'Date_Enregistrement': pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')
                }
                
                pd.concat([df_hist, pd.DataFrame([new_data])], ignore_index=True).to_csv(FILE_DATA, index=False)
                st.success(f"✅ Version '{nom_version}' archivée avec succès !")
                st.session_state.page = "MAIN_APP"
                st.rerun()
                
        if st.button("⬅️ RETOUR"):
            st.session_state.page = "MAIN_APP"
            st.rerun()
# --- 11. PAGE : VIEW BASE (ACCÈS COMPLET AUX DONNÉES) ---
elif st.session_state.page == "VIEW_BASE":
    with st.container(border=True):
        st.title("🔓 GESTION DE L'HISTORIQUE")
        df_full_h = pd.read_csv(FILE_DATA)
        user_data = df_full_h[df_full_h['Utilisateur'] == st.session_state.current_user]
        
        st.write(f"Enregistrements pour : {st.session_state.current_user}")
        st.dataframe(user_data, use_container_width=True)
        
        st.write("---")
        st.subheader("Supprimer une entrée")
        target_del = st.selectbox("Sélectionner la version à effacer", ["---"] + user_data['Mois'].tolist())
        
        if target_del != "---":
            if st.button("🗑️ CONFIRMER LA SUPPRESSION", type="secondary"):
                df_full_h = df_full_h[~((df_full_h['Utilisateur'] == st.session_state.current_user) & (df_full_h['Mois'] == target_del))]
                df_full_h.to_csv(FILE_DATA, index=False)
                st.warning(f"Version {target_del} supprimée.")
                st.rerun()
        
        if st.button("⬅️ RETOUR"):
            st.session_state.page = "MAIN_APP"
            st.rerun()

# --- 12. PAGE : PROGRESSION (CODE FINAL CORRIGÉ) ---
elif st.session_state.page == "PROGRESS":
    FILE_DATA = 'historique_complet.csv'
    FILE_DEP_EPARGNE = 'depenses_epargne.csv'
    
    # Initialisation du fichier de dépenses si absent
    if not os.path.exists(FILE_DEP_EPARGNE):
        pd.DataFrame(columns=['ID', 'Utilisateur', 'Raison', 'Montant', 'Date']).to_csv(FILE_DEP_EPARGNE, index=False)

    with st.container(border=True):
        # --- ÉTAPE 1 : ACCÈS SÉCURISÉ ---
        if not st.session_state.get('prog_access_granted', False):
            st.title("📈 ANALYSE DE PROGRESSION")
            st.info("Cette section est sécurisée. Veuillez entrer votre code d'accès.")
            pwd_input = st.text_input("PASSWORD", type="password")
            
            if st.button("🔓 VALIDER L'ACCÈS", use_container_width=True):
                if pwd_input == st.session_state.get('user_pw_adm_extra'):
                    st.session_state.prog_access_granted = True
                    st.session_state.mode_prog2 = False
                    st.rerun()
                else:
                    st.error("Code incorrect.")
            
            if st.button("⬅️ RETOUR"):
                st.session_state.page = "MAIN_APP"
                st.rerun()
        
        # --- ÉTAPE 2 : LOGIQUE APRÈS VALIDATION ---
        else:
            # Navigation dynamique
            col_nav_titre, col_nav_btn = st.columns([2, 1])
            with col_nav_btn:
                label_nav = "📈 1st FONCTION" if st.session_state.get('mode_prog2') else "🔄 2nd FONCTION"
                if st.button(label_nav, use_container_width=True):
                    st.session_state.mode_prog2 = not st.session_state.get('mode_prog2', False)
                    st.rerun()

            with col_nav_titre:
                titre_final = "📈 ANALYSE DE PROGRESSION 2" if st.session_state.get('mode_prog2') else "📈 ANALYSE DE PROGRESSION 1"
                st.title(titre_final)

            # Lecture des données
            df_p = pd.read_csv(FILE_DATA)
            data_user = df_p[df_p['Utilisateur'] == st.session_state.current_user].copy()
            
            if not data_user.empty:
                # Filtrage : Dernière version par mois
                data_user['Mois_Base'] = data_user['Mois'].apply(lambda x: x.split('Mod')[0])
                data_user['Date_Enregistrement'] = pd.to_datetime(data_user['Date_Enregistrement'], dayfirst=True)
                data_final = data_user.sort_values('Date_Enregistrement').drop_duplicates(subset=['Mois_Base', 'Annee'], keep='last')

                if not st.session_state.get('mode_prog2'):
                # --- INTERFACE 1 (GRAPHES VISIBLES MÊME AVEC UN SEUL MOIS) ---
                 if not st.session_state.get('mode_prog2'):
                    st.write("### Évolution de l'épargne")
                    
                    # On prépare les données indexées
                    chart_data = data_final.set_index('Mois')['Epargne']
                    
                    # Astuce : Si on n'a qu'un seul mois, on utilise un Bar Chart 
                    # pour que ce soit bien visible. Sinon, un Area Chart.
                    if len(data_final) <= 1:
                        st.bar_chart(chart_data, color="#2e7d32")
                        st.info("Note : La courbe se dessinera automatiquement dès le deuxième mois.")
                    else:
                        st.area_chart(chart_data, color="#2e7d32")
                    
                    st.write("### Revenu vs Dépenses")
                    st.bar_chart(data_final.set_index('Mois')[['Revenu', 'Total_Depenses']])
                    
                    if st.button("🔒 VERROUILLER ET QUITTER", use_container_width=True):
                        st.session_state.prog_access_granted = False
                        st.session_state.page = "MAIN_APP"
                        st.rerun()
                    # --- INTERFACE 2 (GESTION & SÉCURITÉ) ---
                    # Calculs des montants
                    total_ep_cumulee = data_final['Epargne'].astype(float).sum()
                    df_dep_file = pd.read_csv(FILE_DEP_EPARGNE)
                    user_deps = df_dep_file[df_dep_file['Utilisateur'] == st.session_state.current_user]
                    total_sorties = user_deps['Montant'].sum()
                    solde_actuel = total_ep_cumulee - total_sorties

                    # Affichage réduit des totaux
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"""<div style="background-color:#f1f8e9; padding:10px; border-radius:5px; border-left:5px solid #4caf50;">
                            <small>TOTAL ÉPARGNE CUMULÉE</small><br><span style="font-size:18px; font-weight:bold;">{total_ep_cumulee:,.2f} $</span></div>""", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"""<div style="background-color:#fff3e0; padding:10px; border-radius:5px; border-left:5px solid #ff9800;">
                            <small>SOLDE ACTUEL</small><br><span style="font-size:18px; font-weight:bold;">{solde_actuel:,.2f} $</span></div>""", unsafe_allow_html=True)

                    st.write("")
                    if st.button("💸 DÉPENSES SUR L'ÉPARGNE", use_container_width=True):
                        st.session_state.show_f = not st.session_state.get('show_f', False)
                        st.rerun()

                    if st.session_state.get('show_f'):
                        with st.form("form_secu_dep"):
                            st.subheader("ENTRÉE VOS DÉPENSES ET RAISONS")
                            f_rai = st.text_input("Raison")
                            f_mon = st.number_input("Montant ($)", min_value=0.0)
                            
                            if st.form_submit_button("✅ VALIDER"):
                                if f_mon > solde_actuel:
                                    st.error(f"❌ SOLDE INSUFFISANT ! (Disponible: {solde_actuel:,.2f} $)")
                                elif f_rai and f_mon > 0:
                                    new_d = pd.DataFrame([{'ID': len(df_dep_file)+1, 'Utilisateur': st.session_state.current_user, 
                                                           'Raison': f_rai, 'Montant': f_mon, 
                                                           'Date': pd.Timestamp.now().strftime('%d/%m/%Y')}])
                                    pd.concat([df_dep_file, new_d], ignore_index=True).to_csv(FILE_DEP_EPARGNE, index=False)
                                    st.success("Dépense enregistrée.")
                                    st.rerun()

                    # Récapitulatif avec Liste Déroulante
                    st.write("### 📂 Récapitulatif")
                    if not user_deps.empty:
                        list_options = [f"ID:{r['ID']} | {r['Raison']} | {r['Montant']}$" for i, r in user_deps.iterrows()]
                        selection = st.selectbox("Sélectionner une dépense", list_options)
                        
                        if st.button("🗑️ SUPPRIMER LA SÉLECTION"):
                            sel_id = int(selection.split(" | ")[0].split(":")[1])
                            df_dep_file = df_dep_file[~((df_dep_file['ID'] == sel_id) & (df_dep_file['Utilisateur'] == st.session_state.current_user))]
                            df_dep_file.to_csv(FILE_DEP_EPARGNE, index=False)
                            st.rerun()
                    else:
                        st.info("Aucune dépense enregistrée.")
            else:
                st.info("Données insuffisantes.")

# --- 13. PAGE : VERIF USER ADM ---
elif st.session_state.page == "VERIF_USER_ADM":
    with st.container(border=True):
        st.subheader("Accès Modification Profil")
        u_check = st.text_input("Nom de l'utilisateur")
        p_check = st.text_input("Mot de Passe USER ADM", type="password")
        
        if st.button("VÉRIFIER LES DROITS"):
            df_c = pd.read_csv(FILE_CLIENTS, dtype=str)
            match = df_c[(df_c['name'] == u_check) & (df_c['pw_user_adm'] == p_check)]
            if not match.empty:
                st.session_state.temp_user = match.iloc[0].to_dict()
                st.session_state.page = "EDIT_PROFIL"
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
        if st.button("⬅️ RETOUR"):
            st.session_state.page = "ACCEUIL"
            st.rerun()

# --- 14. PAGE : EDIT PROFIL ---
elif st.session_state.page == "EDIT_PROFIL":
    with st.container(border=True):
        st.title("✏️ MODIFICATION DES CODES")
        usr = st.session_state.temp_user
        st.write(f"Utilisateur : **{usr['name']}**")
        
        new_p1 = st.text_input("NOUVEAU PW (OPEN/MODIFY)", value=usr['pw_open_modify'])
        new_p2 = st.text_input("NOUVEAU PW (ADM/PRINT/PROG)", value=usr['pw_adm_print_prog'])
        new_p3 = st.text_input("NOUVEAU PW (USER ADM)", value=usr['pw_user_adm'])
        
        if st.button("💾 ENREGISTRER LES MODIFICATIONS"):
            # Vérification si des changements ont été apportés
            if (new_p1 == usr['pw_open_modify'] and 
                new_p2 == usr['pw_adm_print_prog'] and 
                new_p3 == usr['pw_user_adm']):
                
                st.info("Aucune modification n'a été effectuée.")
            else:
                # Procéder à la sauvegarde
                df_clients = pd.read_csv(FILE_CLIENTS, dtype=str)
                df_clients.loc[df_clients['name'] == usr['name'], ['pw_open_modify','pw_adm_print_prog','pw_user_adm']] = [new_p1, new_p2, new_p3]
                df_clients.to_csv(FILE_CLIENTS, index=False)
                
                # Mise à jour de l'état temporaire pour refléter les nouveaux changements
                st.session_state.temp_user.update({
                    'pw_open_modify': new_p1,
                    'pw_adm_print_prog': new_p2,
                    'pw_user_adm': new_p3
                })
                
                st.success("Mise à jour réussie ! Cliquez sur RETOUR pour quitter.")
                # Note : On ne redirige plus ici, l'utilisateur reste sur la page.
                
        if st.button("⬅️ RETOUR"):
            st.session_state.page = "ACCEUIL"
            st.rerun()