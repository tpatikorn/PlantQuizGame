from models.abstract_model import AbstractDatabaseObject


class Image(AbstractDatabaseObject):
    id, filename, dir, active = None, None, None, None
    tags = None

    table_name = "images"
    field_list = ["id", "filename", "dir", "active"]
    json_field_list = ["id"]

    @classmethod
    def get_query(cls, field_sublist: list[str]) -> str:
        if "tag_ids" in field_sublist:
            query = f"select images.*, image_tags.tag_id as image_tag_id " \
                    f"from images inner join image_tags on images.id = image_tags.image_id " \
                    f"where tag_id in %s "
            field_sublist.remove("tag_ids")
            if "active" not in field_sublist:
                query = query + "and image_tags.active = True and images.active = True "
            if len(field_sublist) > 0:
                query = query + " and "
            field_sublist = [f"images.{_}" for _ in field_sublist]
            return query + " and ".join([f"{k} = %s" for k in field_sublist])
        else:
            return super(cls, Image).get_query(field_sublist)


class Tags(AbstractDatabaseObject):
    id, name, name_en, name_th, description, tag_type_id, active = None, None, None, None, None, None, None

    table_name = "tags"
    field_list = ["id", "name", "name_en", "name_th", "description", "tag_type_id", "active"]


class User(AbstractDatabaseObject):
    id, username, password, email, admin, active = None, None, None, None, None, None
    table_name = "users"
    field_list = ["id", "username", "password", "email", "admin", "active"]
    json_field_list = ["id", "username"]


if __name__ == "__main__":
    print(Image.get_query(["tag_ids", "active"]))
    print(Image.get_query(["active"]))
    print(Image.get_query(["tag_ids"]))

    from connectors import db_connector as dbc

    x = dbc.select_all(Image.get_query(["tag_ids"]), [(1, 2)])
    print(x)
