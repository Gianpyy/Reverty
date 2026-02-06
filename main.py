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

def process_submission():
    # 1. Recuperiamo il valore dalla key della text_area
    testo_inserito = st.session_state.get("input_prompt", "")
    
    # 2. Possiamo salvarlo in una variabile di "stato finale" se serve
    st.session_state.final_prompt = testo_inserito

    st.session_state.prompt_height = 50

def select_example(text):
    st.session_state.input_prompt = text
    
def main():

    # Load CSS styles from main.css
    with open("./gui/styles/main.css", "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.set_page_config(
        page_title="Reverty", 
        page_icon="🐍", 
        layout="wide",
        initial_sidebar_state="expanded" # Opzioni: "auto", "expanded", "collapsed"
    )

    st.markdown("""
        <style>
            .block-container { padding-top: 1rem; }
            
            /* STILE TAB PIÙ GRANDI */
            button[data-baseweb="tab"] p {
                font-size: 1.2rem !important; /* Dimensione dei titoli */
                font-weight: 600 !important;  /* Peso del font */
            }
        </style>
    """, unsafe_allow_html=True)

    # 2. CSS per eliminare l'header di sistema e compattare il layout
    st.markdown("""
        <style>
            .block-container {
                padding-top: 0.1rem;
                padding-bottom: 0rem;
            }
            .header-link {
                text-decoration: none;
                color: inherit;
                display: flex;
                align-items: center;
                gap: 5px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 3. Nuovo Header con Titolo, GitHub e Info
    col_t1, col_t2 = st.columns([2, 1])
    
    with col_t1:
        # Definiamo lo stile una volta sola
        st.markdown("""
            <style>
                .header-container {
                    display: flex;
                    align-items: center; /* Allinea verticalmente al centro */
                    gap: 20px;           /* Spazio tra logo e testo */
                }
                .gradient-text {
                    font-weight: 800;
                    background: linear-gradient(90deg, #3B5F7E 0%, #E7B94C 40%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin: 0;
                    line-height: 1;
                }
            </style>
        """, unsafe_allow_html=True)

        # Creiamo l'header con logo e testo nello stesso div
        # Nota: usiamo l'URL dell'immagine se possibile, o carichiamola tramite base64 se è locale
        # Ma per semplicità con Streamlit, ecco il metodo ibrido più pulito:
        
        col_logo_img, col_text_title = st.columns([1.4, 8],gap="xxsmall")
        with col_logo_img:
             st.image("./assets/logos/reverty_logo.png", width=160) # Logo più piccolo per stare in linea
        with col_text_title:
             st.markdown('<p class="gradient-text" style="font-size: 5rem;">Reverty</p>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 4rem;'></div>", unsafe_allow_html=True)

    # --- INIZIALIZZAZIONE SESSION STATE ---
    if "last_run" not in st.session_state:
        st.session_state.last_run = None
    if "shared_log_string" not in st.session_state:
        st.session_state.shared_log_string = ""
    # --- INIZIALIZZAZIONE SESSION STATE ---
    if "prompt_height" not in st.session_state:
        st.session_state.prompt_height = 140  # Altezza iniziale (es. 200px)

    # --- INIZIALIZZAZIONE CONFIGURAZIONE ---
    LLM_Model = "Llama 3.2"
    temperature = 0.7


    with st.sidebar:
        col_side1, col_logo, col_side2 = st.columns([0.2, 2, 0.2])
        
        st.markdown("<div style='font-size: 1.6rem;margin-bottom: 1rem;'>Settings</div>", unsafe_allow_html=True)
        
        # Client LLM
        client_mapping = {
            "Mock Client": LLMClientType.MOCK, 
            "Ollama": LLMClientType.OLLAMA, 
            "GitHub Models": LLMClientType.GITHUB_MODELS
        }
        selected_client_str = st.selectbox("Client LLM", list(client_mapping.keys()))
        selected_client_enum = client_mapping[selected_client_str]
        
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
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
            st.session_state.input_prompt = ""
            st.session_state.prompt_height = 140 
            st.rerun()
        
        # Spacer che spinge i link in fondo
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        
        # Alternativa: usa un container con posizione assoluta
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                display: flex;
                flex-direction: column;
            }
            .sidebar-footer {
                margin-top: auto;
                padding-top: 2rem;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Wrapper per i bottoni
        st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
        sac.buttons([
            sac.ButtonsItem(label='GitHub', icon='github', href='https://github.com/tuo-profilo/reverty'),
            sac.ButtonsItem(label='Documentation', icon='file-earmark-text'),
        ], align='end', variant='link', size='sm', index=None)
        st.markdown('</div>', unsafe_allow_html=True)
        

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
        
        # --- LAYOUT DEL PROMPT ---

        # Creiamo le colonne per centrare il contenuto
        col_spacer1, col_prompt, col_spacer2 = st.columns([0.2, 1, 0.2])
        
        with col_prompt:
            
            # 1. Placeholder per il messaggio iniziale
            message_placeholder = st.empty()
            
            # Mostra il messaggio solo se non è stata ancora fatta una run
            if not st.session_state.get("last_run"):
                with message_placeholder:
                    message_placeholder.markdown("""
                        <h2 style='margin: 0;margin-bottom: 40px; color: rgba(255, 255, 255, 0.7);font-weight: 300;'>
                            Ready to generate some code?
                        </h2>
                    """, unsafe_allow_html=True)
            # 2. Area di input

            if "input_prompt" not in st.session_state:
                st.session_state.input_prompt = ""

            prompt_utente = st.text_area(
                "Requisiti del Codice", 
                value=st.session_state.input_prompt, # <--- Collega il valore iniziale
                placeholder="Write a function...", 
                height=st.session_state.prompt_height,
                label_visibility="collapsed",
                key="input_prompt" 
            )

            btn_run = st.button(
                "Generate", 
                use_container_width=True, 
                type="primary",
                on_click=process_submission, # Esegue il rimpicciolimento istantaneo
            )
        

        # 1. Definizione degli esempi
        esempi = [
            "Factorial function", "Fibonacci sequence", 
            "Bubble sort", "Binary search", 
            "Matrix multiplication", "REST API Client"
        ]

        # 2. Creazione della griglia 3x2
        # Dividiamo la lista in gruppi di 2 per riga
        st.markdown("<hr style='margin-bottom: 0px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 40px; color: rgba(255, 255, 255, 0.9);'>Examples</h3>", unsafe_allow_html=True)
        
        esempi = {
            "Factorial function": "Write a function that calculates the factorial of a number.", 
            "Fibonacci sequence": "Write a function that calculates the Fibonacci sequence.", 
            "Bubble sort": "Write a function that implements the bubble sort algorithm.", 
            "Binary search": "Write a function that implements the binary search algorithm.", 
            "Matrix multiplication": "Write a function that multiplies two matrices.", 
            "REST API Client": "Write a function that implements a REST API client.", 
        }   

        # 1. Trasformiamo il dizionario in una lista di tuple per gestire gli indici
        lista_esempi = list(esempi.items()) 

        for i in range(0, len(lista_esempi), 3):
            cols = st.columns(3)
            for j in range(3):
                index = i + j
                if index < len(lista_esempi):
                    # label è la chiave (es. "Factorial function")
                    # prompt è il valore (es. "Write a function...")
                    label, prompt = lista_esempi[index]
                    
                    with cols[j]:
                        st.button(
                            label, 
                            key=f"ex_{index}", 
                            use_container_width=True,
                            on_click=select_example,
                            args=(prompt,) # Passiamo il prompt completo alla funzione
                        )

        # Spazio extra sotto la griglia
        st.markdown("<div style='margin-bottom: 60px;'></div>", unsafe_allow_html=True)
            

    # --- LOGICA DI ESECUZIONE ---
    if btn_run:
        st.session_state.prompt_height = 50
        message_placeholder.empty()
        # Pulizia log per la nuova run
        st.session_state.log_list = []
        log_container.empty()
        
        with col_left:
            #with st.status("Agenti in azione...", expanded=True) as status:
            try:
                # Callback che passa il container stesso
                callback = lambda msg: update_log_ui(msg, log_container)
                
                # Inizializza Orchestrator
                orchestrator = Orchestrator(selected_client_enum, temperature, on_log=callback)
                
                # Esecuzione
                result = orchestrator.run(prompt_utente)
                
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
        tab_reverty, tab_python, tab_ast = st.tabs(["Reverty", "Python", "AST Explorer"])
        
        # Gestione Tab Reverty
        with tab_reverty:
            if res and res.get("reverty"):
                st.code(res["reverty"], language="rust")
            else:
                st.info("No Reverty code available. Click 'Generate' to start.")
        # Gestione Tab Python
        with tab_python:
            if res and res.get("python"):
                st.code(res["python"], language="python")
            else:
                st.info("No Python code available.", icon="🐍")

        # Gestione Tab AST
        with tab_ast:
            if res and res.get("ast"):
                sac_items = parse_ast_string_to_sac(res["ast"])
                sac.tree(items=sac_items, open_all=True, show_line=True, size='sm')
            else:
                st.info("No AST available.")

if __name__ == "__main__":
    main()