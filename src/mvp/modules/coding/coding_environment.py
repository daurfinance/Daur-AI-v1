"""
Coding Environment - Local Code Generation and Execution
Creates, saves, and runs code projects locally
"""

import logging
import subprocess
from typing import Optional, List, Dict
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger(__name__)


class CodingEnvironment:
    """Manage local coding projects"""
    
    def __init__(self, workspace_dir: Optional[str] = None):
        """
        Initialize coding environment
        
        Args:
            workspace_dir: Directory for projects (defaults to ~/daur_projects)
        """
        if workspace_dir:
            self.workspace = Path(workspace_dir)
        else:
            self.workspace = Path.home() / "daur_projects"
        
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # Get LLM for code generation
        from ...core.ollama_client import get_ollama_client
        self.llm = get_ollama_client()
        
        logger.info(f"Coding environment initialized: {self.workspace}")
    
    def create_project(self, project_name: str, language: str = "python") -> Path:
        """
        Create new project directory
        
        Args:
            project_name: Name of project
            language: Programming language
            
        Returns:
            Path to project directory
        """
        project_dir = self.workspace / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic structure based on language
        if language == "python":
            (project_dir / "src").mkdir(exist_ok=True)
            (project_dir / "tests").mkdir(exist_ok=True)
            
            # Create README
            readme = project_dir / "README.md"
            readme.write_text(f"# {project_name}\n\nPython project created by Daur AI\n")
            
            # Create requirements.txt
            requirements = project_dir / "requirements.txt"
            requirements.write_text("# Python dependencies\n")
        
        elif language == "javascript" or language == "node":
            (project_dir / "src").mkdir(exist_ok=True)
            
            # Create package.json
            package_json = project_dir / "package.json"
            package_json.write_text(f'''{{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "Node.js project created by Daur AI",
  "main": "src/index.js",
  "scripts": {{
    "start": "node src/index.js"
  }}
}}
''')
        
        logger.info(f"Created project: {project_dir}")
        return project_dir
    
    def generate_code(self, task_description: str, language: str = "python") -> str:
        """
        Generate code using local LLM
        
        Args:
            task_description: What the code should do
            language: Programming language
            
        Returns:
            Generated code
        """
        logger.info(f"Generating {language} code for: {task_description}")
        
        code = self.llm.generate_code(task_description, language)
        
        # Clean up code (remove markdown formatting if present)
        if code.startswith('```'):
            lines = code.split('\n')
            # Remove first and last lines (markdown code blocks)
            code = '\n'.join(lines[1:-1])
        
        return code
    
    def save_code(self, project_dir: Path, filename: str, code: str) -> Path:
        """
        Save code to file
        
        Args:
            project_dir: Project directory
            filename: Filename (e.g., "main.py")
            code: Code content
            
        Returns:
            Path to saved file
        """
        # Determine subdirectory based on filename
        if filename.endswith('.py'):
            file_path = project_dir / "src" / filename
        elif filename.endswith('.js'):
            file_path = project_dir / "src" / filename
        else:
            file_path = project_dir / filename
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(code)
        
        logger.info(f"Saved code: {file_path}")
        return file_path
    
    def run_python(self, file_path: Path) -> Dict[str, any]:
        """
        Run Python file
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dict with 'success', 'output', 'error'
        """
        try:
            result = subprocess.run(
                ['python3', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=file_path.parent
            )
            
            success = result.returncode == 0
            
            logger.info(f"Ran Python file: {file_path} (success={success})")
            
            return {
                'success': success,
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode
            }
        
        except subprocess.TimeoutExpired:
            logger.error(f"Python execution timeout: {file_path}")
            return {
                'success': False,
                'output': '',
                'error': 'Execution timeout (30s)',
                'returncode': -1
            }
        
        except Exception as e:
            logger.error(f"Python execution error: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'returncode': -1
            }
    
    def run_node(self, file_path: Path) -> Dict[str, any]:
        """
        Run Node.js file
        
        Args:
            file_path: Path to JavaScript file
            
        Returns:
            Dict with 'success', 'output', 'error'
        """
        try:
            result = subprocess.run(
                ['node', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=file_path.parent
            )
            
            success = result.returncode == 0
            
            logger.info(f"Ran Node.js file: {file_path} (success={success})")
            
            return {
                'success': success,
                'output': result.stdout,
                'error': result.stderr,
                'returncode': result.returncode
            }
        
        except Exception as e:
            logger.error(f"Node.js execution error: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'returncode': -1
            }
    
    def install_dependencies(self, project_dir: Path, language: str = "python") -> bool:
        """
        Install project dependencies
        
        Args:
            project_dir: Project directory
            language: Programming language
            
        Returns:
            True if successful
        """
        try:
            if language == "python":
                requirements = project_dir / "requirements.txt"
                if requirements.exists():
                    result = subprocess.run(
                        ['pip3', 'install', '-r', str(requirements)],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode == 0:
                        logger.info("Python dependencies installed")
                        return True
                    else:
                        logger.error(f"Dependency installation failed: {result.stderr}")
                        return False
            
            elif language == "javascript" or language == "node":
                package_json = project_dir / "package.json"
                if package_json.exists():
                    result = subprocess.run(
                        ['npm', 'install'],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        cwd=project_dir
                    )
                    
                    if result.returncode == 0:
                        logger.info("Node.js dependencies installed")
                        return True
                    else:
                        logger.error(f"Dependency installation failed: {result.stderr}")
                        return False
            
            return True
        
        except Exception as e:
            logger.error(f"Dependency installation error: {e}")
            return False
    
    def create_and_run_project(
        self,
        project_name: str,
        task_description: str,
        language: str = "python"
    ) -> Dict[str, any]:
        """
        Complete workflow: create project, generate code, save, and run
        
        Args:
            project_name: Name of project
            task_description: What the code should do
            language: Programming language
            
        Returns:
            Dict with project info and execution result
        """
        # Create project
        project_dir = self.create_project(project_name, language)
        
        # Generate code
        code = self.generate_code(task_description, language)
        
        if not code:
            return {
                'success': False,
                'error': 'Code generation failed',
                'project_dir': str(project_dir)
            }
        
        # Save code
        if language == "python":
            filename = "main.py"
        elif language == "javascript" or language == "node":
            filename = "index.js"
        else:
            filename = "main.txt"
        
        file_path = self.save_code(project_dir, filename, code)
        
        # Run code
        if language == "python":
            result = self.run_python(file_path)
        elif language == "javascript" or language == "node":
            result = self.run_node(file_path)
        else:
            result = {
                'success': False,
                'error': f'Unsupported language: {language}'
            }
        
        return {
            **result,
            'project_dir': str(project_dir),
            'file_path': str(file_path),
            'code': code
        }
    
    def list_projects(self) -> List[str]:
        """List all projects in workspace"""
        projects = [d.name for d in self.workspace.iterdir() if d.is_dir()]
        return projects
    
    def delete_project(self, project_name: str) -> bool:
        """Delete project"""
        project_dir = self.workspace / project_name
        
        if project_dir.exists():
            shutil.rmtree(project_dir)
            logger.info(f"Deleted project: {project_name}")
            return True
        
        return False


def get_coding_environment() -> CodingEnvironment:
    """Get coding environment instance"""
    return CodingEnvironment()

