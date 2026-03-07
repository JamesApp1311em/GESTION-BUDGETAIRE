import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Gestionnaire de Dépenses", layout="centered")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .st-emotion-cache-zq5wms {visibility: visible !important;}
            
            /* Bloquer le glisser-pour-actualiser sur mobile */
            body {
                overscroll-behavior-y: contain;
            }
            html {
                overscroll-behavior-y: contain;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# --- 1. INITIALISATION ---
FILE_CLIENTS = 'clients.csv'
FILE_DATA = 'historique_complet.csv'

def init_db():
    if not os.path.exists(FILE_CLIENTS) or os.stat(FILE_CLIENTS).st_size == 0:
        pd.DataFrame(columns=['name', 'pw_open_modify', 'pw_adm_print_prog', 'pw_user_adm', 'status']).to_csv(FILE_CLIENTS, index=False)
    if not os.path.exists(FILE_DATA) or os.stat(FILE_DATA).st_size == 0:
        pd.DataFrame(columns=['Utilisateur', 'Mois', 'Annee', 'Revenu', 'Loyer', 'Scolarite', 'Ration', 'Dette', 'Poche', 'Assistance', 'Autres', 'Total_Depenses', 'Epargne', 'Date_Enregistrement']).to_csv(FILE_DATA, index=False)

init_db()

# --- 2. FONCTION PDF (RECUPÉRÉE DU 2ÈME CODE) ---
def create_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Header Bleu
    pdf.set_fill_color(164, 198, 228)
    pdf.cell(190, 10, "BULLETIN DES DEPENSES MENSUELLES", 1, 1, 'C', True)
    
    # Période
    pdf.set_font("Arial", "B", 12)
    pdf.cell(45, 10, "PERIODE", 1, 0, 'L', True)
    pdf.cell(70, 10, f"{row['Mois']}", 1, 0, 'C')
    pdf.cell(75, 10, f"{row['Annee']}", 1, 1, 'C')

    # Revenu
    pdf.cell(45, 10, "REVENU MENSUEL($)", 1, 0, 'L', True)
    pdf.cell(10, 10, "$", 1, 0, 'C')
    pdf.cell(100, 10, f"{float(row['Revenu']):,.2f}", 1, 0, 'R')
    pdf.cell(35, 10, "100%", 1, 1, 'C')

    # Liste des Dépenses
    pdf.cell(190, 10, "LES DEPENSES ($)", 1, 1, 'C', True)
    rev = float(row['Revenu']) if float(row['Revenu']) > 0 else 1
    items = [
        ("LOYER", row['Loyer']), ("SCOLARITE", row['Scolarite']), 
        ("RATION", row['Ration']), ("DETTE", row['Dette']), 
        ("ARGENT DE POCHE", row['Poche']), ("ASSISTANCE", row['Assistance']), 
        ("AUTRES DEPENSES", row['Autres'])
    ]
    
    for label, val in items:
        perc = (float(val)/rev)*100
        pdf.cell(45, 8, label, 1, 0, 'L')
        pdf.cell(10, 8, "$", 1, 0, 'C')
        pdf.cell(100, 8, f"{float(val):,.2f}", 1, 0, 'R')
        pdf.cell(35, 8, f"{perc:.0f}%", 1, 1, 'C')

    # Totaux
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(45, 10, "TOTAL DEPENSES", 1, 0, 'L', True)
    pdf.cell(10, 10, "$", 1, 0, 'C')
    pdf.cell(100, 10, f"{float(row['Total_Depenses']):,.2f}", 1, 0, 'R')
    pdf.cell(35, 10, f"{(float(row['Total_Depenses'])/rev)*100:.0f}%", 1, 1, 'C')

    pdf.cell(45, 10, "EPARGNE", 1, 0, 'L', True)
    pdf.cell(10, 10, "$", 1, 0, 'C')
    pdf.cell(100, 10, f"{float(row['Epargne']):,.2f}", 1, 0, 'R')
    pdf.cell(35, 10, f"{(float(row['Epargne'])/rev)*100:.0f}%", 1, 1, 'C')

    # Observation
    obs = "GOOD" if float(row['Epargne']) > 0 else "BAD"
    pdf.cell(45, 10, "OBSERVATION", 1, 0, 'L', True)
    pdf.set_fill_color(144, 238, 144) if obs == "GOOD" else pdf.set_fill_color(255, 99, 71)
    pdf.cell(145, 10, obs, 1, 1, 'C', True)

    # Section RÉSUMÉ
    pdf.ln(5)
    pdf.set_fill_color(164, 198, 228)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 30, "RÉSUMÉ", 1, 0, 'C', True)
    
    ratio = (float(row['Epargne'])/rev)*100
    if obs == "GOOD":
        texte_res = f"Felicitation ! Vous avez epargne {ratio:.0f}% de votre revenu. Vos finances sont saines pour le mois de {row['Mois']}."
    else:
        texte_res = f"Attention ! Vos depenses excedent votre revenu. Vous avez un deficit de {abs(float(row['Epargne'])):,.2f}$. Revoyez vos priorites."
    
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(130, 10, texte_res, 1, 'L')

    # Date
    pdf.ln(5)
    pdf.set_fill_color(164, 198, 228)
    pdf.cell(120, 8, "", 0, 0)
    pdf.set_font("Arial", "B", 8)
    pdf.cell(40, 8, "CALCULATION DATE", 1, 0, 'C', True)
    pdf.cell(30, 8, f"{pd.to_datetime(row['Date_Enregistrement']).strftime('%d/%m/%Y')}", 1, 1, 'C')
    
    return bytes(pdf.output(dest='S'))

