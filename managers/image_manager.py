from connectors.db_connector import get_cursor as cur
from connectors.db_connector import terminate_db_connection
from models.images import Image, ImageCategory


def fetch_image_categories(query_dict: dict = None) -> list[ImageCategory]:
    if query_dict is None:
        query_dict = {}
    cur().execute(ImageCategory().get_query(query_dict.keys()), list(query_dict.values()))
    return list(map(lambda _: ImageCategory(_), cur().fetchall()))


def fetch_images(query_dict: dict = None) -> list[Image]:
    if query_dict is None:
        query_dict = {}
    cur().execute(Image().get_query(query_dict.keys()), list(query_dict.values()))
    return list(map(lambda _: Image(_), cur().fetchall()))


if __name__ == "__main__":
    print("=============================")
    print(*fetch_image_categories(), sep="\n")
    print("=============================")
    print(*fetch_images(), sep="\n")
    print("=============================")
    print(*fetch_images({"image_category_id": 6}), sep="\n")
    print("=============================")
    print(*fetch_image_categories({"name": "banana", "is_active": False}), sep="\n")
    print("=============================")
    print(*fetch_image_categories({"name": "banana", "is_active": True}), sep="\n")
    print("=============================")
    terminate_db_connection()
