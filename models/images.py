class DatabaseObject:
    def __init__(self, table_name, field_list, args) -> None:
        super().__init__()
        self.__table_name = table_name
        self.__field_list = field_list
        if len(field_list) > len(args):
            raise KeyError(f"{table_name} object need {len(field_list)} attributes, provided {len(args)}")
        for i in range(0, min(len(field_list), len(args))):
            setattr(self, field_list[i], args[i])

    def get_table_name(self):
        return self.__table_name

    def get_field_list(self):
        return self.__field_list

    def __str__(self):
        return f"Object from table: {self.__table_name} | " \
            + " | ".join([f"{f}: {getattr(self, f)}" for f in self.__field_list])


class Image(DatabaseObject):
    id, filename, image_category_id, path, is_active = None, None, None, None, None

    # These objects aren't meant to be created manually, but instead use data from DB to generate
    def __init__(self, args) -> None:
        super().__init__(table_name="images",
                         field_list=["id", "filename", "image_category_id", "path", "is_active"],
                         args=args)


class ImageCategory(DatabaseObject):
    id, name, description, parent_category_id, is_active = None, None, None, None, None

    # These objects aren't meant to be created manually, but instead use data from DB to generate
    def __init__(self, args) -> None:
        super().__init__(table_name="image_categories",
                         field_list=["id", "name", "description", "parent_category_id", "is_active"],
                         args=args)


if __name__ == "__main__":
    img_cat1 = ImageCategory([12, "durianx", "hahahahahahahahahah", 1, True])
    print(img_cat1.id)
    print(img_cat1.name)
    print(img_cat1.description)
    print(img_cat1.parent_category_id)
    print(img_cat1)
    img1 = Image([9, "durianx.jpg", 1, "hello/durianx.jpg", True])
    print(img1.id)
    print(img1.path)
    print(img1.filename)
    print(img1.image_category_id)
    print(img1)