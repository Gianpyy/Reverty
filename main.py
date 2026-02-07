import streamlit as st
import streamlit_antd_components as sac
from orchestrator import Orchestrator
from helpers.enums import LLMClientType
from config import github_token
from gui.examples import examples
from helpers.utils import parse_ast_string_to_sac  


def update_log_ui(message, container):
    """
    Updates the log UI by appending a new message to the session log list.
    It re-renders all previous logs inside the provided container.
    """
    if "log_list" not in st.session_state:
        st.session_state.log_list = []
    
    st.session_state.log_list.append(message)
    
    container.empty()
    with container.container(height=550, border=False):
        for msg in st.session_state.log_list:
            with st.chat_message("assistant"):
                st.text(msg)

def reset_generation():
    """Resets generation state variables and clears logs."""
    st.session_state.log_list = []
    st.session_state.last_run = None
    st.session_state.final_prompt = ""
    st.session_state.prompt_height = 140
    st.session_state.input_prompt = ""

def process_submission():
    """Processes the input submission: resets generation and stores the current prompt."""
    if st.session_state.last_run:
        reset_generation()
        
    testo_inserito = st.session_state.get("input_prompt", "")
    st.session_state.final_prompt = testo_inserito
    st.session_state.prompt_height = 50

def select_example(text):
    """Updates the text area with the selected example text."""
    st.session_state.input_prompt = text
    
