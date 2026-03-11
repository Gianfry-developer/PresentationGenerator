"""
Presentation Generator - Applicazione principale
Genera presentazioni professionali da documenti usando Ollama
"""

import streamlit as st
from pathlib import Path

# Importa moduli
from modules.ollama_client import OllamaClient
from ui.sidebar import SidebarComponent
from ui.file_uploader import FileUploadComponent
from ui.chat_interface import ChatInterface
import config


# Configurazione pagina
st.set_page_config(
    page_title="Presentation Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stile custom
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Inizializza lo stato della sessione"""
    if 'ollama_client' not in st.session_state:
        st.session_state.ollama_client = OllamaClient(host=config.OLLAMA_HOST)
    
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = config.DEFAULT_MODEL
    
    if 'presentation_duration' not in st.session_state:
        st.session_state.presentation_duration = config.TARGET_PRESENTATION_MINUTES
    
    if 'words_per_minute' not in st.session_state:
        st.session_state.words_per_minute = config.WORDS_PER_MINUTE


def main():
    """Funzione principale dell'applicazione"""
    
    # Inizializza
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📊 Presentation Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Trasforma i tuoi documenti in presentazioni professionali con AI</p>', 
                unsafe_allow_html=True)
    
    # Sidebar
    sidebar = SidebarComponent(st.session_state.ollama_client)
    sidebar.render()
    
    # Layout principale
    tab1, tab2 = st.tabs(["📁 Carica & Genera", "💬 Chat Assistente"])
    
    with tab1:
        # File uploader
        uploader = FileUploadComponent()
        uploaded_file_path = uploader.render()
        
        if uploaded_file_path:
            st.session_state.current_document = uploaded_file_path
            
            st.divider()
            
            # Pulsante generazione
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("🚀 Genera Presentazione", type="primary", use_container_width=True):
                    generate_presentation()
            
            # Download presentazione se disponibile
            if 'last_presentation' in st.session_state:
                st.divider()
                st.success("✅ Presentazione pronta per il download!")
                
                with open(st.session_state.last_presentation, 'rb') as f:
                    st.download_button(
                        label="📥 Scarica Presentazione (PPTX)",
                        data=f,
                        file_name=st.session_state.last_presentation.name,
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True
                    )
    
    with tab2:
        # Chat interface
        chat = ChatInterface(st.session_state.ollama_client)
        chat.render()


def generate_presentation():
    """Genera la presentazione"""
    from modules.presentation_generator import PresentationGenerator
    
    if not st.session_state.current_document:
        st.error("⚠️ Carica prima un documento!")
        return
    
    try:
        with st.spinner("🔄 Analisi documento e generazione presentazione..."):
            # Crea generator
            generator = PresentationGenerator(st.session_state.ollama_client)
            
            # Progress steps
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Parsing
            status_text.text("📄 Parsing documento...")
            progress_bar.progress(25)
            
            # Step 2: Generazione contenuto
            status_text.text("🤖 Generazione contenuto con AI...")
            progress_bar.progress(50)
            
            presentation_data = generator.generate_presentation_content(
                st.session_state.current_document,
                model=st.session_state.get('selected_model', config.DEFAULT_MODEL)
            )
            
            if 'error' in presentation_data:
                st.error(f"❌ Errore: {presentation_data['error']}")
                return
            
            # Step 3: Creazione PPTX
            status_text.text("📊 Creazione file PowerPoint...")
            progress_bar.progress(75)
            
            output_filename = f"presentazione_{st.session_state.current_document.stem}.pptx"
            output_path = config.OUTPUT_DIR / output_filename
            
            generator.create_pptx(presentation_data, output_path)
            
            # Step 4: Completato
            progress_bar.progress(100)
            status_text.text("✅ Completato!")
            
            # Salva in session state
            st.session_state.last_presentation = output_path
            
            # Mostra riepilogo
            st.success("🎉 Presentazione generata con successo!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📑 Slide", len(presentation_data.get('slides', [])))
            with col2:
                st.metric("🖼️ Immagini", len(presentation_data.get('metadata', {}).get('images', [])))
            with col3:
                words = presentation_data.get('metadata', {}).get('word_count', 0)
                st.metric("📝 Parole fonte", f"{words:,}")
            
            st.balloons()
    
    except Exception as e:
        st.error(f"❌ Errore durante la generazione: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
