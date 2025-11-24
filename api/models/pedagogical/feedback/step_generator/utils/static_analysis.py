import ast

def is_only_pass(node):
    """
    Check if the given AST node contains only a 'pass' statement.
    """
    node_name = type(node).__name__
    if isinstance(node, ast.Module):
        # For a module, check if it has only one statement which is a 'pass'
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            return True
        return False
    elif isinstance(node, ast.Pass):
        return True
    elif node_name in ["For", "While", "If", "With", "AsyncFor", "AsyncWith",
                             "ClassDef", "AsyncFunctionDef", "FunctionDef", 
                             "Try", "ExceptHandler", "TryStar"]:
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            return True
        else:
            return False
    else:
        return False

def get_control_list(parsed_state):
    
    class StructuresVisitor(ast.NodeVisitor):

        structures_list = []

        def visit(self, node):
            node_name = type(node).__name__
            if node_name in ["For", "While", "If", "With", "AsyncFor", "AsyncWith",
                             "ClassDef", "AsyncFunctionDef", "FunctionDef", 
                             "Try", "ExceptHandler", "TryStar"]:
                start_lino = node.lineno
                end_lino = node.end_lineno
                is_empty = is_only_pass(node)
                self.structures_list.append((node_name, start_lino, end_lino, is_empty))
            return super().visit(node)
        
    visitor = StructuresVisitor()
    visitor.visit(parsed_state)
    return visitor.structures_list

def has_empty_control_structure(control_list):
    for control in control_list:
        if control[3]:
            return True
    return False
