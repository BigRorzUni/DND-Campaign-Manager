import requests


class MonsterDatasetService:
    BASE_URL = "https://www.dnd5eapi.co"

    @classmethod
    def search_monsters(cls, q: str | None = None) -> list[dict]:
        try:
            response = requests.get(f"{cls.BASE_URL}/api/2014/monsters", timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            return []

        results = data.get("results", [])

        if not q:
            return results

        q_lower = q.strip().lower()
        return [
            monster for monster in results
            if q_lower in monster.get("name", "").lower()
            or q_lower in monster.get("index", "").lower()
        ]

    @classmethod
    def get_monster(cls, monster_index: str) -> dict | None:
        try:
            response = requests.get(
                f"{cls.BASE_URL}/api/2014/monsters/{monster_index}",
                timeout=10
            )
            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    @classmethod
    def extract_armor_class(cls, monster: dict) -> int | None:
        armor_class = monster.get("armor_class")

        if isinstance(armor_class, int):
            return armor_class

        if isinstance(armor_class, list) and armor_class:
            first = armor_class[0]
            if isinstance(first, dict):
                return first.get("value")
            if isinstance(first, int):
                return first

        return None

    @classmethod
    def extract_monster_type(cls, monster: dict) -> str | None:
        monster_type = monster.get("type")

        if isinstance(monster_type, str):
            return monster_type

        if isinstance(monster_type, dict):
            return monster_type.get("name")

        return None