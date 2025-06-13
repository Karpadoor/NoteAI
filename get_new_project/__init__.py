import azure.functions as func
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    _ = req
    file_path = os.path.join(os.path.dirname(__file__), "new_project.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return func.HttpResponse(
            json.dumps(data),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            f"Error reading new_project.json: {str(e)}",
            status_code=500
        )