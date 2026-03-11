"""
Estrattore di immagini da documenti
"""

import io
import zipfile
from pathlib import Path
from typing import List, Dict
from PIL import Image
import docx


class ImageExtractor:
    """Estrae immagini da documenti"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def extract_from_docx(self, file_path: Path) -> List[Dict]:
        """
        Estrae immagini da file DOCX
        
        Returns:
            Lista di dict con 'filename', 'path', 'size'
        """
        images = []
        
        try:
            # Metodo 1: usando docx2txt (più semplice)
            import docx2txt
            text = docx2txt.process(str(file_path), str(self.output_dir))
            
            # Conta le immagini estratte
            for img_file in self.output_dir.glob("image*.png"):
                images.append({
                    "filename": img_file.name,
                    "path": str(img_file),
                    "size": img_file.stat().st_size
                })
            
            # Metodo 2: estrazione manuale dal ZIP se il primo metodo fallisce
            if not images:
                images = self._extract_from_docx_zip(file_path)
            
        except Exception as e:
            print(f"Errore nell'estrazione immagini: {e}")
            images = []
        
        return images
    
    def _extract_from_docx_zip(self, file_path: Path) -> List[Dict]:
        """Estrae immagini direttamente dal file DOCX (che è uno ZIP)"""
        images = []
        
        try:
            with zipfile.ZipFile(file_path, 'r') as docx_zip:
                # Le immagini sono in word/media/
                for file_info in docx_zip.namelist():
                    if file_info.startswith('word/media/'):
                        # Estrai l'immagine
                        img_data = docx_zip.read(file_info)
                        img_name = Path(file_info).name
                        
                        # Salva l'immagine
                        output_path = self.output_dir / img_name
                        with open(output_path, 'wb') as f:
                            f.write(img_data)
                        
                        images.append({
                            "filename": img_name,
                            "path": str(output_path),
                            "size": len(img_data)
                        })
        
        except Exception as e:
            print(f"Errore nell'estrazione ZIP: {e}")
        
        return images
    
    def extract_from_latex(self, file_path: Path) -> List[Dict]:
        """
        Estrae riferimenti a immagini da LaTeX
        (cerca i comandi \includegraphics)
        """
        images = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            # Cerca pattern \includegraphics{filename}
            pattern = r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}'
            
            for match in re.finditer(pattern, content):
                img_filename = match.group(1)
                
                # Cerca il file nella stessa directory
                latex_dir = file_path.parent
                possible_paths = [
                    latex_dir / img_filename,
                    latex_dir / f"{img_filename}.png",
                    latex_dir / f"{img_filename}.jpg",
                    latex_dir / f"{img_filename}.pdf"
                ]
                
                for img_path in possible_paths:
                    if img_path.exists():
                        # Copia l'immagine nella directory output
                        output_path = self.output_dir / img_path.name
                        
                        import shutil
                        shutil.copy(img_path, output_path)
                        
                        images.append({
                            "filename": img_path.name,
                            "path": str(output_path),
                            "size": img_path.stat().st_size
                        })
                        break
        
        except Exception as e:
            print(f"Errore nell'estrazione immagini LaTeX: {e}")
        
        return images
    
    def extract_from_markdown(self, file_path: Path) -> List[Dict]:
        """
        Estrae riferimenti a immagini da Markdown
        (cerca pattern ![alt](path))
        """
        images = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            # Cerca pattern ![alt](path)
            pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
            
            md_dir = file_path.parent
            
            for match in re.finditer(pattern, content):
                img_path_str = match.group(2)
                
                # Gestisci path relativi
                if not img_path_str.startswith('http'):
                    img_path = md_dir / img_path_str
                    
                    if img_path.exists():
                        # Copia l'immagine
                        output_path = self.output_dir / img_path.name
                        
                        import shutil
                        shutil.copy(img_path, output_path)
                        
                        images.append({
                            "filename": img_path.name,
                            "path": str(output_path),
                            "size": img_path.stat().st_size
                        })
        
        except Exception as e:
            print(f"Errore nell'estrazione immagini Markdown: {e}")
        
        return images
    
    def extract_images(self, file_path: Path) -> List[Dict]:
        """Estrae immagini in base al formato del file"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.docx':
            return self.extract_from_docx(file_path)
        elif suffix == '.tex':
            return self.extract_from_latex(file_path)
        elif suffix in ['.md', '.markdown']:
            return self.extract_from_markdown(file_path)
        else:
            return []
