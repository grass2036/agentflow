"""
Code Generation Plugin
======================

An example plugin that provides code generation capabilities.
"""

from typing import Any, Dict
import logging

from agentflow.plugins.base import TaskPlugin, PluginMetadata, PluginContext

logger = logging.getLogger(__name__)


class CodeGenPlugin(TaskPlugin):
    """Plugin for generating code snippets."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="codegen",
            version="1.0.0",
            description="Generate code snippets for common programming patterns",
            author="AgentFlow Team",
            homepage="https://github.com/agentflow/agentflow",
            tags=["codegen", "templates", "productivity"],
            supports_async=True
        )
        
    async def initialize(self) -> None:
        """Initialize the code generation plugin."""
        logger.info("Initializing CodeGen plugin")
        self.templates = {
            "python_class": self._python_class_template,
            "python_function": self._python_function_template,
            "javascript_component": self._javascript_component_template,
            "api_endpoint": self._api_endpoint_template
        }
        self.register_hook("generate_code")
        self.register_hook("list_templates")
        
    async def cleanup(self) -> None:
        """Cleanup plugin resources."""
        logger.info("Cleaning up CodeGen plugin")
        self.templates.clear()
        
    async def process_task(self, context: PluginContext) -> Any:
        """Process a code generation task."""
        task_data = context.data
        
        if "template" not in task_data:
            raise ValueError("Template name is required")
            
        template_name = task_data["template"]
        params = task_data.get("params", {})
        
        if template_name not in self.templates:
            available = list(self.templates.keys())
            raise ValueError(f"Template '{template_name}' not found. Available: {available}")
            
        # Generate code using template
        code = self.templates[template_name](params)
        
        return {
            "generated_code": code,
            "template_used": template_name,
            "language": self._get_language_for_template(template_name)
        }
        
    async def pre_task_execution(self, context: PluginContext) -> Dict[str, Any]:
        """Enhance context with code generation capabilities."""
        if context.data.get("task_type") == "code_generation":
            return {
                "codegen_available": True,
                "available_templates": list(self.templates.keys())
            }
        return {}
        
    def _python_class_template(self, params: Dict[str, Any]) -> str:
        """Generate a Python class template."""
        class_name = params.get("class_name", "MyClass")
        base_class = params.get("base_class", "")
        methods = params.get("methods", ["__init__"])
        
        base_part = f"({base_class})" if base_class else ""
        
        code = f'''class {class_name}{base_part}:
    """A {class_name} class."""
    
'''
        
        for method in methods:
            if method == "__init__":
                code += f'''    def __init__(self):
        """Initialize {class_name}."""
        super().__init__()
        
'''
            else:
                code += f'''    def {method}(self):
        """Implement {method}."""
        pass
        
'''
        
        return code.rstrip()
        
    def _python_function_template(self, params: Dict[str, Any]) -> str:
        """Generate a Python function template."""
        func_name = params.get("function_name", "my_function")
        args = params.get("args", [])
        return_type = params.get("return_type", "None")
        async_func = params.get("async", False)
        
        async_keyword = "async " if async_func else ""
        args_str = ", ".join(args) if args else ""
        
        code = f'''{async_keyword}def {func_name}({args_str}) -> {return_type}:
    """Implement {func_name}."""
    pass'''
        
        return code
        
    def _javascript_component_template(self, params: Dict[str, Any]) -> str:
        """Generate a JavaScript/React component template."""
        component_name = params.get("component_name", "MyComponent")
        props = params.get("props", [])
        
        props_str = "{ " + ", ".join(props) + " }" if props else ""
        
        code = f'''import React from 'react';

const {component_name} = ({props_str}) => {{
  return (
    <div className="{component_name.lower()}">
      <h1>{component_name}</h1>
    </div>
  );
}};

export default {component_name};'''
        
        return code
        
    def _api_endpoint_template(self, params: Dict[str, Any]) -> str:
        """Generate an API endpoint template."""
        endpoint_name = params.get("endpoint_name", "my_endpoint")
        method = params.get("method", "GET").upper()
        path = params.get("path", f"/{endpoint_name}")
        
        if method == "GET":
            code = f'''@app.route('{path}', methods=['{method}'])
def {endpoint_name}():
    """Handle {method} request for {path}."""
    try:
        # Implement your logic here
        return jsonify({{"message": "Success"}}), 200
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500'''
        else:
            code = f'''@app.route('{path}', methods=['{method}'])
def {endpoint_name}():
    """Handle {method} request for {path}."""
    try:
        data = request.get_json()
        # Implement your logic here
        return jsonify({{"message": "Success", "data": data}}), 200
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500'''
        
        return code
        
    def _get_language_for_template(self, template_name: str) -> str:
        """Get programming language for a template."""
        language_map = {
            "python_class": "python",
            "python_function": "python", 
            "javascript_component": "javascript",
            "api_endpoint": "python"
        }
        return language_map.get(template_name, "text")
        
    async def generate_code(self, context: PluginContext, template: str, params: Dict[str, Any]) -> str:
        """Public API to generate code."""
        if template not in self.templates:
            raise ValueError(f"Template '{template}' not found")
            
        return self.templates[template](params)
        
    async def list_templates(self, context: PluginContext) -> Dict[str, Any]:
        """List available code templates."""
        return {
            "templates": list(self.templates.keys()),
            "total_count": len(self.templates),
            "plugin_name": self.metadata.name,
            "plugin_version": self.metadata.version
        }