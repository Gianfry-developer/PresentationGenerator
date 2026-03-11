"""
Componente per upload file
"""

import streamlit as st
from pathlib import Path
import config


class FileUploadComponent:
    """Componente per upload documenti"""
    
    def render(self):
        """Renderizza il componente upload"""
        st.header("📁 Carica Documento")
        
        uploaded_file = st.file_uploader(
            "Scegli un file DOCX, LaTeX o Markdown",
            type=['docx', 'tex', 'md', 'markdown'],
            help="Formati supportati: DOCX, LaTeX (.tex), Markdown (.md)"
        )
        
        if uploaded_file:
            # Salva il file
            file_path = config.UPLOAD_DIR / uploaded_file.name
            
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ File caricato: {uploaded_file.name}")
            
            # Mostra info file
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Nome", uploaded_file.name)
            with col2:
                st.metric("Dimensione", f"{uploaded_file.size / 1024:.1f} KB")
            with col3:
                st.metric("Tipo", file_path.suffix[1:].upper())
            
            return file_path
        
        return None
