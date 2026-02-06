import streamlit as st
import streamlit_antd_components as sac
from orchestrator import Orchestrator
from helpers.enums import LLMClientType

def parse_ast_string_to_sac(ast_string):
    """
    Converte la stringa di Lark in sac.TreeItem.
    """
    lines = ast_string.strip().split('\n')
    if not lines:
        return []

    items = []
    stack = []

    for line in lines:
        indent = len(line) - len(line.lstrip())
        name = line.strip().replace('|--', '').replace('`--', '').replace('|', '').strip()
        
        new_item = sac.TreeItem(label=name)
        
        if indent == 0:
            items.append(new_item)
            stack = [(0, new_item)]
        else:
            while stack and stack[-1][0] >= indent:
                stack.pop()
            
            if stack:
                parent = stack[-1][1]
                if parent.children is None:
                    parent.children = []
                parent.children.append(new_item)
            
            stack.append((indent, new_item))
            
    return items

# def update_log_ui(message, container):
#     """
#     Aggiunge un messaggio alla lista dei log e lo visualizza immediatamente.
#     """
#     if "log_list" not in st.session_state:
#         st.session_state.log_list = []
    
#     # Aggiungiamo il messaggio alla cronologia
#     st.session_state.log_list.append(message)
    
#     # Visualizziamo nel container usando lo stile chat (che ha lo scroll migliore)
#     with container:
#         with st.chat_message("ai"): # Puoi usare un'icona personalizzata qui
#             st.markdown(f"**{message}**")

def update_log_ui(message, container):
    if "log_list" not in st.session_state:
        st.session_state.log_list = []
    
    # Aggiungi il nuovo messaggio
    st.session_state.log_list.append(message)
    
    # Svuota e ri-renderizza TUTTO il container con TUTTI i messaggi
    container.empty()
    with container.container(height=550, border=False):
        for msg in st.session_state.log_list:
            with st.chat_message("assistant"):
                st.text(msg)

def main():

    # Load CSS styles from main.css
    with open("./gui/styles/main.css", "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.set_page_config(page_title="Reverty", page_icon="🐍", layout="wide")
    st.title("Reverty")

    # --- INIZIALIZZAZIONE SESSION STATE ---
    if "last_run" not in st.session_state:
        st.session_state.last_run = None
    if "shared_log_string" not in st.session_state:
        st.session_state.shared_log_string = ""

    # --- INIZIALIZZAZIONE CONFIGURAZIONE ---
    LLM_Model = "Llama 3.2"
    temperature = 0.7


    with st.sidebar:
        col_side1, col_logo, col_side2 = st.columns([0.2, 2, 0.2])
        with col_logo:
            try:
                st.image("./assets/logos/reverty_logo.png", width=180)
            except:
                st.markdown("### 🤖 REVERTY")

        st.header("Settings")
        
        # Client LLM
        client_mapping = {
            "Mock Client": LLMClientType.MOCK, 
            "Ollama": LLMClientType.OLLAMA, 
            "GitHub Models": LLMClientType.GITHUB_MODELS
        }
        selected_client_str = st.selectbox("Client LLM", list(client_mapping.keys()))
        selected_client_enum = client_mapping[selected_client_str]
        
        # Slider Temperatura
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.3,
            step=0.1,
            help="Controls the model's creativity. Low values (0.0-0.3) = more deterministic, high values (0.7-2.0) = more creative"
        )

    
        if st.button("Reset", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()
        

    # --- LAYOUT ---
    col_left, col_right = st.columns([1, 0.8])
    

    with col_left:
        #st.subheader("📋 Processo di Validazione")
        
        # Container per i log
        log_container = st.empty()
        
        # Mostra log esistenti o messaggio iniziale
        if st.session_state.get("log_list"):
            with log_container.container(height=550, border=False):
                for msg in st.session_state.log_list:
                    with st.chat_message("assistant"):
                        st.text(msg)
        
        # SPAZIO TRA LOG E PROMPT
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        
        # Sezione Prompt - più stretta al centro
        col_spacer1, col_prompt, col_spacer2 = st.columns([0.2, 1, 0.2])

       
        
        with col_prompt:
            
            prompt_utente = st.text_area(
                "Requisiti del Codice", 
                value="Write a function that calculates the factorial of a number.", 
                height=30,
                label_visibility="collapsed"
            )

            btn_run = st.button("Generate", use_container_width=True, type="primary")
    
            


    # --- LOGICA DI ESECUZIONE ---
    if btn_run:
        # Pulizia log per la nuova run
        st.session_state.log_list = []
        log_container.empty()
        
        with col_left:
            #with st.status("Agenti in azione...", expanded=True) as status:
            try:
                # Inizializza Orchestrator
                orchestrator = Orchestrator(selected_client_enum, temperature)
                
                # Callback che passa il container stesso
                callback = lambda msg: update_log_ui(msg, log_container)
                
                # Esecuzione
                result = orchestrator.run(prompt_utente, on_log=callback)
                
                # ... resto del codice ...
                    
                # Recupero AST (se salvato in session_state dall'orchestrator)
                ast_data = st.session_state.get("shared_ast_string", "")
                
                # Salvataggio risultati finali
                st.session_state.last_run = {
                    "reverty": result.get("reverty_code", ""),
                    "python": result.get("python_code", ""),
                    "ast": ast_data,
                    "logs": st.session_state.shared_log_string,
                    "success": result.get("status") == "success"
                }
                
                #status.update(label="Completato!", state="complete", expanded=False)
                st.rerun() # Refresh per popolare i tab a destra con i dati salvati
                    
            except Exception as e:
                st.error(f"Errore: {e}")
                #status.update(label="Fallito.", state="error")

    # --- VISUALIZZAZIONE RISULTATI (Colonna Destra) ---
    
    res = st.session_state.last_run
    with col_right:
        tab_reverty, tab_python, tab_ast = st.tabs(["📄 Reverty", "🐍 Python", "🌳 AST Explorer"])
        
        if res:
            with tab_reverty:
                st.code(res["reverty"], language="rust")
            with tab_python:
                st.code(res["python"], language="python")
            with tab_ast:
                if res["ast"]:
                    st.write("### Interactive AST View")
                    sac_items = parse_ast_string_to_sac(res["ast"])
                    sac.tree(items=sac_items, label='Struttura Gerarchica', open_all=True, show_line=True, size='sm')
                else:
                    st.error("Nessun AST disponibile.")

if __name__ == "__main__":
    main()