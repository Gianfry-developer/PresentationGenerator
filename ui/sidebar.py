"""
Componente Sidebar per configurazioni
"""

import streamlit as st
from modules.ollama_client import OllamaClient
import config


class SidebarComponent:
    """Sidebar con configurazioni"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
    
    def render(self):
        """Renderizza la sidebar"""
        with st.sidebar:
            st.title("⚙️ Configurazioni")
            
            # Sezione Ollama
            st.header("🤖 Ollama")
            
            # Stato connessione
            models = self.ollama_client.list_models()
            if models:
                st.success(f"✅ Connesso ({len(models)} modelli)")
            else:
                st.error("❌ Ollama non raggiungibile")
                st.info(f"Verifica che Ollama sia in esecuzione su {config.OLLAMA_HOST}")
            
            # Selezione modello
            if models:
                selected_model = st.selectbox(
                    "Modello attivo",
                    options=models,
                    index=0 if models else None
                )
                st.session_state['selected_model'] = selected_model
            else:
                st.session_state['selected_model'] = config.DEFAULT_MODEL
            
            # Installazione nuovo modello
            st.subheader("📥 Installa nuovo modello")
            
            model_to_install = st.text_input(
                "Nome modello",
                placeholder="es: llama3.2, mistral, codellama"
            )
            
            if st.button("Installa modello", type="primary"):
                if model_to_install:
                    self._install_model(model_to_install)
                else:
                    st.warning("Inserisci un nome modello")
            
            # Parametri presentazione
            st.header("📊 Parametri Presentazione")
            
            duration = st.slider(
                "Durata target (minuti)",
                min_value=5,
                max_value=30,
                value=config.TARGET_PRESENTATION_MINUTES,
                step=1
            )
            st.session_state['presentation_duration'] = duration
            
            wpm = st.slider(
                "Parole per minuto",
                min_value=100,
                max_value=160,
                value=config.WORDS_PER_MINUTE,
                step=10
            )
            st.session_state['words_per_minute'] = wpm
            
            # Calcola parole target
            target_words = duration * wpm
            st.info(f"📝 Target: ~{target_words} parole\n\n📑 Slides stimato: ~{target_words // 100}")
            
            # Info
            st.divider()
            st.caption("Presentation Generator v1.0")
            st.caption(f"Powered by Ollama")
    
    def _install_model(self, model_name: str):
        """Installa un modello con progress bar"""
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        with st.spinner(f"Download {model_name} in corso..."):
            try:
                for progress in self.ollama_client.pull_model(model_name):
                    if 'error' in progress:
                        st.error(f"Errore: {progress['error']}")
                        return
                    
                    if 'status' in progress:
                        status_placeholder.text(progress['status'])
                    
                    if 'completed' in progress and 'total' in progress:
                        percent = progress['completed'] / progress['total']
                        progress_placeholder.progress(percent)
                
                st.success(f"✅ Modello {model_name} installato!")
                st.rerun()
            
            except Exception as e:
                st.error(f"Errore installazione: {e}")
