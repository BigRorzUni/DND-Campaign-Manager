import requests

BASE_URL = "https://www.dnd5eapi.co/api/2014/classes"


class ClassDatasetService:
    @staticmethod
    def list_classes():
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()["results"]

        results = []
        for item in data:
            detail = ClassDatasetService.get_class(item["index"])
            results.append({
                "index": detail["index"],
                "name": detail["name"],
            })

        return results

    @staticmethod
    def get_class(class_index: str):
        response = requests.get(f"{BASE_URL}/{class_index}", timeout=10)
        response.raise_for_status()
        return response.json()