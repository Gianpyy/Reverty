import streamlit as st
import streamlit_antd_components as sac
from orchestrator import Orchestrator
from helpers.enums import LLMClientType

def parse_ast_string_to_sac(ast_string):
    """
    Converts Lark AST string to a list of TreeItem for visualization.
    """
    lines = ast_string.strip().split('\n')
    if not lines:
        return []

    items = []
    stack = []

    for line in lines:
        # Calculate indentation level
        indent = len(line) - len(line.lstrip())
        # Clean the node name by removing Lark's tree formatting characters
        name = line.strip().replace('|--', '').replace('`--', '').replace('|', '').strip()
        
        new_item = sac.TreeItem(label=name)
        
        if indent == 0:
            # Handle root node
            items.append(new_item)
            stack = [(0, new_item)]
        else:
            # Find the correct parent by comparing indentation levels
            while stack and stack[-1][0] >= indent:
                stack.pop()
            
            if stack:
                parent = stack[-1][1]
                if parent.children is None:
                    parent.children = []
                parent.children.append(new_item)
            
            stack.append((indent, new_item))
            
    return items

def main():
    st.set_page_config(page_title="Reverty", page_icon="🤖", layout="wide")
    st.title("Reverty")

    with st.sidebar:


        col_side1, col_logo, col_side2 = st.columns([0.2, 2, 0.2])
        
        with col_logo:
            st.image("./assets/logos/reverty_logo.png", width=180)

        st.header("Impostazioni")
        client_mapping = {"Mock Client": LLMClientType.MOCK, "GitHub Models": LLMClientType.GITHUB_MODELS, "Ollama": LLMClientType.OLLAMA}
        selected_client_str = st.selectbox("Client LLM", list(client_mapping.keys()))
        selected_client_enum = client_mapping[selected_client_str]
        
        prompt_utente = st.text_area("Requisiti del Codice:", value="Write a function that calculates the factorial of a number.", height=150)
        btn_run = st.button("Avvia Generazione", use_container_width=True)
        
        if st.button("Reset"):
            st.session_state.clear()
            st.rerun()

    # --- LAYOUT ---
    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.subheader("📋 Processo di Validazione")
        st.container(border=True)
        
    if btn_run:
        with col_left:
            with st.status("Agenti in azione...", expanded=True) as status:
                try:
                    orchestrator = Orchestrator(selected_client_enum)
                    result = orchestrator.run(prompt_utente)
                    print("Result: ", result)
                    ast_data = st.session_state.get("shared_ast_string", "")
                    
                    st.session_state.last_run = {
                        "reverty": result.get("reverty_code", ""),
                        "python": result.get("python_code", ""),
                        "ast": ast_data,
                        "success": result.get("status") == "success"
                    }
                    status.update(label="Completato!", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"Errore: {e}")
                    status.update(label="Fallito.", state="error")

    # --- VISUALIZZAZIONE RISULTATI ---
    if "last_run" in st.session_state:
        res = st.session_state.last_run
        
        with col_right:
            tab_reverty, tab_python, tab_ast = st.tabs(["📄 Reverty", "🐍 Python", "🌳 AST Explorer"])
            
            with tab_reverty:
                st.code(res["reverty"], language="rust")
                
            with tab_python:
                st.code(res["python"], language="python")
                    
            with tab_ast:
                if res["ast"]:
                    st.write("### Interactive AST View")
                    sac_items = parse_ast_string_to_sac(res["ast"])
                    
                    sac.tree(
                        items=sac_items,
                        label='Struttura Gerarchica',
                        index=0,
                        open_all=True,
                        show_line=True,
                        size='sm'
                    )
                else:
                    st.error("Nessun AST disponibile.")
    else:
        with col_right:
            st.info("I risultati appariranno qui.")

if __name__ == "__main__":
    main()