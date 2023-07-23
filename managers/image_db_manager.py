import os
from dotenv import load_dotenv
from connectors.db_connector import DBConnector


def inactivate_folder_images() -> None:
    dbc = DBConnector()
    dbc.execute("update image_categories set active=FALSE WHERE TRUE")
    dbc.commit()
    dbc.execute("update images set active=FALSE WHERE TRUE")
    dbc.commit()
    dbc.terminate()


# traverse through path and put image folders to db
# set all existing images and image_categories that don't have corresponding files/folders to False
# only 2 levels of directories are stored:
# - main_cat_level: used to identify the main category of image
# - main_cat_level + 1: the level directly within main_cat_level as subcategories
# manual DB connection pool for fast processing
# return list of (path_to_folder, level, list of files) of all sub-folders
def sync_image_folder_with_db(path: str, main_cat_level: int = -1) -> list[tuple[str, int, list[str]]]:
    dbc = DBConnector()
    inactivate_folder_images()
    result = __traverse_path(path, main_cat_level, dbc=dbc)
    dbc.terminate()
    return result


# helper function for traversing path
# only 2 levels of directories are stored:
# - main_cat_level: used to identify the main category of image
# - main_cat_level + 1: the level directly within main_cat_level as subcategories
# return list of (path_to_folder, level, list of files) of all sub-folders
def __traverse_path(path: str, main_cat_level: int, dbc: DBConnector,
                    level: int = 0, image_category: str = None) -> list[tuple[str, int, list[str]]]:
    items = os.listdir(path)
    sub_folders = list(filter(lambda _: os.path.isdir(os.path.join(path, _)), items))
    items = list(filter(lambda _: _ not in sub_folders, items))
    new_cat_id = None
    if level == main_cat_level:
        main_cat_name = os.path.basename(path)
        dbc.execute(f"insert into image_categories "
                    f"(name, description, parent_category_id) "
                    f"values ('{main_cat_name}', '', NULL) "
                    f"on conflict "
                    f"on constraint image_categories_name_parent_category_id_key "
                    f"do update set active=True returning id;")
        dbc.commit()
        new_cat_id = dbc.fetchone()[0]

    result = [(path, level, items)]
    if image_category is not None:
        for i in items:
            dbc.execute(f"insert into images (filename, image_category_id, dir) "
                        f"values ('{i}', {image_category}, '{path}') "
                        f"on conflict on constraint images_filename_image_category_id_key "
                        f"do update set active=True;")
            dbc.commit()

    for sf in sub_folders:
        print(sf, level, main_cat_level)
        new_image_cat_id = image_category  # use a new variable to not contaminate the input argument
        if level == main_cat_level:
            dbc.execute(f"insert into image_categories "
                        f"(name, description, parent_category_id) "
                        f"values ('{sf}', '', {new_cat_id}) "
                        f"on conflict "
                        f"on constraint image_categories_name_parent_category_id_key "
                        f"do update set active=True returning id;")
            dbc.commit()
            new_image_cat_id = dbc.fetchone()[0]

        result.append(__traverse_path(os.path.join(path, sf), main_cat_level, dbc, level + 1, new_image_cat_id))
    return result


if __name__ == "__main__":
    load_dotenv()
    all_image_path = os.getenv("IMAGE_ROOT")
    all_images = sync_image_folder_with_db(all_image_path, main_cat_level=1)
    print(len(all_images))
