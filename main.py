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
    
    return bytes(pdf.output(dest='S'))

# --- 3. GESTION DU SESSION STATE (MÉMOIRE DE L'APP) ---
if 'page' not in st.session_state: st.session_state.page = "ACCEUIL"
if 'inputs_locked' not in st.session_state: st.session_state.inputs_locked = True 
if 'confirm_exit' not in st.session_state: st.session_state.confirm_exit = False
if 'show_extend_table' not in st.session_state: st.session_state.show_extend_table = False
if 'current_user' not in st.session_state: st.session_state.current_user = None

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

        st.write("---")
        if st.button("❌ QUITTER L'APP", use_container_width=True):
            st.session_state.confirm_exit = True
            st.rerun()

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
    
    # --- BARRE LATÉRALE (SIDEBAR) ---
    with st.sidebar:
        st.markdown(f"<h2 style='color:#1E88E5;'>👤 {st.session_state.current_user}</h2>", unsafe_allow_html=True)
        st.write("---")
        
        # SÉLECTION DU MOIS
        if st.button("📅 SELECT MONTH", use_container_width=True):
            st.session_state.show_date_picker = not st.session_state.get('show_date_picker', False)
        
        if st.session_state.get('show_date_picker'):
            with st.container(border=True):
                m_list = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
                m_c = st.selectbox("Mois", m_list)
                a_c = st.selectbox("Année", [str(a) for a in range(2024, 2036)])
                
                # Filtrer les versions existantes
                versions = user_recs[(user_recs['Mois'].str.startswith(m_c)) & (user_recs['Annee'].astype(str) == a_c)]
                v_choisie = st.selectbox("Versions disponibles", versions['Mois'].tolist()) if not versions.empty and len(versions) > 1 else m_c
                
                if st.button("✅ CONFIRMER"):
                    st.session_state.update({'sel_mois_base': m_c, 'sel_annee': a_c, 'show_date_picker': False})
                    if not versions.empty:
                        target = versions[versions['Mois'] == v_choisie].iloc[0]
                        st.session_state.update({
                            'sel_mois_affiche': target['Mois'],
                            'n_rev': target['Revenu'], 'n_loy': target['Loyer'],
                            'n_sco': target['Scolarite'], 'n_rat': target['Ration'],
                            'n_det': target['Dette'], 'n_poc': target['Poche'],
                            'n_ast': target['Assistance'], 'n_aut': target['Autres'],
                            'inputs_locked': True, 'last_version_name': versions.iloc[-1]['Mois']
                        })
                    else:
                        st.session_state.update({'sel_mois_affiche': m_c, 'inputs_locked': False, 'last_version_name': m_c})
                        for k in ["n_rev", "n_loy", "n_sco", "n_rat", "n_det", "n_poc", "n_ast", "n_aut"]: st.session_state[k] = 0
                    st.rerun()
        
        # ADMINISTRATION ACCÈS DONNÉES
        if st.button("🛡️ ADM (DATA ACCESS)", use_container_width=True):
            st.session_state.ask_adm_main = not st.session_state.get('ask_adm_main', False)
        
        if st.session_state.get('ask_adm_main'):
            p_adm = st.text_input("Code ADM / PRINT", type="password")
            if st.button("Valider"):
                if str(p_adm).strip() == st.session_state.user_pw_adm_extra:
                    st.session_state.page = "VIEW_BASE"
                    st.rerun()
                else:
                    st.error("Accès refusé.")
        
        # IMPRESSION PDF
        if st.button("🖨️ PRINT (BULLETIN)", use_container_width=True):
            st.session_state.show_print_ui = not st.session_state.get('show_print_ui', False)
        
        if st.session_state.get('show_print_ui'):
            choix_pdf = st.selectbox("Choisir une version", user_recs['Mois'].tolist()) if not user_recs.empty else None
            if choix_pdf:
                pdf_bytes = create_pdf(user_recs[user_recs['Mois'] == choix_pdf].iloc[0])
                st.download_button("📥 Télécharger PDF", pdf_bytes, f"Bulletin_{choix_pdf}.pdf", "application/pdf", use_container_width=True)
        
        # PROGRESSION ET DÉCONNEXION
        if st.button("📈 PROGRESS", use_container_width=True):
            st.session_state.page = "PROGRESS"
            st.rerun()
        
        st.write("---")
        if st.button("🟦 DÉCONNEXION", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- INTERFACE DE SAISIE DES DONNÉES ---
    with st.container(border=True):
        st.markdown("<h1 style='text-align: center; color: #2E7D32;'>💰 BULLETIN DES DEPENSES</h1>", unsafe_allow_html=True)
        
        # Bouton Modifier
        if st.session_state.get('sel_mois_base') and st.session_state.inputs_locked:
            if st.button("📝 ACTIVER LA MODIFICATION", use_container_width=True):
                st.session_state.ask_u = not st.session_state.get('ask_u', False)
            
            if st.session_state.get('ask_u'):
                pwd_mod = st.text_input("Vérification Password OPEN/MODIFY", type="password")
                if st.button("Débloquer les champs"):
                    if pwd_mod == st.session_state.user_pw_open:
                        st.session_state.inputs_locked = False
                        st.rerun()
                    else:
                        st.error("Mot de passe incorrect.")

        L = st.session_state.inputs_locked
        col_m, col_a = st.columns(2)
        col_m.text_input("MOIS EN COURS", value=st.session_state.get('sel_mois_affiche',''), disabled=True)
        col_a.text_input("ANNÉE", value=st.session_state.get('sel_annee',''), disabled=True)
        
        st.write("### Entrées financières")
        st.session_state.n_rev = st.number_input("REVENU MENSUEL GLOBAL ($)", value=int(st.session_state.get('n_rev',0)), disabled=L)
        
        st.write("### Ventilation des dépenses")
        c1, c2 = st.columns(2)
        st.session_state.n_loy = c1.number_input("LOYER & CHARGES", value=int(st.session_state.get('n_loy',0)), disabled=L)
        st.session_state.n_sco = c1.number_input("SCOLARITÉ / ÉTUDES", value=int(st.session_state.get('n_sco',0)), disabled=L)
        st.session_state.n_rat = c1.number_input("RATION ALIMENTAIRE", value=int(st.session_state.get('n_rat',0)), disabled=L)
        
        st.session_state.n_det = c2.number_input("REMBOURSEMENT DETTES", value=int(st.session_state.get('n_det',0)), disabled=L)
        st.session_state.n_poc = c2.number_input("ARGENT DE POCHE", value=int(st.session_state.get('n_poc',0)), disabled=L)
        st.session_state.n_ast = c2.number_input("ASSISTANCE / DONS", value=int(st.session_state.get('n_ast',0)), disabled=L)
        
        st.session_state.n_aut = st.number_input("AUTRES DÉPENSES IMPRÉVUES", value=int(st.session_state.get('n_aut',0)), disabled=L)
        
        st.write("---")
        if st.button("🚀 CALCULER ET VOIR LES RÉSULTATS", use_container_width=True, type="primary"):
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
        st.markdown(f"<h2 style='text-align: center;'>📊 BILAN : {st.session_state.sel_mois_base.upper()}</h2>", unsafe_allow_html=True)
        
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
            # Gestion des versions (Mod1, Mod2...)
            exist = df_hist[(df_hist['Utilisateur'] == st.session_state.current_user) & 
                            (df_hist['Mois'].str.startswith(st.session_state.sel_mois_base)) & 
                            (df_hist['Annee'].astype(str) == st.session_state.sel_annee)]
            
            nom_version = f"{st.session_state.sel_mois_base}Mod{len(exist)}" if not exist.empty else st.session_state.sel_mois_base
            
            new_data = {
                'Utilisateur': st.session_state.current_user, 'Mois': nom_version, 
                'Annee': st.session_state.sel_annee, 'Revenu': st.session_state.n_rev, 
                'Loyer': st.session_state.n_loy, 'Scolarite': st.session_state.n_sco, 
                'Ration': st.session_state.n_rat, 'Dette': st.session_state.n_det, 
                'Poche': st.session_state.n_poc, 'Assistance': st.session_state.n_ast, 
                'Autres': st.session_state.n_aut, 'Total_Depenses': st.session_state.total_dep, 
                'Epargne': st.session_state.epargne, 'Date_Enregistrement': pd.Timestamp.now()
            }
            pd.concat([df_hist, pd.DataFrame([new_data])], ignore_index=True).to_csv(FILE_DATA, index=False)
            st.success("Données archivées avec succès !")
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

# --- 12. PAGE : PROGRESSION (GRAPHES) ---
elif st.session_state.page == "PROGRESS":
    with st.container(border=True):
        st.title("📈 ANALYSE DE PROGRESSION")
        df_p = pd.read_csv(FILE_DATA)
        data_p = df_p[df_p['Utilisateur'] == st.session_state.current_user]
        
        if not data_p.empty:
            st.write("Évolution de l'épargne au fil du temps")
            st.line_chart(data_p, x='Mois', y='Epargne')
            
            st.write("Comparaison Revenu vs Dépenses")
            st.bar_chart(data_p, x='Mois', y=['Revenu', 'Total_Depenses'])
        else:
            st.info("Aucune donnée disponible pour générer les graphiques.")
            
        if st.button("⬅️ RETOUR"):
            st.session_state.page = "MAIN_APP"
            st.rerun()

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
        
        if st.button("💾 SAUVEGARDER LES NOUVEAUX CODES"):
            df_clients = pd.read_csv(FILE_CLIENTS, dtype=str)
            df_clients.loc[df_clients['name'] == usr['name'], ['pw_open_modify','pw_adm_print_prog','pw_user_adm']] = [new_p1, new_p2, new_p3]
            df_clients.to_csv(FILE_CLIENTS, index=False)
            st.success("Mise à jour réussie !")
            st.session_state.page = "ACCEUIL"
            st.rerun()
        if st.button("⬅️ ANNULER"):
            st.session_state.page = "ACCEUIL"
            st.rerun()