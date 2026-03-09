from sqlalchemy.orm import Session as DbSession

from app.models.character import Character


class CharacterRepo:
    def create(
        self,
        db: DbSession,
        *,
        campaign_id: int,
        name: str,
        role: str,
        class_name: str | None,
        level: int | None,
        max_hp: int | None,
        current_hp: int | None,
        armor_class: int | None,
        notes: str | None,
    ) -> Character:
        obj = Character(
            campaign_id=campaign_id,
            name=name,
            role=role,
            class_name=class_name,
            level=level,
            max_hp=max_hp,
            current_hp=current_hp,
            armor_class=armor_class,
            notes=notes,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db: DbSession, character_id: int) -> Character | None:
        return db.get(Character, character_id)

    def list_for_campaign(self, db: DbSession, campaign_id: int) -> list[Character]:
        return (
            db.query(Character)
            .filter(Character.campaign_id == campaign_id)
            .order_by(Character.id.desc())
            .all()
        )

    def update(
        self,
        db: DbSession,
        obj: Character,
        *,
        name: str | None,
        role: str | None,
        class_name: str | None,
        level: int | None,
        max_hp: int | None,
        current_hp: int | None,
        armor_class: int | None,
        notes: str | None,
    ) -> Character:
        if name is not None:
            obj.name = name
        if role is not None:
            obj.role = role
        if class_name is not None:
            obj.class_name = class_name
        if level is not None:
            obj.level = level
        if max_hp is not None:
            obj.max_hp = max_hp
        if current_hp is not None:
            obj.current_hp = current_hp
        if armor_class is not None:
            obj.armor_class = armor_class
        if notes is not None:
            obj.notes = notes

        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: DbSession, obj: Character) -> None:
        db.delete(obj)
        db.commit()