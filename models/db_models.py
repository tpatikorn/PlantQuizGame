from models.abstract_model import AbstractDatabaseObject

# TODO create another class for Image but for view
class Image(AbstractDatabaseObject):
    id, filename, image_category_id, dir, active = None, None, None, None, None
    image_category = None
    table_name = "images"
    field_list = ["id", "filename", "image_category_id", "dir", "active"]
    json_field_list = ["id", "image_category_id", "active"]


class ImageCategory(AbstractDatabaseObject):
    id, name, description, parent_category_id, active = None, None, None, None, None
    parent_category = None
    table_name = "image_categories"
    field_list = ["id", "name", "description", "parent_category_id", "active"]


class User(AbstractDatabaseObject):
    id, username, password, email, admin, active = None, None, None, None, None, None
    table_name = "users"
    field_list = ["id", "username", "password", "email", "admin", "active"]


if __name__ == "__main__":
    img_cat1 = ImageCategory({"id": 12,
                              "name": "durianx",
                              "description": "hahahahahahahahahah",
                              "parent_category_id": 1,
                              "active": True})
    print(img_cat1.id)
    print(img_cat1.name)
    print(img_cat1.description)
    print(img_cat1.parent_category_id)
    print(img_cat1)
    print(ImageCategory.get_query(["name"]))
    img1 = Image({"id": 9,
                  "filename": "durianx.jpg",
                  "image_category_id": 1,
                  "dir": "hello/durianx.jpg",
                  "active": True})
    print(img1.id)
    print(img1.dir)
    print(img1.filename)
    print(img1.image_category_id)
    print(img1)
    print(Image.get_query(["filename", "active"]))
