import json
import asyncio
import base64
import aiohttp

async def execute_code_judge0(code_payload, url=f"http://0.0.0.0:2358"):
    """Execute a code snippet in judge0 and wait for the result to return.

    Args:
        code_payload (str): string containing an executable python program
        url (str, optional): Url of the Judge0 server. Defaults to "http://host:2358".

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """
    async with aiohttp.ClientSession() as session:
        payload = {
            #"expected_output": "null",
            "language_id": "10",
            "max_file_size": "1000", #kb
            #"max_processes_and_or_threads": "1",
            "memory_limit": 100000, #kb
            "source_code": code_payload,#base64.b64encode(bytes(code_payload, 'utf-8')).decode("ascii"),
            #"stack_limit": "null",
            #"stdin": "null",
            "wall_time_limit": "10", #sec
            "cpu_time_limit": "10", #sec
            "enable_network": "false",
            "redirect_stderr_to_stdout": "true",
            }
        async with session.post(f"{url}/submissions/?base64_encoded=false", data=payload) as response:
            run_token = await response.text()
            run_token = json.loads(run_token)["token"]
        max_iter = 100
        for i in range(0, max_iter): #max_iter for querying the status
            async with session.get(f"{url}/submissions/{run_token}") as response:
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


if __name__ == "__main__":
    code = "print('Hello World')"
    result = asyncio.run(execute_code_judge0(code))
    print(result)
