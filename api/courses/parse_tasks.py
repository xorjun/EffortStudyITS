"""Read a folder of tasks from disk to db.
"""
import json
import os
import ast
import io
import ast
import re
import base64
from courses.schemas import TaskType
from db import database
from PIL import Image

def process_file(file_path):
    # Process the content of the text file as needed.
    with io.open(file_path, mode="r", encoding="utf-8") as f:
        content = f.readlines()
    content_docstring = "".join(content)
    return(content_docstring)

def get_function_names(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())
    
    function_names = []
    context = []

    
    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            if not context:
                function_names.append(node.name)
            context.append(node)
            self.generic_visit(node)
            context.pop()

        def visit_ClassDef(self, node):
            context.append(node)
            self.generic_visit(node)
            context.pop()

        def generic_visit(self, node):
            for child in ast.iter_child_nodes(node):
                self.visit(child)

    visitor = Visitor()
    visitor.visit(tree)

    # function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and not isinstance(node.parent, ast.FunctionDef)]
    return function_names

def extract_argument_names(func_str):
    try:
        tree = ast.parse(func_str)
        # Find the function definition node
        func_def = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        # Extract parameter names
        param_names = [param.arg for param in func_def.args.args]
        return param_names
    except Exception as e:
        raise ValueError(f"Error extracting arguments: {e}")

async def parse_all_tasks(dir, db=None):
    for location in os.listdir(dir):
        if location.startswith("task_") and (not location.endswith(".json")):
            assert location.startswith("task_"), "Wrong format for task folders, use task_[task_unique_name]"
            try:
                await task_to_json(dir, location, db)
            except Exception as e:
                print(f"A problem occured during uploading task {location}")
                raise e
        else:
            await parse_all_tasks(os.path.join(dir, location), db=db)

async def task_to_json(dir, task_unique_name, db=None):
    # Iterate through the files in the folder
    task_dict = {}
    task_dict["unique_name"] = task_unique_name.removeprefix("task_").split(".")[0]
    tests = {}
    for file_name in os.listdir(os.path.join(dir, task_unique_name)):
        file_path = os.path.join(dir, task_unique_name, file_name)
        if os.path.isdir(file_path):
            print(f"'{file_name}' is a directory was ignored.")
            continue
        # PNGs cannot be read with utf-8
        elif file_name.endswith("png"):
            continue
        content_docstring = process_file(file_path)
        if file_name.startswith("test"):
            #test_name = file_name.split("_", 1)[1]
            test_name = file_name.split(".")[0]
            test_name_alt = get_function_names(file_path)
            if len(test_name_alt) == 1:
                pass
            assert len(test_name_alt) == 1, "Too many test functions defined in single test file. Define only one!"
            assert test_name == test_name_alt[0], "Name of the test function should be the same as the filename"
            #Split on stop-symbol for imports
            test = content_docstring.split("#!cut_imports!#")[1]
            #json.dump({"test_{0}".format(test_number): test}, outfile, ensure_ascii=False)
            tests[test_name] = test
        elif file_name.endswith("md"):
            header = content_docstring.split("\n")[0]
            if not header.startswith("# "):
                raise ValueError(f"'{file_path}' should contain the first line '# task_display_name'")
            task_display_name = header.split("#")[1].strip()
            content_docstring = replace_images(content_docstring, task_unique_name, dir)
            task_dict["display_name"] = task_display_name
            task_dict["task"] = content_docstring
            #json.dump({"task": content_docstring}, outfile, ensure_ascii=False)
        elif file_name == "example_solution.py":
            task_type = content_docstring.split("!#")[0]
            task_type = task_type[2:]
            task_dict["type"] = task_type
            if task_type not in [TaskType.Function, TaskType.Print, TaskType.PlotFunction]: #["function", "print", "plot_function"]
                raise Exception(f"Invalid task-type use function or print, not {task_type}")
            #json.dump({"example_solution": content_docstring}, outfile, ensure_ascii=False)
            prefix = content_docstring.split("#!prefix!#")[0]
            prefix = prefix.split("!#")[1].lstrip()
            task_dict["prefix"] = prefix.strip()
            #test if there is a required signature, and if so, add it to database.
            task_dict["example_solution"] = content_docstring.split("#!prefix!#\n")[1]
            task_dict["function_name"] = get_function_names(file_path)[0] #TODO: Secure for example solutions with multiple functions.
            if task_type in [TaskType.Function, TaskType.PlotFunction]:
                arguments = extract_argument_names(task_dict["prefix"] + "\n" + task_dict["example_solution"])
                task_dict["arguments"] = arguments
                if task_type == TaskType.PlotFunction:
                    # check that plt is imported as plt
                    if not "import matplotlib.pyplot as plt" in prefix:
                        raise ValueError("Please impot mytplotlib.pyplot as plt.")
        elif file_name.startswith("multiple_choice"):
            task_dict["type"] = TaskType.MultipleChoice
            task_dict["prefix"] = "no_prefix"
            task_dict["example_solution"] = ""
            if file_name.endswith(".py"):
                json_section = content_docstring.split("#!json!#")[1]
                mc_json = json.loads(json_section)
            elif file_name.endswith(".json"):
                mc_json = json.loads(content_docstring)
            else: raise TypeError("'multiple_choice' has to be of type '.py' or '.json'.")
            task_dict["possible_choices"] = mc_json["possible_choices"]
            task_dict["correct_choices"] = mc_json["correct_choices"]
            task_dict["choice_explanations"] = mc_json["choice_explanations"]
            
    task_dict["tests"] = tests
    await database.create_task(task_dict)

# replaces markdown images with base64 html containers
def replace_images(content_docstring: str, task_unique_name: str, dir: str) -> str:
    # find html images and convert to base64
    matches = re.findall(r"<img\s+.+>", content_docstring)
    for match in matches:
        img_path, img_format = None, None
        split_match = re.split(r"""['|"]""", match)
        for i, split in enumerate(split_match):
            if split.endswith("src="):
                img_path = split_match[i+1]
        # skip if already data image
        if not img_path: continue
        if "data:image" in img_path: continue
        img_format = img_path.split('.')[-1]
        
        with open(os.path.join(dir, task_unique_name, img_path), mode='rb') as img:
            img_base64 = base64.b64encode(img.read()).decode()
        # layered replace to ensure only the current one gets replaced
        match_replacement = f"data:image/{img_format};base64,{img_base64}"
        replacement = match.replace(img_path, match_replacement)
        content_docstring = content_docstring.replace(match, replacement)
    
    # find and convert markdown image to html base64 image
    matches = re.findall(r"!\[[^\]]*\]\([^)]*\)", content_docstring)
    for match in matches:
        # split at brackets
        split_match = re.split(r"[\[|\]|(|)]", match)
        img_label = split_match[1]
        img_path = split_match[3]
        img_format = img_path.split('.')[-1]
        img_style = "max-width:88%; padding: 0% 5% 0% 5%"
        
        # skip if already data image
        if not "data:image" in img_path:
            with open(os.path.join(dir, task_unique_name, img_path), mode='rb') as img:
                img_base64 = base64.b64encode(img.read()).decode()
        else: img_base64 = img_path
        replacement = f"<img alt='{img_label}' src='data:image/{img_format};base64,{img_base64}' style='{img_style}'>"
        content_docstring = content_docstring.replace(match, replacement)
    return content_docstring