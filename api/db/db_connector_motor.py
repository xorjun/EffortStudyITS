import motor.motor_asyncio
from fastapi.encoders import jsonable_encoder
import json
import io

#def print_to_string(*args, **kwargs):
#    output = io.StringIO()
#    print(*args, file=output, **kwargs)
#    contents = output.getvalue()
#    output.close()
#    return contents

class database:

    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.its_db

    async def log_code_submission(self, tested_submission):
        #Await to enusre the event-loop is not blocked
        await self.db["submission"].insert_one(jsonable_encoder(tested_submission))

    async def get_task(self, task_id):
        cursor = self.db.tasks.find({"task_id": task_id})
        task_json = await cursor.to_list(length=1)
        if len(task_json) == 1:
            return(task_json[0])
        else: 
            raise Exception("Multiple Tasks with same ID present")
        
    async def get_feedback(self, submission_id):
        cursor = self.db.submission.find({"submission_id": submission_id}, {'_id': 0})
        submission_json = await cursor.to_list(length = 2)
        if len(submission_json) == 1:
            return(submission_json[0])
        elif len(submission_json) == 2: 
            raise Exception("Multiple Tasks with same ID present")
        elif len(submission_json) == 0:
            raise Exception("Unknown submission")
