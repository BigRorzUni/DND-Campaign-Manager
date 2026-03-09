from sqlalchemy.orm import Session as DbSession

from app.models.character_resource_state import CharacterResourceState


class ResourceStateRepo:
    def create(
        self,
        db: DbSession,
        *,
        character_id: int,
        current_hp: int | None,
        spell_slots_1_current: int | None,
        spell_slots_1_max: int | None,
        spell_slots_2_current: int | None,
        spell_slots_2_max: int | None,
        spell_slots_3_current: int | None,
        spell_slots_3_max: int | None,
        hit_dice_current: int | None,
        hit_dice_max: int | None,
    ) -> CharacterResourceState:
        obj = CharacterResourceState(
            character_id=character_id,
            current_hp=current_hp,
            spell_slots_1_current=spell_slots_1_current,
            spell_slots_1_max=spell_slots_1_max,
            spell_slots_2_current=spell_slots_2_current,
            spell_slots_2_max=spell_slots_2_max,
            spell_slots_3_current=spell_slots_3_current,
            spell_slots_3_max=spell_slots_3_max,
            hit_dice_current=hit_dice_current,
            hit_dice_max=hit_dice_max,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get_by_character_id(
        self, db: DbSession, character_id: int
    ) -> CharacterResourceState | None:
        return (
            db.query(CharacterResourceState)
            .filter(CharacterResourceState.character_id == character_id)
            .first()
        )

    def update(
        self,
        db: DbSession,
        obj: CharacterResourceState,
        *,
        current_hp: int | None,
        spell_slots_1_current: int | None,
        spell_slots_1_max: int | None,
        spell_slots_2_current: int | None,
        spell_slots_2_max: int | None,
        spell_slots_3_current: int | None,
        spell_slots_3_max: int | None,
        hit_dice_current: int | None,
        hit_dice_max: int | None,
    ) -> CharacterResourceState:
        if current_hp is not None:
            obj.current_hp = current_hp

        if spell_slots_1_current is not None:
            obj.spell_slots_1_current = spell_slots_1_current
        if spell_slots_1_max is not None:
            obj.spell_slots_1_max = spell_slots_1_max

        if spell_slots_2_current is not None:
            obj.spell_slots_2_current = spell_slots_2_current
        if spell_slots_2_max is not None:
            obj.spell_slots_2_max = spell_slots_2_max

        if spell_slots_3_current is not None:
            obj.spell_slots_3_current = spell_slots_3_current
        if spell_slots_3_max is not None:
            obj.spell_slots_3_max = spell_slots_3_max

        if hit_dice_current is not None:
            obj.hit_dice_current = hit_dice_current
        if hit_dice_max is not None:
            obj.hit_dice_max = hit_dice_max

        db.commit()
        db.refresh(obj)
        return obj