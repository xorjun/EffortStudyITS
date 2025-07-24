from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/about")
def get_about():
    filepath = os.path.join(os.path.dirname(__file__), "about.md")
    print(filepath)
    with open(filepath) as f:
        about_markdown = f.read()
    return({"about_markdown": about_markdown})

@router.get("/data_collection")
def get_about():
    filepath = os.path.join(os.path.dirname(__file__), "data_collection.md")
    print(filepath)
    with open(filepath) as f:
        data_collection_markdown = f.read()
    return({"data_collection_markdown": data_collection_markdown})

@router.get("/privacy_policy")
def get_policy():
    filepath = os.path.join(os.path.dirname(__file__), "privacy_policy.md")
    print(filepath)
    with open(filepath) as f:
        privacy_policy_markdown = f.read()
    return({"privacy_policy_markdown": privacy_policy_markdown})

@router.get("/imprint")
def get_imprint():
    filepath = os.path.join(os.path.dirname(__file__), "imprint.md")
    print(filepath)
    with open(filepath) as f:
        imprint_markdown = f.read()
    return({"imprint_markdown": imprint_markdown})