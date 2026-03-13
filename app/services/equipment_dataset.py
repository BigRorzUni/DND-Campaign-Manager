import requests


BASE_URL = "https://www.dnd5eapi.co/api/2014/equipment"


class EquipmentDatasetService:
    _equipment_index_cache: list[dict] | None = None
    _equipment_detail_cache: dict[str, dict] = {}

    @staticmethod
    def list_equipment_index():
        if EquipmentDatasetService._equipment_index_cache is not None:
            return EquipmentDatasetService._equipment_index_cache

        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
        results = response.json()["results"]
        EquipmentDatasetService._equipment_index_cache = results
        return results

    @staticmethod
    def search_equipment(query: str):
        q = query.lower().strip()
        return [
            {
                "api_index": item["index"],
                "name": item["name"],
            }
            for item in EquipmentDatasetService.list_equipment_index()
            if q in item["name"].lower()
        ][:25]

    @staticmethod
    def get_equipment(equipment_index: str):
        if equipment_index in EquipmentDatasetService._equipment_detail_cache:
            return EquipmentDatasetService._equipment_detail_cache[equipment_index]

        response = requests.get(f"{BASE_URL}/{equipment_index}", timeout=10)
        response.raise_for_status()
        detail = response.json()
        EquipmentDatasetService._equipment_detail_cache[equipment_index] = detail
        return detail

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