import json
from typing import Optional, List
from sqlalchemy import Boolean, ForeignKey, select, Text, Table, Column
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship, MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    json_field_list = None

    def to_json(self):
        return json.dumps({key: self.__getattribute__(key) for key in self.json_field_list})

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return self.to_json()


ImageTag = Table(
    "image_tags",
    Base.metadata,
    Column("id", primary_key=True),
    Column("image_id", ForeignKey("images.id")),
    Column("tag_id", ForeignKey("tags.id")),
)


class Image(Base):
    __tablename__ = "images"
    json_field_list = ["id"]

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(Text)
    dir: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean)
    tags: Mapped[List["Tag"]] = relationship(secondary=ImageTag,
                                             back_populates="images", repr=False)

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return self.to_json()


class Tag(Base):
    __tablename__ = "tags"
    json_field_list = ["id", "name", "name_th", "name_en", "description", "tag_type_id"]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    name_en: Mapped[Optional[str]] = mapped_column(Text)
    name_th: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    tag_type_id: Mapped[int] = mapped_column(ForeignKey("tag_types.id"))
    active: Mapped[bool] = mapped_column(Boolean)
    images: Mapped[List["Image"]] = relationship(secondary=ImageTag,
                                                 back_populates="tags", repr=False)
    tag_type: Mapped["TagType"] = relationship(back_populates="tags", repr=False)

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return self.to_json()


class TagType(Base):
    __tablename__ = "tag_types"
    json_field_list = ["id", "name", "description"]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean)
    tags: Mapped[List["Tag"]] = relationship(back_populates="tag_type", repr=False)


class User(Base):
    __tablename__ = "users"
    json_field_list = ["id", "username", "email", "admin"]

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(Text)
    password: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text)
    admin: Mapped[bool] = mapped_column(Boolean)
    active: Mapped[bool] = mapped_column(Boolean)


if __name__ == "__main__":
    from app import create_app
    import os
    from dotenv import load_dotenv
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    with create_app().app_context():
        load_dotenv()
        engine = create_engine("postgresql://%s:%s@%s:5432/%s" %
                               (os.getenv("DB_USER"),
                                os.getenv("DB_PASS"),
                                os.getenv("DB_SERVER"),
                                os.getenv("DB_DB")))

        with Session(engine) as session:
            q = select(Image).join(ImageTag).join(Tag).where(Tag.id == 2).limit(10)
            result = session.scalars(q).fetchall()
            print(result)
            print(type(result[0]), result[0])
            print("done")
