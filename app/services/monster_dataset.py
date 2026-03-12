import re
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

    @classmethod
    def _extract_average_damage(cls, desc: str) -> int | None:
        if not desc:
            return None

        match = re.search(r"(\d+)\s*\(\s*([^)]+)\s*\)\s*[a-zA-Z ]+damage", desc)
        if match:
            return int(match.group(1))

        match = re.search(r"Hit:\s*(\d+)", desc)
        if match:
            return int(match.group(1))

        return None

    @classmethod
    def _extract_damage_dice(cls, desc: str) -> str | None:
        if not desc:
            return None

        match = re.search(r"\(\s*([0-9d+\- ]+)\s*\)\s*[a-zA-Z ]+damage", desc)
        if match:
            return match.group(1).strip()

        return None

    @classmethod
    def _extract_damage_type(cls, desc: str) -> str | None:
        if not desc:
            return None

        match = re.search(r"\)\s*([A-Za-z]+)\s+damage", desc)
        if match:
            return match.group(1)

        return None

    @classmethod
    def _extract_range_text(cls, desc: str) -> str | None:
        if not desc:
            return None

        match = re.search(r"(Melee Weapon Attack:|Ranged Weapon Attack:|Melee or Ranged Weapon Attack:)", desc)
        if match:
            return match.group(1).replace(":", "")

        return None

    @classmethod
    def extract_action_rows(cls, monster: dict, participant_id: int) -> list[dict]:
        rows: list[dict] = []

        for action in monster.get("actions", []):
            desc = action.get("desc")

            rows.append(
                {
                    "participant_id": participant_id,
                    "name": action.get("name", "Unnamed Action"),
                    "action_type": "ACTION",
                    "description": desc,
                    "attack_bonus": action.get("attack_bonus"),
                    "average_damage": cls._extract_average_damage(desc or ""),
                    "damage_dice": cls._extract_damage_dice(desc or ""),
                    "damage_type": cls._extract_damage_type(desc or ""),
                    "range_text": cls._extract_range_text(desc or ""),
                    "is_dataset_imported": True,
                    "notes": None,
                }
            )

        for action in monster.get("special_abilities", []):
            rows.append(
                {
                    "participant_id": participant_id,
                    "name": action.get("name", "Unnamed Special Ability"),
                    "action_type": "SPECIAL",
                    "description": action.get("desc"),
                    "attack_bonus": None,
                    "average_damage": None,
                    "damage_dice": None,
                    "damage_type": None,
                    "range_text": None,
                    "is_dataset_imported": True,
                    "notes": None,
                }
            )

        return rows