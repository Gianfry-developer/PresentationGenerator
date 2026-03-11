"""
Interfaccia chat simile a NotebookLM
"""

import streamlit as st
from typing import List, Dict
from modules.ollama_client import OllamaClient
from modules.presentation_generator import PresentationGenerator
import config


class ChatInterface:
    """Interfaccia chat per interazione con l'utente"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.generator = PresentationGenerator(ollama_client)
        
        # Inizializza session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'current_document' not in st.session_state:
            st.session_state.current_document = None
    
    def render(self):
        """Renderizza l'interfaccia chat"""
        st.header("💬 Chat Assistente")
        
        # Mostra storico messaggi
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input utente
        if prompt := st.chat_input("Chiedi qualcosa o chiedi di generare la presentazione..."):
            # Aggiungi messaggio utente
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Genera risposta
            with st.chat_message("assistant"):
                response = self._generate_response(prompt)
                st.markdown(response)
            
            # Aggiungi risposta allo storico
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
    
    def _generate_response(self, user_message: str) -> str:
        """Genera risposta usando Ollama"""
        
        # Rileva intent
        if any(keyword in user_message.lower() for keyword in ['genera', 'crea', 'presentazione', 'slides']):
            return self._handle_generation_request(user_message)
        
        # Chat normale
        messages = [
            {"role": "system", "content": config.CHAT_SYSTEM_PROMPT}
        ]
        
        # Aggiungi storico (ultimi 5 messaggi)
        for msg in st.session_state.messages[-5:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Aggiungi messaggio corrente
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Genera risposta
        model = st.session_state.get('selected_model', config.DEFAULT_MODEL)
        response = self.ollama_client.chat(messages=messages, model=model)
        
        if hasattr(response, 'message'):
            return response.message.content
        else:
            return response.get('message', {}).get('content', 'Errore nella generazione della risposta')
    
    def _handle_generation_request(self, user_message: str) -> str:
        """Gestisce richiesta di generazione presentazione"""
        
        if not st.session_state.current_document:
            return "⚠️ Devi prima caricare un documento usando la sezione 'Carica Documento'."
        
        try:
            with st.spinner("🔄 Generazione presentazione in corso..."):
                # Genera contenuto
                presentation_data = self.generator.generate_presentation_content(
                    st.session_state.current_document,
                    model=st.session_state.get('selected_model', config.DEFAULT_MODEL)
                )
                
                if 'error' in presentation_data:
                    return f"❌ Errore: {presentation_data['error']}"
                
                # Crea PPTX
                output_filename = f"presentazione_{st.session_state.current_document.stem}.pptx"
                output_path = config.OUTPUT_DIR / output_filename
                
                self.generator.create_pptx(presentation_data, output_path)
                
                # Salva in session state per download
                st.session_state.last_presentation = output_path
                
                return f"""✅ **Presentazione generata con successo!**

📊 **Dettagli:**
- Titolo: {presentation_data.get('title', 'N/A')}
- Numero di slide: {len(presentation_data.get('slides', []))}
- Immagini incluse: {len(presentation_data.get('metadata', {}).get('images', []))}

📥 Usa il pulsante qui sotto per scaricare la presentazione."""
        
        except Exception as e:
            return f"❌ Errore durante la generazione: {str(e)}"
