from typing import Optional, List, Dict, Any
import inspect
import sys
from pathlib import Path
import json

class APIDocGenerator:
    """Генератор документации API."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_module_docs(self, module_name: str) -> Dict[str, Any]:
        """Генерирует документацию для модуля.
        
        Args:
            module_name: Имя модуля для документирования
            
        Returns:
            Словарь с документацией модуля
        """
        try:
            module = sys.modules[module_name]
        except KeyError:
            return {"error": f"Module {module_name} not found"}
            
        doc_data = {
            "name": module_name,
            "description": module.__doc__ or "",
            "classes": self._document_classes(module),
            "functions": self._document_functions(module)
        }
        
        return doc_data
    
    def _document_classes(self, module: Any) -> List[Dict[str, Any]]:
        """Документирует классы модуля."""
        classes = []
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ != module.__name__:
                continue
                
            class_doc = {
                "name": name,
                "description": obj.__doc__ or "",
                "methods": self._document_methods(obj),
                "attributes": self._document_attributes(obj)
            }
            classes.append(class_doc)
            
        return classes
    
    def _document_methods(self, cls: Any) -> List[Dict[str, Any]]:
        """Документирует методы класса."""
        methods = []
        
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            if name.startswith('_') and name != '__init__':
                continue
                
            method_doc = {
                "name": name,
                "description": method.__doc__ or "",
                "parameters": self._document_parameters(method),
                "returns": self._document_return(method)
            }
            methods.append(method_doc)
            
        return methods
    
    def _document_attributes(self, cls: Any) -> List[Dict[str, str]]:
        """Документирует атрибуты класса."""
        attributes = []
        
        for name, value in vars(cls).items():
            if not name.startswith('_'):
                attributes.append({
                    "name": name,
                    "type": str(type(value).__name__)
                })
                
        return attributes
    
    def _document_functions(self, module: Any) -> List[Dict[str, Any]]:
        """Документирует функции модуля."""
        functions = []
        
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if func.__module__ != module.__name__:
                continue
                
            func_doc = {
                "name": name,
                "description": func.__doc__ or "",
                "parameters": self._document_parameters(func),
                "returns": self._document_return(func)
            }
            functions.append(func_doc)
            
        return functions
    
    def _document_parameters(self, func: Any) -> List[Dict[str, str]]:
        """Документирует параметры функции."""
        params = []
        signature = inspect.signature(func)
        
        for name, param in signature.parameters.items():
            param_doc = {
                "name": name,
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                "default": str(param.default) if param.default != inspect.Parameter.empty else None
            }
            params.append(param_doc)
            
        return params
    
    def _document_return(self, func: Any) -> Optional[str]:
        """Документирует возвращаемое значение функции."""
        signature = inspect.signature(func)
        if signature.return_annotation != inspect.Parameter.empty:
            return str(signature.return_annotation)
        return None
    
    def save_documentation(self, module_name: str) -> None:
        """Сохраняет документацию в JSON файл."""
        doc_data = self.generate_module_docs(module_name)
        output_file = self.output_dir / f"{module_name}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)
            
    def generate_markdown(self, module_name: str) -> str:
        """Генерирует Markdown документацию."""
        doc_data = self.generate_module_docs(module_name)
        md_content = [f"# {doc_data['name']}\n"]
        
        if doc_data["description"]:
            md_content.append(f"{doc_data['description']}\n")
            
        if doc_data["classes"]:
            md_content.append("## Classes\n")
            for class_doc in doc_data["classes"]:
                md_content.append(self._class_to_markdown(class_doc))
                
        if doc_data["functions"]:
            md_content.append("## Functions\n")
            for func_doc in doc_data["functions"]:
                md_content.append(self._function_to_markdown(func_doc))
                
        return "\n".join(md_content)
    
    def _class_to_markdown(self, class_doc: Dict[str, Any]) -> str:
        """Конвертирует документацию класса в Markdown."""
        md_parts = [f"### {class_doc['name']}\n"]
        
        if class_doc["description"]:
            md_parts.append(f"{class_doc['description']}\n")
            
        if class_doc["attributes"]:
            md_parts.append("#### Attributes\n")
            for attr in class_doc["attributes"]:
                md_parts.append(f"- `{attr['name']}`: {attr['type']}\n")
                
        if class_doc["methods"]:
            md_parts.append("#### Methods\n")
            for method in class_doc["methods"]:
                md_parts.append(self._function_to_markdown(method, is_method=True))
                
        return "\n".join(md_parts)
    
    def _function_to_markdown(self, func_doc: Dict[str, Any], is_method: bool = False) -> str:
        """Конвертирует документацию функции в Markdown."""
        prefix = "##### " if is_method else "### "
        md_parts = [f"{prefix}{func_doc['name']}\n"]
        
        if func_doc["description"]:
            md_parts.append(f"{func_doc['description']}\n")
            
        if func_doc["parameters"]:
            md_parts.append("Parameters:\n")
            for param in func_doc["parameters"]:
                default = f" = {param['default']}" if param['default'] else ""
                md_parts.append(f"- `{param['name']}`: {param['type']}{default}\n")
                
        if func_doc["returns"]:
            md_parts.append(f"Returns: {func_doc['returns']}\n")
            
        return "\n".join(md_parts)