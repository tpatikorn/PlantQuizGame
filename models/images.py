class DatabaseObject:
    """
    constructor for any DatabaseObject
    for subclasses, recommend overriding this __init__ with pre-populated table_name and field_list
    and pass args as list/tuple (no need for starred notation)
    must be constructed with either
    - len(args) == len(field_list) (__initialized flag will be set to True, all fields will be populated)
    - len(args) == 0 (blank object, __initialized flag will be set to False, and all fields to None)
    """

    def __init__(self, table_name, field_list, args) -> None:
        super().__init__()
        self.__table_name = table_name
        self.__field_list = field_list
        if len(args) == 0:
            self.__initialized = False
            for _ in field_list:
                setattr(self, _, None)
        else:
            self.__initialized = True
            if len(field_list) != len(args):
                raise KeyError(f"{table_name} object expected {len(field_list)} attributes, provided {len(args)}")
            for f in field_list:
                print(args)
                setattr(self, f, args[f])

    def get_table_name(self):
        return self.__table_name

    def get_field_list(self):
        return self.__field_list

    def __str__(self):
        return f"Object from table: {self.__table_name} | " \
            + " | ".join([f"{f}: {getattr(self, f)}" for f in self.__field_list])

    def get_query(self, field_sublist):
        query = f"select * from {self.__table_name} where "
        if "is_active" in self.__field_list and "is_active" not in field_sublist:
            query = query + "is_active = True"
            if len(field_sublist) > 0:
                query = query + " and "
        return query + " and ".join([f"{k} = %s" for k in field_sublist])


class Image(DatabaseObject):
    id, filename, image_category_id, path, is_active = None, None, None, None, None
    image_category = None

    # These objects aren't meant to be created manually, but instead use data from DB to generate
    def __init__(self, args=()) -> None:
        super().__init__(table_name="images",
                         field_list=["id", "filename", "image_category_id", "path", "is_active"],
                         args=args)


class ImageCategory(DatabaseObject):
    id, name, description, parent_category_id, is_active = None, None, None, None, None
    parent_category = None

    # These objects aren't meant to be created manually, but instead use data from DB to generate
    def __init__(self, args=()) -> None:
        super().__init__(table_name="image_categories",
                         field_list=["id", "name", "description", "parent_category_id", "is_active"],
                         args=args)


if __name__ == "__main__":
    img_cat1 = ImageCategory({"id": 12,
                              "name": "durianx",
                              "description": "hahahahahahahahahah",
                              "parent_category_id": 1,
                              "is_active": True})
    print(img_cat1.id)
    print(img_cat1.name)
    print(img_cat1.description)
    print(img_cat1.parent_category_id)
    print(img_cat1)
    print(ImageCategory().get_query(["name"]))
    img1 = Image({"id": 9,
                  "filename": "durianx.jpg",
                  "image_category_id": 1,
                  "path": "hello/durianx.jpg",
                  "is_active": True})
    print(img1.id)
    print(img1.path)
    print(img1.filename)
    print(img1.image_category_id)
    print(img1)
    print(Image().get_query(["filename", "is_active"]))
