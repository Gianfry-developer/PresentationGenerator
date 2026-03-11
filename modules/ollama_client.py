"""
Client per comunicazione con Ollama
"""

import json
from typing import Dict, List, Optional, Generator
import ollama
from ollama import ChatResponse


class OllamaClient:
    """Client per interagire con Ollama"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.client = ollama.Client(host=host)
    
    def list_models(self) -> List[str]:
        """Lista dei modelli disponibili localmente"""
        try:
            models = self.client.list()
            return [model['name'] for model in models.get('models', [])]
        except Exception as e:
            print(f"Errore nel recupero modelli: {e}")
            return []
    
    def pull_model(self, model_name: str) -> Generator[Dict, None, None]:
        """
        Scarica un modello da Ollama
        
        Yields:
            Dict con status del download
        """
        try:
            for progress in self.client.pull(model_name, stream=True):
                yield progress
        except Exception as e:
            yield {"error": str(e)}
    
    def is_model_available(self, model_name: str) -> bool:
        """Verifica se un modello è disponibile"""
        models = self.list_models()
        # Confronta anche senza tag di versione
        base_name = model_name.split(':')[0]
        return any(base_name in m for m in models)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama3.2",
        stream: bool = False,
        format: Optional[str] = None
    ) -> ChatResponse | Generator[Dict, None, None]:
        """
        Invia messaggi alla chat
        
        Args:
            messages: Lista di messaggi con 'role' e 'content'
            model: Nome del modello da usare
            stream: Se True, restituisce generator per streaming
            format: Se 'json', forza output JSON
        """
        try:
            options = {}
            if format == 'json':
                options['format'] = 'json'
            
            if stream:
                return self.client.chat(
                    model=model,
                    messages=messages,
                    stream=True,
                    **options
                )
            else:
                response = self.client.chat(
                    model=model,
                    messages=messages,
                    stream=False,
                    **options
                )
                return response
        
        except Exception as e:
            print(f"Errore nella chat: {e}")
            if stream:
                def error_gen():
                    yield {"error": str(e)}
                return error_gen()
            else:
                return {"error": str(e)}
    
    def generate(
        self,
        prompt: str,
        model: str = "llama3.2",
        system: Optional[str] = None,
        stream: bool = False,
        format: Optional[str] = None
    ) -> Dict | Generator[Dict, None, None]:
        """
        Genera testo da un prompt
        
        Args:
            prompt: Prompt di input
            model: Nome del modello
            system: System prompt opzionale
            stream: Se True, restituisce generator
            format: Se 'json', forza output JSON
        """
        try:
            options = {}
            if format == 'json':
                options['format'] = 'json'
            if system:
                options['system'] = system
            
            response = self.client.generate(
                model=model,
                prompt=prompt,
                stream=stream,
                **options
            )
            
            return response
        
        except Exception as e:
            print(f"Errore nella generazione: {e}")
            if stream:
                def error_gen():
                    yield {"error": str(e)}
                return error_gen()
            else:
                return {"error": str(e)}
