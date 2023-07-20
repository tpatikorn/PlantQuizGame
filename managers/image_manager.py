from connectors.db_connector import get_cursor as cur
from connectors.db_connector import terminate_db_connection
from models.images import Image, ImageCategory


class ImageCacheManager(object):
    __images, __image_categories, __initialized, obj = None, None, False, None

    def __new__(cls, root_path, main_cat_level):
        if cls.__initialized:
            return cls.obj
        else:
            cls.obj = super(ImageCacheManager, cls).__new__(cls)
            cls.__images = dict()
            cls.__image_categories = dict()
            cls.obj.__dict__ = {
                "images": cls.__images,
                "image_categories": cls.__image_categories,
                "initialized": True
            }
            cls.__initialized = True
            return cls.obj

    @staticmethod
    def get_images() -> dict[ImageCategory, list[Image]]:
        return ImageCacheManager.__images

    @staticmethod
    def get_image_categories() -> list[ImageCategory]:
        return ImageCacheManager.__image_categories

    @staticmethod
    def update_cache() -> None:
        cats = fetch_image_categories()
        cat_queue = list(filter(lambda _: _.parent_category_id is None, cats))
        cat_done = []
        while len(cat_queue) > 0:
            this_cat = cat_queue.pop()
            for c in list(filter(lambda _: _.parent_category_id == this_cat.id, cats)):
                c.parent_category = this_cat
                cat_queue.append(c)
            cats = list(filter(lambda _: _.parent_category_id != this_cat.id, cats))
            cat_done.append(this_cat)
        ImageCacheManager.__image_categories = cat_done + cat_queue

        ImageCacheManager.__images = dict()
        imgs = fetch_images()
        for cat in ImageCacheManager.__image_categories:
            ImageCacheManager.__images[cat] = list(filter(lambda _: _.image_category_id == cat.id, imgs))


def fetch_image_categories(query_dict: dict = None) -> list[ImageCategory]:
    if query_dict is None:
        query_dict = {}
    cur().execute(ImageCategory().get_query(query_dict.keys()), list(query_dict.values()))
    result = list(map(lambda _: ImageCategory(_), cur().fetchall()))
    return result


def fetch_images(query_dict: dict = None) -> list[Image]:
    if query_dict is None:
        query_dict = {}
    cur().execute(Image().get_query(query_dict.keys()), list(query_dict.values()))
    return list(map(lambda _: Image(_), cur().fetchall()))


if __name__ == "__main__":
    ImageCacheManager.update_cache()
    for c in ImageCacheManager.get_image_categories():
        print(c, c.parent_category)
    for c, i in ImageCacheManager.get_images().items():
        print(c, i)
    # print("=============================")
    # print(*fetch_image_categories(), sep="\n")
    # print("=============================")
    # print(*fetch_images(), sep="\n")
    # print("=============================")
    # print(*fetch_images({"image_category_id": 6}), sep="\n")
    # print("=============================")
    # print(*fetch_image_categories({"name": "banana", "is_active": False}), sep="\n")
    # print("=============================")
    # print(*fetch_image_categories({"name": "banana", "is_active": True}), sep="\n")
    # print("=============================")
    terminate_db_connection()
