import ast
from models.pedagogical.feedback.step_generator.utils import tree
from edist.ted import standard_ted



def ast_to_tree(ast_node):
    """ Converts a Python abstract syntax tree as returned by the Python
    compiler into a tree.Tree

    Parameters
    ----------
    ast_node: class ast.AST
        An abstract syntax tree in Pythons internal compiler format.

    Returns
    -------
    x: class tree.Tree
        A tree object according to the tree.Tree class. At each node, we
        additionally annotate variable references.

    """

    label = ast_node.__class__.__name__
    if label == 'ImportFrom':
        # map ImportFrom to Import because they are semantically the same
        label = 'Import'

    # set up an output tree node
    out_node = tree.Tree(label)

    # check for certain attributes and store them at the node
    attributes = ['arg', 'id', 'name', 'attr', 'is_async', 
                'conversion', 'annotation', 'returns']

    for attribute in attributes:
        if hasattr(ast_node, attribute):
            setattr(out_node, attribute, getattr(ast_node, attribute))
    if label == 'Constant':
        out_node.value = ast_node.value

    # consider a few special cases where we need to convert to conform to the
    # grammar
    if label == 'If':
        # add test as first child
        out_node._children.append(ast_to_tree(ast_node.test))
        # disambiguate the then and the else block in an if statement
        # by using an intermediate node
        then_node = tree.Tree('Then')
        out_node._children.append(then_node)
        for node in ast_node.body:
            then_node._children.append(ast_to_tree(node))

        else_node = tree.Tree('Else')
        out_node._children.append(else_node)
        for node in ast_node.orelse:
            else_node._children.append(ast_to_tree(node))
        return out_node
    elif label == 'Slice':
        # explicity treat slice nodes to insert intermediate
        # nodes for lower bound, upper bound, and step size
        lower_node = tree.Tree('Lower')
        if hasattr(ast_node, 'lower') and ast_node.lower != None:
            lower_node._children.append(ast_to_tree(ast_node.lower))

        upper_node = tree.Tree('Upper')
        if hasattr(ast_node, 'upper') and ast_node.upper != None:
            upper_node._children.append(ast_to_tree(ast_node.upper))

        step_node = tree.Tree('Step')
        if hasattr(ast_node, 'step') and ast_node.step != None:
            step_node._children.append(ast_to_tree(ast_node.step))

        out_node._children = [lower_node, upper_node, step_node]
        return out_node
    elif label == 'Subscript':
        # add the array that is subscripted as first child
        out_node._children.append(ast_to_tree(ast_node.value))
        # then handle the case where the slice is not an explicit Slice node
        if not isinstance(ast_node.slice, ast.Slice):
            index_node = tree.Tree('Index')
            index_node._children.append(ast_to_tree(ast_node.slice))
            out_node._children.append(index_node)
        else:
            out_node._children.append(ast_to_tree(ast_node.slice))
        return out_node
    elif label == 'Dict':
        # explicity treat dict nodes to insert intermediate
        # nodes for key list and value list
        keys_node = tree.Tree('Keys')
        for node in ast_node.keys:
            keys_node._children.append(ast_to_tree(node))

        values_node = tree.Tree('Values')
        for node in ast_node.values:
            values_node._children.append(ast_to_tree(node))

        out_node._children = [keys_node, values_node]

        return out_node
    elif label == 'Try':
        # explicity treat try nodes to insert an intermediate
        # node for finally
        for node in ast_node.body:
            out_node._children.append(ast_to_tree(node))
        for node in ast_node.handlers:
            out_node._children.append(ast_to_tree(node))
        finally_node = tree.Tree('Finally')
        out_node._children.append(finally_node)
        for node in ast_node.finalbody:
            finally_node._children.append(ast_to_tree(node))
        return out_node
    else:
        # if none of the special cases applied, handle the children recursively.
        # handle all children of this node recursively
        for node in ast.iter_child_nodes(ast_node):
            # ignore some nodes
            if isinstance(node, ast.Load) or isinstance(node, ast.Store) or isinstance(node, ast.Del) or isinstance(node, ast.alias):
                continue
            out_node._children.append(ast_to_tree(node))
        return out_node


class TreeConverter():

    def __init__(self):
        self.reset_variables()

    def reset_variables(self):
        self.nodes = []
        self.node_types = []
        self.adjacency_list = []
        self.signature_hashes = []
        self.body_hashes = []

    def extract_tree(self, reduced_tree):
        if isinstance(reduced_tree, dict):
            self.nodes.append(reduced_tree["uuid"])
            self.node_types.append(reduced_tree["name"])
            self.signature_hashes.append(reduced_tree["signature_hash"])
            self.body_hashes.append(reduced_tree["body_hash"])
            child_list = []
            if isinstance(reduced_tree["body"], list) :
                child_list.extend([node["uuid"] for node in reduced_tree["body"]])
            elif isinstance(reduced_tree["body"], dict):
                child_list.append(reduced_tree["body"]["uuid"])
            else:
                raise Exception("Invalid subtree body.")
            self.adjacency_list.append(child_list)
            self.extract_tree(reduced_tree["body"])
        if isinstance(reduced_tree, list):
            [self.extract_tree(node) for node in reduced_tree]

    def tree_to_list(self, reduced_tree, name_field="types"):
        self.reset_variables()
        self.extract_tree(reduced_tree)
        adj_list_uuid = self.adjacency_list
        adj_list = []
        for sublist in adj_list_uuid:
            adj_list.append(list(map(self.nodes.index, sublist)))
        if not len(self.signature_hashes) == len(self.nodes) == len(self.body_hashes):
            raise Exception("Invalid tree to list conversion.")
        if name_field == "types":
            return self.node_types.copy(), adj_list
        

def structural_metric(astx, asty):
    treex = ast_to_tree(astx)
    treey = ast_to_tree(asty)
    
    return standard_ted(treex.to_list_format(), treey.to_list_format())