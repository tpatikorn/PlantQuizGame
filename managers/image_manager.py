from connectors.db_connector import get_cursor as cur
from connectors.db_connector import terminate_db_connection
from models.images import Image, ImageCategory


def fetch_image_categories() -> list[ImageCategory]:
    cur().execute("select * from image_categories where is_active = True")
    return list(map(lambda _: ImageCategory(_), cur().fetchall()))


def fetch_images() -> list[Image]:
    cur().execute("select * from image_categories where is_active = True")
    return list(map(lambda _: Image(_), cur().fetchall()))


if __name__ == "__main__":
    print(*fetch_image_categories(), sep="\n")
    print(*fetch_images(), sep="\n")
    terminate_db_connection()
