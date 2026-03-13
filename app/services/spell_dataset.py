import requests

BASE_URL = "https://www.dnd5eapi.co/api/2014/spells"


class SpellDatasetService:
    @staticmethod
    def list_spells():
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()["results"]

        results = []
        for item in data:
            detail = SpellDatasetService.get_spell(item["index"])
            desc = detail.get("desc", [])
            brief_description = desc[0] if isinstance(desc, list) and desc else None

            classes = [
                cls.get("name")
                for cls in (detail.get("classes") or [])
                if cls.get("name")
            ]

            results.append({
                "index": detail["index"],
                "name": detail["name"],
                "level": detail["level"],
                "brief_description": brief_description,
                "classes": classes,
                "url": item.get("url"),
            })

        return results

    @staticmethod
    def search_spells(query: str):
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()["results"]

        filtered = [
            item for item in data
            if query.lower() in item["name"].lower()
        ]

        results = []
        for item in filtered[:25]:
            detail = SpellDatasetService.get_spell(item["index"])
            desc = detail.get("desc", [])
            brief_description = desc[0] if isinstance(desc, list) and desc else None

            classes = [
                cls.get("name")
                for cls in (detail.get("classes") or [])
                if cls.get("name")
            ]

            results.append({
                "index": detail["index"],
                "name": detail["name"],
                "level": detail["level"],
                "brief_description": brief_description,
                "classes": classes,
                "url": item.get("url"),
            })

        return results

    @staticmethod
    def get_spell(spell_index: str):
        response = requests.get(f"{BASE_URL}/{spell_index}", timeout=10)
        response.raise_for_status()
        return response.json()