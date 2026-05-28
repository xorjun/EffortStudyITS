from _ast import Call, Del, Delete, Global, Interactive, Nonlocal, Name
from typing import Any
from pathlib import Path
from sys import __stdout__, executable as python_executable
from config import config
import asyncio
import aiohttp
import base64
import json
import ast
import re
import io
import os
import matplotlib.pyplot as plt
import tempfile
import zipfile


async def execute_code(code, additional_files: list = []):
    run_result = await execute_code_judge0(code_payload=code, additional_files=additional_files)
    if "##!serialization!##" in run_result:
        pattern = r".*?\##!serialization!##(.*?)\##!serialization!##.*"
        parsed_result_string = re.findall(pattern, run_result, re.DOTALL)
        if len(parsed_result_string) > 1: raise ValueError("Unexpected serialization tags.")
        run_result = json.loads(parsed_result_string[0])
    return(run_result)


def zip_additional_files(additional_files: list):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in additional_files:
            zf.writestr(file['filename'], file['content'])
    zip_bytes = zip_buffer.getvalue()
    return zip_bytes


async def execute_code_judge0(code_payload, additional_files: list = [], url=f"{config.judge0_host}", bearer_token=config.judge0_token):
    try:
        return await execute_code_judge0_primary(code_payload, additional_files=additional_files, url=url, bearer_token=bearer_token)
    except Exception as error:
        if not should_use_local_execution_fallback():
            raise
        print(f"Judge0 execution failed, using local development fallback: {error}")
        return await execute_code_local(code_payload, additional_files=additional_files)


def should_use_local_execution_fallback():
    return (
        config.judge0_mode == "local"
        and config.env in ["development", "development-docker"]
        and getattr(config, "unsafe_local_execution_fallback_enabled", False)
    )


async def execute_code_local(code_payload, additional_files: list = []):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        script_path = temp_path / "script.py"
        script_path.write_text(code_payload, encoding="utf-8")

        for additional_file in additional_files:
            file_name = Path(additional_file["filename"]).name
            (temp_path / file_name).write_text(additional_file["content"], encoding="utf-8")

        environment = os.environ.copy()
        environment["MPLBACKEND"] = "Agg"
        process = await asyncio.create_subprocess_exec(
            python_executable,
            script_path.name,
            cwd=str(temp_path),
            env=environment,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        try:
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=20)
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            return "Time limit exceeded."

    return stdout.decode("utf-8", errors="replace")


