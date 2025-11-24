from fastapi.testclient import TestClient
import json
from submissions.handle_submissions import router
import pytest
from httpx import AsyncClient

#TODO: Implement User-logic for this test: create a test user and store cookie - send submit request with cookie.
async def submit_code(code, expected_status=1, expected_message_prefix="", task_id=1):
    async with AsyncClient(app=router, base_url="http://test") as ac:
        response = await ac.post("/code_submit", content=json.dumps({"task_unique_name": task_id, 
                                                                     "code": code, 
                                                                     "log": "True", 
                                                                     "submission_id": "test",
                                                                     "submission_time": ""}),
                                                                     )
    payload = response.json()
    print(payload)
    assert payload['test_results'][0]['status'] == expected_status, "Incorrect status code"
    message = payload['test_results'][0]['message']
    assert message.startswith(expected_message_prefix), f"Incorrect message prefix: {message} instead of {expected_message_prefix}"


@pytest.mark.asyncio
async def test_incorrect_code_submit():
    code = """
def factorial(n):
    return(1)
"""
    await submit_code(code, 0, "Test failure")


@pytest.mark.asyncio
async def test_correct_code_submit():
    code = """
def factorial(n):
    if n < 0:
        raise ValueError("Factorial is undefined for negative numbers.")
    elif n == 0:
        return 1
    else:
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result
"""
    await submit_code(code, 1, "Test success")

# Benjamin fragen!
@pytest.mark.asyncio
async def test_syntax_error_handling():
    code="""
def factorial(n:
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
"""
    await submit_code(code, 0, "Error or Exception")

@pytest.mark.asyncio
async def test_import_statement_refusal():
    code = """
import os
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
"""
    await submit_code(code, 0, "Error or Exception: Imports are not allowed in this context")


@pytest.mark.asyncio
async def test_from_import_statement_refusal():
    code="""
from os import system
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
"""
    await submit_code(code, 0, "Error or Exception: Imports are not allowed in this context")


@pytest.mark.asyncio
async def test_delete_refusal():
    code="""
def factorial(n):
    return(n)
del test_result
"""
    await submit_code(code, 0, "Error or Exception: Deletes are not allowed in this context")

@pytest.mark.asyncio
async def test_global_refusal():
    code="""
def factorial(n):
    return(n)
global test_result
test_result = 1
"""
    await submit_code(code, 0, "Error or Exception: Global Scope is not allowed")

@pytest.mark.asyncio
async def test_nonlocal_refusal():
    code="""
def factorial(n):
    test_result = 0
    def change_result():
        nonlocal test_result
        test_result = 1
    change_result()
    return(n)
"""
    await submit_code(code, 0, "Error or Exception: Nonlocal Scope is not allowed")

@pytest.mark.asyncio
async def test_exec_refusal():
    code="""
def factorial(n):
    return(n)
exec("import os")
"""
    await submit_code(code, 0, "Error or Exception: exec() is not allowed in this context")

@pytest.mark.asyncio
async def test_exec_refusal():
    code="""
def factorial(n):
    return(n)
eval("import os")
"""
    await submit_code(code, 0, "Error or Exception: eval() is not allowed in this context")

