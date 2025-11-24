import numpy as np
import ast
from models.pedagogical.feedback.step_generator.state_space.base_state_space import Base_state_space

class Rule_based_state_space(Base_state_space):


    def state_encoding(self, code: str) -> str:
        return self.blind_names(code)
    
    def blind_names(self, code: str) -> str:
        variables, classes, functions = self.extract_names(code)
        reserved_words = ["False",	"def",	"if", "raise", "None", "del", "import", "return",
            "True", "elif", "in", "try", "and", "else", "is", "while", "as", "except", "lambda", "with",
                "assert", "finally", "nonlocal", "yield", "break", "for", "not", "class", "form", "or", "continue", "global", "pass"]
        for var in variables:
            # Handle same initial letter for vars 
            if var not in reserved_words:
                code = self.refactor_variable(var, "v", code)
        for _class in classes:
            if _class not in reserved_words:
                code = self.refactor_variable(_class, "c", code)
        for f in functions:
            if f not in reserved_words:
                code = self.refactor_variable(f, "f", code)
        return code
    
    
    def refactor_variable(self, old_name: str, new_name: str, program_str: str) -> str:
        tree = ast.parse(program_str)
        transformer = SimpleRenamer(old_name, new_name)
        modified_tree = transformer.visit(tree)
        return ast.unparse(modified_tree)

    def extract_names(self, source_code: str) -> tuple[list]:
        """Extract names of three kinds (variables, classes, functions) from a python code snippet.

        Args:
            source_code (_type_): _description_

        Returns:
            _type_: _description_
        """
        tree = ast.parse(source_code)
        
        variables = []
        classes = []
        functions = []

        def collect_names(target):
            if isinstance(target, ast.Name):
                variables.append(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    collect_names(elt)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
                
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
                
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    collect_names(target)
                    
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                collect_names(node.target)
                
            # Don't Handle imports, because they are not user generated in the ITS
            #elif isinstance(node, ast.Import):
            #    for alias in node.names:
            #        variables.append(alias.asname or alias.name.split('.')[0])
                    
            #elif isinstance(node, ast.ImportFrom):
            #    for alias in node.names:
            #        if alias.name != '*':
            #            variables.append(alias.asname or alias.name)
                        
        return variables, classes, functions


class SimpleRenamer(ast.NodeTransformer):
    def __init__(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name
        
    def visit_Name(self, node):
        if node.id == self.old_name:
            node.id = self.new_name
        return node
    
    def visit_Attribute(self, node):
        if node.attr == self.old_name:
            node.attr = self.new_name
        self.generic_visit(node)
        return node
    
    def visit_arg(self, node):
        if node.arg == self.old_name:
            node.arg = self.new_name
        return node
    
    def visit_FunctionDef(self, node):
        if node.name == self.old_name:
            node.name = self.new_name
        self.generic_visit(node)
        return node
    
    def visit_ClassDef(self, node):
        if node.name == self.old_name:
            node.name = self.new_name
        self.generic_visit(node)
        return node
    
    def visit_Global(self, node):
        node.names = [self.new_name if n == self.old_name else n for n in node.names]
        return node
    
    def visit_Nonlocal(self, node):
        node.names = [self.new_name if n == self.old_name else n for n in node.names]
        return node
    
    # Don't Handle imports, because they are not user generated in the ITS
    #def visit_Import(self, node):
    #    for alias in node.names:
    #        if alias.asname == self.old_name:
    #            alias.asname = self.new_name
    #        elif alias.asname is None and alias.name == self.old_name:
    #            alias.asname = self.new_name
    #    return node
    
    #def visit_ImportFrom(self, node):
    #    for alias in node.names:
    #        if alias.asname == self.old_name:
    #            alias.asname = self.new_name
    #        elif alias.asname is None and alias.name == self.old_name:
    #            alias.asname = self.new_name
    #    return node

