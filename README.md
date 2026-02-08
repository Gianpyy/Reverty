<div align="center">
  <img src="https://github.com/Gianpyy/Reverty/blob/main/assets/logos/reverty_logo.png" alt="Logo" style="width: 40%">
</div>

## About Reverty
Reverty is an automated code generation framework built on a multi-agent architecture. The system is designed to transform natural language requests into executable code through a structured and verifiable generation pipeline.

At its core, Reverty relies on a custom programming language, also named Reverty, which can be described as a reversed variant of Python. This language preserves Python’s semantic model and execution logic while deliberately altering its syntactic surface.

The adoption of a custom language enables the integration of formal static analysis tools, including a dedicated parser and a transpiler that converts Reverty code into standard Python. These components are tightly integrated into the code generation process, allowing syntactic validation, error detection, and controlled execution of the generated programs.

### Example of Reverty code 
```ruby
: tni -> (tni: n) factorial fed
  res : tni = 1
  : n > 1 elihw
      res = res * n
      n = n - 1
  nruter res
```

## Documentation
You can read the full documentation [here](https://github.com/Gianpyy/Reverty/blob/main/docs/TechnicalDocument.pdf)
 > **Note:** The documentation is written in italian.

## Installation & Setup

Follow these steps to set up the project locally.

### Prerequisites

Before you begin, ensure you have [**Python 3.8+**](https://www.python.org/downloads/) installed on your system:

### 1. Install Ollama and Model

Reverty uses **Ollama** for local LLM inference.

1.  **Download and Install:** Visit [ollama.com](https://ollama.com/) and download the installer for your OS.
2.  **Pull the Model:** Open your terminal (Command Prompt, PowerShell, or Terminal) and run the following command to download the default model (`llama3.2`):
    ```bash
    ollama pull llama3.2
    ```
    > **Note:** If you want to use a different model, update the `OLLAMA_LLM_MODEL` variable in `config.py`.

### 2. Configure GitHub Models

To use **GitHub Models**:

1.  **Get Access:** Ensure you have access to GitHub Models (currently in limited public beta).
2.  **Generate a Token:** 
    -   Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens).
    -   Generate a new token (Classic or Fine-grained) with read access.
3.  **Setup Environment Variables:**
    -   Duplicate the `.env.example` file and rename it to `.env`.
    -   Open `.env` with a text editor and paste your token:
        ```ini
        GITHUB_TOKEN=your_generated_token_here
        ```

### 3. Install Python Dependencies

It is highly recommended to use a virtual environment to manage dependencies.

#### Option A: Using `venv` (Standard)

1.  **Create a Virtual Environment:**
    
    **Windows:**
    ```powershell
    python -m venv venv
    ```
    
    **macOS/Linux:**
    ```bash
    python3 -m venv venv
    ```

2.  **Activate the Virtual Environment:**
    
    **Windows:**
    ```powershell
    .\venv\Scripts\activate
    ```
    
    **macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

3.  **Install Requirements:**
    ```bash
    pip install -r requirements.txt
    ```


## Running the Application

Once everything is set up, you can launch the Reverty application.

Run the following command in your terminal (ensure your virtual environment is activated if using one):

```bash
streamlit run main.py
```

The application typically starts at `http://localhost:8501` and will open automatically in your default web browser.


## Authors

The project was realized by [Gianpio Silvestri](https://github.com/Gianpyy) and [Claudio Buono](https://github.com/ClaudioBuono) in 2026.
