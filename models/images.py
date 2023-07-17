class DatabaseObject:
    def __init__(self, table_name, field_list, **kwargs) -> None:
        super().__init__()
        self.__table_name = table_name
        self.__field_list = field_list
        missing_fields = list(filter(lambda f: f not in kwargs.keys(), field_list))
        if len(missing_fields) > 0:
            raise KeyError(f"For {table_name} object, the following fields are missing: {missing_fields}")
        for kw, arg in kwargs.items():
            setattr(self, kw, arg)

    def get_table_name(self):
        return self.__table_name

    def get_field_list(self):
        return self.__field_list


class Image(DatabaseObject):
    id, filename, image_category_id, path = None, None, None, None

    # These objects aren't meant to be created manually, but instead use data from DB to generate
    def __init__(self, **kwargs) -> None:
        super().__init__(table_name="images",
                         field_list=["id", "filename", "image_category_id", "path"],
                         **kwargs)


class ImageCategory(DatabaseObject):
    id, name, description, parent_category_id = None, None, None, None

    # These objects aren't meant to be created manually, but instead use data from DB to generate
    def __init__(self, **kwargs) -> None:
        super().__init__(table_name="images",
                         field_list=["id", "name", "description", "parent_category_id"],
                         **kwargs)


if __name__ == "__main__":
    img_cat1 = ImageCategory(id=12, name="durianx", description="hahahahahahahahahah", parent_category_id=1)
    print(img_cat1.id)
    print(img_cat1.name)
    print(img_cat1.description)
    print(img_cat1.parent_category_id)
    img1 = Image(id=9, filename="durianx.jpg", image_category_id=1, path="hello/durianx.jpg")
    print(img1.id)
    print(img1.path)
    print(img1.filename)
    print(img1.image_category_id)
