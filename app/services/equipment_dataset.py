import requests

BASE_URL = "https://www.dnd5eapi.co/api/2014/equipment"


class EquipmentDatasetService:
    @staticmethod
    def list_equipment():
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
        data = response.json()["results"]

        results = []
        for item in data:
            detail = EquipmentDatasetService.get_equipment(item["index"])
            results.append(EquipmentDatasetService.to_summary(detail))

        return results

    @staticmethod
    def search_equipment(query: str):
        all_equipment = EquipmentDatasetService.list_equipment()
        return [
            item for item in all_equipment
            if query.lower() in item["name"].lower()
        ][:25]

    @staticmethod
    def get_equipment(equipment_index: str):
        response = requests.get(f"{BASE_URL}/{equipment_index}", timeout=10)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def to_summary(detail: dict) -> dict:
        damage = detail.get("damage") or {}
        damage_type = damage.get("damage_type") or {}
        desc = detail.get("desc") or []

        armor_class = detail.get("armor_class") or {}
        range_info = detail.get("range") or {}
        equipment_category = detail.get("equipment_category") or {}

        return {
            "api_index": detail["index"],
            "name": detail["name"],
            "category": equipment_category.get("name"),
            "weapon_category": detail.get("weapon_category"),
            "damage_dice": damage.get("damage_dice"),
            "damage_type": damage_type.get("name"),
            "range_normal": range_info.get("normal"),
            "range_long": range_info.get("long"),
            "armor_category": detail.get("armor_category"),
            "armor_class_base": armor_class.get("base"),
            "armor_dex_bonus": armor_class.get("dex_bonus"),
            "armor_max_bonus": armor_class.get("max_bonus"),
            "weight": detail.get("weight"),
            "brief_description": desc[0] if isinstance(desc, list) and desc else None,
        }