async def execute_code_judge0_primary(code_payload, additional_files: list = [], url=f"{config.judge0_host}", bearer_token=config.judge0_token):
    """Execute a code snippet in judge0 and wait for the result to return.

    Args:
        code_payload (str): string containing an executable python program
        url (str, optional): Url of the Judge0 server.".

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    async with aiohttp.ClientSession(trust_env=True) as session:
        payload = {
            #"expected_output": "null",
            "language_id": "10",
            "max_file_size": "5000", #kb
            #"max_processes_and_or_threads": "1",
            "memory_limit": 150000, #kb
            "source_code": base64.b64encode(bytes(code_payload, 'utf-8')).decode("ascii"),
            #"stack_limit": "null",
            #"stdin": "null",
            "wall_time_limit": "20", #sec
            "cpu_time_limit": "20", #sec
            "enable_network": "false",
            "redirect_stderr_to_stdout": "true",
            }
        if not bearer_token is None:
            headers = {"Authorization": f"Bearer {bearer_token}"}
        else:
            headers = {}
        if len(additional_files) > 0:
            payload.update({"additional_files": base64.b64encode(zip_additional_files(additional_files)).decode("ascii")})
        async with session.post(f"{url}/submissions/?base64_encoded=true", data=payload, headers=headers, timeout=20) as response:
            run_token = await response.text()
            run_token = json.loads(run_token)["token"]
        max_iter = 100
        for i in range(0, max_iter): #max_iter for querying the status
            async with session.get(f"{url}/submissions/{run_token}", headers=headers) as response:
                run_result = await response.text()
                run_result = json.loads(run_result)
                if run_result["status"]["description"] not in ["In Queue", "Processing"]:
                    # In case of unexpected return status, return an informative error
                    if (run_result["stdout"] is None) and (run_result["status"]["description"] != "Accepted"):
                        raise Exception("Empty run result: execution status: {0}".format(run_result))
                    elif (run_result["stdout"] is None) and (run_result["status"]["description"] == "Accepted"):
                        run_result["stdout"] = ""
                    return run_result["stdout"]
                await asyncio.sleep(0.2)
        raise Exception("Code Sandbox status frozen!")


def process_plt_plots(func_queue):
    plot_string = ""
    plt.clf()
    for entry in func_queue:
        try:
            if entry["func"] == "show":
                img_stream = io.BytesIO()
                img_format = "png"
                plt.savefig(img_stream, format=img_format, bbox_inches='tight')
                img_stream.seek(0)
                img_base64 = base64.b64encode(img_stream.read()).decode()
                img_style = "height: 100%"#; padding: 0% 5% 0% 5%"
                plot_string = plot_string + f"\n<img alt='test plot' src='data:image/{img_format};base64,{img_base64}' style='{img_style}'>"
                plt.clf()
            else:
                getattr(plt, entry['func'])(*entry['args'], **entry['kwargs'])
        except Exception as e:
            plot_string = plot_string + "\n" + str(e)
    return plot_string

def parse_argument_types(arg_dict):
    run_arguments = [(key, arg_dict[key]) for key in arg_dict.keys()]
    try:
        check_list = [check_user_code(entry[1]) for entry in run_arguments]
    except Exception as e: 
        raise ValueError("Illegal argument.")
    else:
        try:
            run_argument_string = dict([(entry[0], f'#$eval(##{entry[1]}##)$#') for entry in run_arguments])
            run_argument_string = json.dumps(run_argument_string)
            run_argument_string = run_argument_string.replace('"#$', "")
            run_argument_string = run_argument_string.replace('$#"', "")
            run_argument_string = run_argument_string.replace('##', '"')
        except Exception as e:
            raise ValueError("Invalid argument.")
        return run_argument_string


def check_user_code(code, prefix_lines=[]):
    class ImportVisitor(ast.NodeVisitor):
        def __init__(self, prefix_lines: list=[]):
            self.prefix_lines = prefix_lines

        def visit_Import(self, node):
            if node.lineno not in self.prefix_lines:
                raise Exception("Imports are not allowed in this context.")
            else: 
                self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if node.lineno not in self.prefix_lines:
                raise Exception("Imports are not allowed in this context")
            else:
                self.generic_visit(node)
        
        def visit_Interactive(self, node: Interactive):
            if node.lineno in self.prefix_lines:
                raise Exception("Interactive Mode is not allowed")
            else: 
                self.generic_visit(node)
        
        def visit_Delete(self, node: Delete):
            if node.lineno not in self.prefix_lines:
                raise Exception("Deletes are not allowed in this context")
            else:
                self.generic_visit(node)
        
        def visit_Global(self, node: Global):
            if node.lineno not in self.prefix_lines:
                raise Exception("Global Scope is not allowed")
            else:
                self.generic_visit(node)

        def visit_Nonlocal(self, node: Nonlocal):
            if node.lineno not in self.prefix_lines: 
                raise Exception("Nonlocal Scope is not allowed")
            else:
                self.generic_visit(node)
        
        #def visit_Load(self, node: Load) -> Any:
        #    raise Exception("Load not allowed")
        
        #def visit_Store(self, node: Store) -> Any:
        #    raise Exception("Store not allowed")
        
        def visit_Del(self, node: Del) -> Any:
            if node.lineno not in self.prefix_lines:
                raise Exception("Del not allowed")
            else: self.generic_visit(node)
        
        def visit_Call(self, node: Call) -> Any:
            if "id" in node.func._fields:
                func_id = node.func.id
            else:
                func_id = node.func.attr
                #module_id = node.func.value.id
            if func_id == "exec":
                raise Exception("exec() is not allowed in this context")
            if func_id in ["eval", "breakpoint", "callable", "open",
                                 "delattr", "dir", "getattr", "globals",
                                 "hasattr", "help", "id", "input", "locals", 
                                 "memoryview", "property", "setattr", 
                                 "staticmethod", "vars", "__import__"]:
                raise Exception(f"{func_id}() is not allowed in this context")
            self.generic_visit(node)

        def visit_Name(self, node: Name) -> Any:
            bad_func_list = ["exec", "eval", "breakpoint", "callable", "open",
                                 "delattr", "dir", "getattr", "globals",
                                 "hasattr", "help", "id", "input", "locals", 
                                 "memoryview", "property", "setattr", 
                                 "staticmethod", "vars", "__import__"]
            id = node.id
            if id in bad_func_list:
                raise Exception(f"Name {id} is not allowed in this context")
            self.generic_visit(node)


    ast_tree = ast.parse(code)
    visitor = ImportVisitor(prefix_lines=prefix_lines)
    visitor.visit(ast_tree)
    bad_strings = ["__builtins__", "np.distutil", "multiprocessing", "APIRouter", "asyncio", "current_active_user", "database", "run_with_timeout"]
    for string in bad_strings:
        if string in code:
            raise Exception("Bad symbol detected, please don't use {0} in your program".format(string))
    return True