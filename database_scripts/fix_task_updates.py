"""
One-shot script: fix the print_welcome task prefix and clear all simplified course attempts.
Run inside the backend container: python3 /tmp/fix_task_updates.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://backend_service_user:Sc1ptDB_S3rv1ce_2026x@mongodb:27017/?authSource=admin"

TASK_UPDATES = {
    "print_welcome": {
        "prefix": "",
        "function_name": "_helper",
        "type": "print",
        "example_solution": 'print("Welcome to Activity Tracker")\n\ndef _helper(): pass',
        "tests": {
            "test_print_welcome": '\ndef test_print_welcome():\n    assert submission_captured_output == "Welcome to Activity Tracker", "Your code should print exactly: Welcome to Activity Tracker"',
            "test_print_out": '\ndef test_print_out():\n    assert submission_captured_output == "Welcome to Activity Tracker", "Use print() to display: Welcome to Activity Tracker"',
        },
    }
}


async def main():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["its_db"]

    for unique_name, updates in TASK_UPDATES.items():
        result = await db["Task"].update_one(
            {"unique_name": unique_name},
            {"$set": updates},
        )
        print(f"Task '{unique_name}': matched={result.matched_count}, modified={result.modified_count}")

        # Verify
        task = await db["Task"].find_one({"unique_name": unique_name})
        print(f"  prefix now: {repr(task.get('prefix', 'MISSING'))}")
        print(f"  function_name now: {task.get('function_name', 'MISSING')}")

    # Clear stale attempts and enrollments
    r1 = await db["Attempt"].delete_many({"course_unique_name": "activity_tracker_simplified"})
    r2 = await db["CourseEnrollment"].delete_many({"course_unique_name": "activity_tracker_simplified"})
    print(f"Cleared {r1.deleted_count} attempts, {r2.deleted_count} enrollments")

    client.close()


asyncio.run(main())