def main():

    # Load external CSS file for custom styling
    with open("./gui/styles/main.css", "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Streamlit page configuration
    st.set_page_config(
        page_title="Reverty", 
        page_icon="./assets/logos/reverty_logo.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS to modify tab and layout styling
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem; }
            button[data-baseweb="tab"] p {
                font-size: 1.2rem !important;
                font-weight: 600 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Compact layout and remove default header padding
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

    # Header with logo and title
    col_t1, col_t2 = st.columns([2, 1])
    
    with col_t1:
        st.markdown("""
            <style>
                .header-container {
                    display: flex;
                    align-items: center;
                    gap: 20px;
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

        col_logo_img, col_text_title = st.columns([1.3, 8])
        with col_logo_img:
             st.image("./assets/logos/reverty_logo.png", width=130)
        with col_text_title:
             st.markdown('<p class="gradient-text" style="font-size: 3rem;">Reverty</p>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 4rem;'></div>", unsafe_allow_html=True)

    # Initialize session state variables
    if "last_run" not in st.session_state:
        st.session_state.last_run = None
    if "shared_log_string" not in st.session_state:
        st.session_state.shared_log_string = ""
    if "prompt_height" not in st.session_state:
        st.session_state.prompt_height = 140

    # Default configuration for model and temperature
    temperature = 0.3
    st.session_state.api_key = github_token


    # Sidebar setup for configuration and settings
    with st.sidebar:
        col_side1, col_logo, col_side2 = st.columns([0.2, 2, 0.2])
        
        st.markdown("<div style='font-size: 1.6rem;margin-bottom: 1rem;'>Settings</div>", unsafe_allow_html=True)
        
        # Select LLM client type
        client_mapping = {
            "GitHub Models": LLMClientType.GITHUB_MODELS,
            "Ollama": LLMClientType.OLLAMA, 
            "Mock Client": LLMClientType.MOCK, 
        }
        st.markdown("""
            <style>
            div[data-baseweb="select"] > div {
                cursor: pointer !important;
            }
            </style>
            """, unsafe_allow_html=True)

        selected_client_str = st.selectbox("Client LLM", list(client_mapping.keys()))

        # Inizializza la variabile se non esiste
        if "previous_client" not in st.session_state:
            st.session_state.previous_client = selected_client_str

        if selected_client_str == "Mock Client":
            select_example(examples.get("Factorial function"))
        elif st.session_state.previous_client != selected_client_str:
            # Resetta solo se il client è cambiato
            st.session_state.input_prompt = ""

        # Aggiorna il client precedente
        st.session_state.previous_client = selected_client_str


        selected_client_enum = client_mapping[selected_client_str]
        
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        
        # Slider for temperature setting
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.3,
            step=0.1,
            help="Controls the model's creativity. Low = deterministic, high = creative"
        )

        # Sliders for orchestrator and validation iterations
        st.markdown("<div style='margin-top: 20px;font-size: 1.2rem;'>Iterations</div>", unsafe_allow_html=True)
        
        st.slider("Orchestrator", min_value=0, max_value=20, value=3, step=1, key="max_orchestrator_iterations")
        st.slider("Validation", min_value=0, max_value=20, value=3, step=1, key="max_validation_iterations")

        st.markdown("<div style='margin-top: 1s0px;'></div>", unsafe_allow_html=True)

        # Optional GitHub API key input if selected client is GitHub
        if selected_client_enum == LLMClientType.GITHUB_MODELS:
            st.session_state.api_key = st.text_input("API Key", value=st.session_state.api_key, type="password",help="API Key for GitHub Models (optional: took from .env file)")

        if st.session_state.last_run:
            st.markdown("<div style='margin-top: 20px;font-size: 0.9rem;margin-bottom: 5px;'>Generation</div>", unsafe_allow_html=True)
            if st.button("Reset", use_container_width=True, type="secondary"):
                reset_generation()
                st.rerun()
        
        # Footer with links to GitHub and docs
        st.markdown("<div style='height: calc(60vh - 400px);'></div>", unsafe_allow_html=True)
        sac.buttons([
            sac.ButtonsItem(label='GitHub', icon='github', href='https://github.com/Gianpyy/reverty'),
            sac.ButtonsItem(label='Documentation', icon='file-earmark-text', href='https://github.com/Gianpyy/Reverty/blob/main/documentation.pdf'),
        ], align='end', variant='link', size='sm', index=None)


    # --- Main layout ---
    col_left, col_right = st.columns([1, 0.8])
    

    with col_left:
        log_container = st.empty()
        
        if st.session_state.get("log_list"):
            with log_container.container(height=550, border=False):
                for msg in st.session_state.log_list:
                    with st.chat_message("assistant"):
                        st.text(msg)
        
        # Centered input area
        col_spacer1, col_prompt, col_spacer2 = st.columns([0.2, 1, 0.2])
        
        with col_prompt:
            message_placeholder = st.empty()
            
            if not st.session_state.get("last_run"):
                with message_placeholder:
                    message_placeholder.markdown("""
                        <h2 style='margin: 0;margin-bottom: 20px; color: rgba(255, 255, 255, 0.7);font-weight: 300;'>
                            Ready to generate some <i>edoc</i>?
                        </h2>
                    """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

            if "input_prompt" not in st.session_state:
                st.session_state.input_prompt = "" 

            prompt_utente = st.text_area(
                "Requisiti del Codice",
                placeholder="Write a function...",
                height=st.session_state.prompt_height,
                label_visibility="collapsed",
                key="input_prompt"
            )

            is_input_empty = st.session_state.get("input_prompt", "").strip() == ""

            btn_run = st.button(
                "Generate", 
                use_container_width=True, 
                type="primary" if not is_input_empty else "secondary",
                disabled=is_input_empty,
                on_click=process_submission,
            )
        

        # Example buttons grid
        st.markdown("<hr style='margin-bottom: 10px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-bottom: 20px; color: rgba(255, 255, 255, 0.9);'>Examples</h3>", unsafe_allow_html=True)

        examples_list = list(examples.items()) 

        for i in range(0, len(examples_list), 3):
            cols = st.columns(3)
            for j in range(3):
                index = i + j
                if index < len(examples_list):
                    label, prompt = examples_list[index]
                    with cols[j]:
                        st.button(label, key=f"ex_{index}", use_container_width=True, on_click=select_example, args=(prompt,), type="tertiary")

        st.markdown("<div style='margin-bottom: 60px;'></div>", unsafe_allow_html=True)
            

    # --- Run logic ---
    if btn_run:
        st.session_state.prompt_height = 50
        message_placeholder.empty()
        st.session_state.log_list = []
        log_container.empty()
        
        with col_left:
            try:
                callback = lambda msg: update_log_ui(msg, log_container)
                
                orchestrator = Orchestrator(
                    selected_client_enum, 
                    temperature, 
                    api_key=st.session_state.api_key, 
                    on_log=callback,
                    max_orchestrator_iterations=st.session_state.max_orchestrator_iterations,
                    max_validation_iterations=st.session_state.max_validation_iterations
                )
                
                result = orchestrator.run(prompt_utente)
                
                ast_data = st.session_state.get("shared_ast_string", "")
                
                st.session_state.last_run = {
                    "reverty": st.session_state.shared_reverty_code,
                    "python": st.session_state.shared_python_code,
                    "ast": ast_data,
                    "logs": st.session_state.shared_log_string,
                    "success": result.get("status") == "success"
                }
                
                st.rerun()
                    
            except Exception as e:
                st.error(f"Errore: {e}")

    # --- Display results ---
    res = st.session_state.last_run
    with col_right:

        st.markdown("""
        <style>
        div[data-testid="stTabs"] button {
            padding-left: 15px;
            padding-right: 15px;
            margin-left: 5px;
            margin-right: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        tab_reverty, tab_python, tab_ast = st.tabs(["Reverty", "Python", "AST Explorer"])
        
        with tab_reverty:
            if res and res.get("reverty"):
                st.code(res["reverty"], language="rust")
            else:
                st.info("No Reverty code available. Click 'Generate' to start.")
        with tab_python:
            if res and res.get("python"):
                st.code(res["python"], language="python")
            else:
                st.info("No Python code available.")
        with tab_ast:
            if res and res.get("ast"):
                sac_items = parse_ast_string_to_sac(res["ast"])
                sac.tree(items=sac_items, open_all=True, show_line=True, size='sm')
            else:
                st.info("No AST available.")

if __name__ == "__main__":
    main()