# --- 3. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = "ACCEUIL"
if 'inputs_locked' not in st.session_state: st.session_state.inputs_locked = True 
if 'sel_mois_base' not in st.session_state: st.session_state.sel_mois_base = ""
if 'sel_annee' not in st.session_state: st.session_state.sel_annee = ""
if 'sel_mois_affiche' not in st.session_state: st.session_state.sel_mois_affiche = ""

# --- 4. INTERFACE : ACCEUIL ---
if st.session_state.page == "ACCEUIL":
    with st.container(border=True):
        st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🔐 ACCÈS SYSTÈME</h1>", unsafe_allow_html=True)
        u_n = st.text_input("USER NAME")
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
                else: st.error("⚠️ Compte bloqué.")
            else: st.error("❌ Identifiants incorrects.")

        c1, c2, c3 = st.columns(3)
        if c1.button("🔑 LOGIN"): st.session_state.page = "LOGIN"; st.rerun()
        if c2.button("🛡️ APP ADM"): st.session_state.page = "VERIF_ADM"; st.rerun()
        if c3.button("👤 USER ADM"): st.session_state.page = "VERIF_USER_ADM"; st.rerun()

        st.write("---")
        # --- BOUTON DE SORTIE SÉCURISÉ ---
if 'confirm_exit' not in st.session_state:
    st.session_state.confirm_exit = False

if not st.session_state.confirm_exit:
    if st.button("❌ Quitter l'application"):
        st.session_state.confirm_exit = True
        st.rerun()
else:
    st.warning("Êtes-vous sûr de vouloir fermer l'application ?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Oui, Quitter"):
            st.success("Déconnexion réussie. Fermez votre onglet.")
            st.stop()
    with col2:
        if st.button("↩️ Annuler"):
            st.session_state.confirm_exit = False
            st.rerun()
# --- 5. INTERFACE : MAIN_APP ---
elif st.session_state.page == "MAIN_APP":
    df_h = pd.read_csv(FILE_DATA)
    user_recs = df_h[df_h['Utilisateur'] == st.session_state.current_user]

    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.current_user}")
        if st.button("📅 SELECT MONTH", use_container_width=True): 
            st.session_state.show_date_picker = not st.session_state.get('show_date_picker', False)
        
        if st.session_state.get('show_date_picker'):
            with st.container(border=True):
                m_c = st.selectbox("Mois", ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
                a_c = st.selectbox("Année", [str(a) for a in range(2024, 2035)])
                
                versions = user_recs[(user_recs['Mois'].str.startswith(m_c)) & (user_recs['Annee'].astype(str) == a_c)]
                v_choisie = m_c
                
                if not versions.empty and len(versions) > 1:
                    v_choisie = st.selectbox("Versions disponibles", versions['Mois'].tolist())
                
                if st.button("✅ CONFIRMER"):
                    st.session_state.update({'sel_mois_base': m_c, 'sel_annee': a_c, 'show_date_picker': False})
                    if not versions.empty:
                        st.session_state.last_version_name = versions.iloc[-1]['Mois']
                        v = versions[versions['Mois'] == v_choisie].iloc[0]
                        st.session_state.update({
                            'sel_mois_affiche': v['Mois'], 'n_rev': v['Revenu'], 'n_loy': v['Loyer'], 
                            'n_sco': v['Scolarite'], 'n_rat': v['Ration'], 'n_det': v['Dette'], 
                            'n_poc': v['Poche'], 'n_ast': v['Assistance'], 'n_aut': v['Autres'], 'inputs_locked': True
                        })
                    else:
                        st.session_state.update({'sel_mois_affiche': m_c, 'inputs_locked': False, 'last_version_name': m_c})
                        for k in ["n_rev", "n_loy", "n_sco", "n_rat", "n_det", "n_poc", "n_ast", "n_aut"]: st.session_state[k] = 0
                    st.rerun()

        if st.button("🛡️ ADM", use_container_width=True):
            st.session_state.ask_adm_main = not st.session_state.get('ask_adm_main', False)
        if st.session_state.get('ask_adm_main'):
            p_adm = st.text_input("Code ADM", type="password", key="side_adm")
            if st.button("Valider ADM"):
                if str(p_adm).strip() == st.session_state.user_pw_adm_extra:
                    st.session_state.page = "VIEW_BASE"; st.session_state.ask_adm_main = False; st.rerun()

        # --- LOGIQUE PRINT FUSIONNÉE ICI ---
        if st.button("🖨️ PRINT", use_container_width=True):
            st.session_state.ask_print = not st.session_state.get('ask_print', False)
        
        if st.session_state.get('ask_print'):
            p_prt = st.text_input("Pass ADM / PRINT", type="password", key="side_prt")
            if st.button("Accéder au Print"):
                if str(p_prt).strip() == st.session_state.user_pw_adm_extra:
                    st.session_state.show_print_ui = True
                else: st.error("Code incorrect")
            
            if st.session_state.get('show_print_ui'):
                st.write("---")
                if not user_recs.empty:
                    liste_mois = user_recs['Mois'].tolist()
                    choix_pdf = st.selectbox("Choisir le mois à imprimer", liste_mois)
                    
                    if st.button("Générer PDF"):
                        row_to_print = user_recs[user_recs['Mois'] == choix_pdf].iloc[0]
                        pdf_bytes = create_pdf(row_to_print)
                        st.download_button(label="📥 Télécharger le PDF", data=pdf_bytes, file_name=f"Bulletin_{choix_pdf}.pdf", mime="application/pdf")
                else: st.warning("Aucune donnée disponible pour l'impression.")

        if st.button("📈 VOIR PROGRESS", use_container_width=True):
            st.session_state.ask_prog = not st.session_state.get('ask_prog', False)
        if st.session_state.get('ask_prog'):
            p_prog = st.text_input("Pass ADM / PRINT", type="password", key="side_prog")
            if st.button("Ouvrir Progress"):
                if str(p_prog).strip() == st.session_state.user_pw_adm_extra:
                    st.session_state.page = "PROGRESS"; st.session_state.ask_prog = False; st.rerun()

        if st.button("🟦 DÉCONNEXION", use_container_width=True): st.session_state.clear(); st.rerun()

    with st.container(border=True):
        st.markdown("<h1 style='text-align: center; color: #2E7D32;'>💰 BULLETIN DES DEPENSES</h1>", unsafe_allow_html=True)
        
        if st.session_state.get('sel_mois_base') != "" and st.session_state.inputs_locked:
            if st.session_state.sel_mois_affiche == st.session_state.get('last_version_name'):
                if st.button("📝 MODIFY", use_container_width=True):
                    st.session_state.ask_u = not st.session_state.get('ask_u', False)
                
                if st.session_state.get('ask_u'):
                    p_mod = st.text_input("Pass MODIFY", type="password")
                    if st.button("Confirmer Modification"):
                        if str(p_mod).strip() == st.session_state.user_pw_open:
                            st.session_state.inputs_locked = False; st.session_state.ask_u = False; st.rerun()

        c_m, c_a = st.columns(2)
        c_m.text_input("MOIS", value=st.session_state.get('sel_mois_affiche',''), disabled=True)
        c_a.text_input("ANNÉE", value=st.session_state.get('sel_annee',''), disabled=True)
        
        L = st.session_state.inputs_locked
        st.session_state.n_rev = st.number_input("💵 REVENU ($)", value=int(st.session_state.get('n_rev',0)), step=1, disabled=L)
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.n_loy = st.number_input("🏠 LOYER ($)", value=int(st.session_state.get('n_loy',0)), step=1, disabled=L)
            st.session_state.n_sco = st.number_input("🎓 SCOLARITÉ ($)", value=int(st.session_state.get('n_sco',0)), step=1, disabled=L)
            st.session_state.n_rat = st.number_input("🍱 RATION ($)", value=int(st.session_state.get('n_rat',0)), step=1, disabled=L)
        with col2:
            st.session_state.n_det = st.number_input("💳 DETTE ($)", value=int(st.session_state.get('n_det',0)), step=1, disabled=L)
            st.session_state.n_poc = st.number_input("💗 POCHE ($)", value=int(st.session_state.get('n_poc',0)), step=1, disabled=L)
            st.session_state.n_ast = st.number_input("🤝 ASSISTANCE ($)", value=int(st.session_state.get('n_ast',0)), step=1, disabled=L)
        st.session_state.n_aut = st.number_input("📦 AUTRES ($)", value=int(st.session_state.get('n_aut',0)), step=1, disabled=L)

        if st.button("🚀 VOIR MES RÉSULTATS", use_container_width=True):
            if st.session_state.sel_mois_base == "":
                st.error("⚠️ Veuillez d'abord sélectionner un mois via le bouton 'SELECT MONTH'.")
            else:
                st.session_state.total_dep = sum([st.session_state.n_loy, st.session_state.n_sco, st.session_state.n_rat, st.session_state.n_det, st.session_state.n_poc, st.session_state.n_ast, st.session_state.n_aut])
                st.session_state.epargne = st.session_state.n_rev - st.session_state.total_dep
                st.session_state.page = 'RESULTATS'; st.rerun()

# --- 6. INTERFACE : RESULTATS ---
elif st.session_state.page == "RESULTATS":
    with st.container(border=True):
        st.markdown(f"<h2 style='text-align: center; color: #1565C0;'>📊 BILAN {st.session_state.sel_mois_base.upper()}</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown(f"<div style='border:2px solid #D32F2F; padding:15px; border-radius:10px; text-align:center;'><h3 style='color:#D32F2F;'>DEPENSES</h3><h2>{int(st.session_state.total_dep)} $</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='border:2px solid #388E3C; padding:15px; border-radius:10px; text-align:center;'><h3 style='color:#388E3C;'>EPARGNE</h3><h2>{int(st.session_state.epargne)} $</h2></div>", unsafe_allow_html=True)
        
        st.write("")
        if st.button("💾 SAUVEGARDER", use_container_width=True):
            if st.session_state.inputs_locked:
                st.warning("ℹ️ Aucune modification détectée. Sauvegarde ignorée.")
            else:
                df_h = pd.read_csv(FILE_DATA)
                exist = df_h[(df_h['Utilisateur'] == st.session_state.current_user) & (df_h['Mois'].str.startswith(st.session_state.sel_mois_base)) & (df_h['Annee'].astype(str) == st.session_state.sel_annee)]
                nom_f = f"{st.session_state.sel_mois_base}Mod{len(exist)}" if not exist.empty else st.session_state.sel_mois_base
                new_r = {'Utilisateur': st.session_state.current_user, 'Mois': nom_f, 'Annee': st.session_state.sel_annee, 'Revenu': st.session_state.n_rev, 'Loyer': st.session_state.n_loy, 'Scolarite': st.session_state.n_sco, 'Ration': st.session_state.n_rat, 'Dette': st.session_state.n_det, 'Poche': st.session_state.n_poc, 'Assistance': st.session_state.n_ast, 'Autres': st.session_state.n_aut, 'Total_Depenses': st.session_state.total_dep, 'Epargne': st.session_state.epargne, 'Date_Enregistrement': pd.Timestamp.now()}
                pd.concat([df_h, pd.DataFrame([new_r])], ignore_index=True).to_csv(FILE_DATA, index=False)
                st.success(f"✅ Sauvegardé : {nom_f}")
                st.session_state.inputs_locked = True
                st.session_state.page = "MAIN_APP"
                st.rerun()
            
        if st.button("⬅️ RETOUR"): st.session_state.page = "MAIN_APP"; st.rerun()

# --- 7. INTERFACE : PROGRESS ---
elif st.session_state.page == "PROGRESS":
    with st.container(border=True):
        st.title("📈 PROGRESSION")
        df_h = pd.read_csv(FILE_DATA)
        u_data = df_h[df_h['Utilisateur'] == st.session_state.current_user].copy()
        if not u_data.empty:
            c_e, c_t = st.columns(2)
            esc = c_e.radio("Échelle", ["Mensuelle", "Annuelle"], horizontal=True)
            typ = c_t.selectbox("Style de graphe", ["Courbe (Line)", "Colonnes (Bar)", "Points (Scatter)", "Aire (Area)"])
            u_data['Date'] = pd.to_datetime(u_data['Date_Enregistrement'])
            u_data['M_Pur'] = u_data['Mois'].str.replace(r'Mod\d*', '', regex=True).str.strip()
            
            if esc == "Mensuelle":
                df_p = u_data.groupby(['Annee', 'M_Pur']).tail(1).copy()
                m_o = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
                df_p['Idx'] = df_p['M_Pur'].apply(lambda x: m_o.index(x) if x in m_o else 99)
                df_p = df_p.sort_values(by=['Annee', 'Idx'])
                x_ax = 'M_Pur'
            else:
                df_p = u_data.groupby('Annee').tail(1).copy().sort_values('Annee')
                x_ax = 'Annee'

            if "Line" in typ: st.line_chart(df_p, x=x_ax, y='Epargne')
            elif "Bar" in typ: st.bar_chart(df_p, x=x_ax, y='Epargne')
            elif "Scatter" in typ: st.scatter_chart(df_p, x=x_ax, y='Epargne')
            elif "Area" in typ: st.area_chart(df_p, x=x_ax, y='Epargne')
            
            st.text_input("💰 TOTAL CUMULÉ ($)", value=str(int(df_p['Epargne'].sum())), disabled=True)
        
        if st.button("⬅️ RETOUR AU BULLETIN"): st.session_state.page = "MAIN_APP"; st.rerun()

# --- 8. INTERFACE : VIEW_BASE (GESTION DONNÉES) ---
elif st.session_state.page == "VIEW_BASE":
    with st.container(border=True):
        st.title("🔓 GESTION DES DONNÉES")
        df_h = pd.read_csv(FILE_DATA)
        user_recs = df_h[df_h['Utilisateur'] == st.session_state.current_user]
        st.dataframe(user_recs, use_container_width=True)
        h_list = user_recs['Mois'].unique().tolist()
        s_del = st.selectbox("Sélectionner une version à supprimer :", ["---"] + h_list)
        if s_del != "---" and st.button("🗑️ SUPPRIMER"):
            df_h = df_h[~((df_h['Utilisateur'] == st.session_state.current_user) & (df_h['Mois'] == s_del))]
            df_h.to_csv(FILE_DATA, index=False)
            st.success(f"'{s_del}' supprimé."); st.rerun()
        if st.button("⬅️ RETOUR AU BULLETIN"): st.session_state.page = "MAIN_APP"; st.rerun()

# --- 9. INTERFACE : LOGIN / ADM / USER ADM ---
elif st.session_state.page == "LOGIN":
    with st.container(border=True):
        st.title("⚙️ CRÉATION COMPTE")
        n = st.text_input("USER NAME")
        p1 = st.text_input("PASSWORD (OPEN APP / MODIFY)")
        p2 = st.text_input("PASSWORD (ADM / PRINT)")
        p3 = st.text_input("PASSWORD (USER ADM)")
        if st.button("💾 CRÉER COMPTE", use_container_width=True):
            if not n or not p1 or not p2 or not p3: st.error("⚠️ Remplir tous les champs.")
            else:
                df = pd.read_csv(FILE_CLIENTS, dtype=str)
                new_u = pd.DataFrame([{'name':n, 'pw_open_modify':str(p1), 'pw_adm_print_prog':str(p2), 'pw_user_adm':str(p3), 'status':"Active"}])
                pd.concat([df, new_u], ignore_index=True).to_csv(FILE_CLIENTS, index=False)
                st.success("Compte créé !"); st.session_state.page = "ACCEUIL"; st.rerun()
        if st.button("⬅️ RETOUR"): st.session_state.page = "ACCEUIL"; st.rerun()

elif st.session_state.page == "APP_ADM":
    with st.container(border=True):
        st.title("🖥️ PANNEAU D'ADMINISTRATION")
        df_adm = pd.read_csv(FILE_CLIENTS, dtype=str).fillna("")
        for i, r in df_adm.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.write(f"**{r['name']}**")
                is_a = r['status'].lower() in ['true', 'active']
                if c2.checkbox("ACTIF", value=is_a, key=f"stat_{i}") != is_a:
                    df_adm.at[i, 'status'] = "Active" if not is_a else "Blocked"
                    df_adm.to_csv(FILE_CLIENTS, index=False); st.rerun()
                if c3.button("🗑️", key=f"del_{i}"):
                    df_adm.drop(i).to_csv(FILE_CLIENTS, index=False); st.rerun()
        if st.button("⬅️ RETOUR"): st.session_state.page = "ACCEUIL"; st.rerun()

elif st.session_state.page == "VERIF_ADM":
    with st.container(border=True):
        if st.text_input("Code Maître", type="password") == "G1711E" and st.button("VALIDER"): 
            st.session_state.page = "APP_ADM"; st.rerun()
        if st.button("⬅️ RETOUR"): st.session_state.page = "ACCEUIL"; st.rerun()

elif st.session_state.page == "VERIF_USER_ADM":
    with st.container(border=True):
        st.title("👤 ACCÈS PROFIL")
        u_v = st.text_input("USER NAME")
        p_v = st.text_input("PASSWORD (USER ADM)", type="password")
        if st.button("🔍 VÉRIFIER"):
            df = pd.read_csv(FILE_CLIENTS, dtype=str)
            match = df[(df['name'] == u_v.strip()) & (df['pw_user_adm'] == p_v.strip())]
            if not match.empty:
                st.session_state.temp_user = match.iloc[0].to_dict()
                st.session_state.page = "EDIT_PROFIL"; st.rerun()
            else: st.error("Identifiants incorrects.")
        if st.button("⬅️ RETOUR"): st.session_state.page = "ACCEUIL"; st.rerun()

elif st.session_state.page == "EDIT_PROFIL":
    with st.container(border=True):
        st.title("📝 MODIFIER PROFIL")
        d = st.session_state.temp_user
        np1 = st.text_input("NEW PW (OPEN/MODIFY)", value=d['pw_open_modify'])
        np2 = st.text_input("NEW PW (ADM/PRINT)", value=d['pw_adm_print_prog'])
        np3 = st.text_input("NEW PW (USER ADM)", value=d['pw_user_adm'])
        if st.button("💾 ENREGISTRER"):
            df = pd.read_csv(FILE_CLIENTS, dtype=str)
            df.loc[df['name'] == d['name'], ['pw_open_modify','pw_adm_print_prog','pw_user_adm']] = [np1, np2, np3]
            df.to_csv(FILE_CLIENTS, index=False)
            st.success("✅ Changements enregistrés !")
        if st.button("⬅️ RETOUR"): st.session_state.page = "ACCEUIL"; st.rerun()