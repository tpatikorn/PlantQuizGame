import os
from connectors.db_connector import DBConnector
import itertools


def inactivate_folder_images() -> None:
    dbc = DBConnector()
    dbc.execute("update tag_types set active=FALSE WHERE TRUE")
    dbc.execute("update tags set active=FALSE WHERE TRUE")
    dbc.execute("update image_tags set active=FALSE WHERE TRUE")
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
def sync_image_folder_with_db(path: str, folder_level_tags: list[int] = None) -> list[tuple[str, int, list[str]]]:
    if folder_level_tags is None:
        folder_level_tags = [0, 1, 2, 3, 4, 5]
    dbc = DBConnector()
    inactivate_folder_images()
    result = __traverse_path(path, folder_level_tags=folder_level_tags, dbc=dbc, current_tags=[], level=0)
    dbc.terminate()
    return result


# helper function for traversing path
# only 2 levels of directories are stored:
# - main_cat_level: used to identify the main category of image
# - main_cat_level + 1: the level directly within main_cat_level as subcategories
# return list of (path_to_folder, level, list of files) of all sub-folders
def __traverse_path(path: str, folder_level_tags: list[int], dbc: DBConnector,
                    current_tags: list[int], level: int) -> list[tuple[str, int, list[str]]]:
    print(path, level, current_tags)
    items = os.listdir(path)
    sub_folders = list(filter(lambda _: os.path.isdir(os.path.join(path, _)), items))
    items = list(filter(lambda _: _ not in sub_folders, items))
    if level in folder_level_tags:
        tag_name = os.path.basename(path)
        dbc.execute(f"insert into tags "
                    f"(name, tag_type_id, description) "
                    f"values ('{tag_name}', {level}, 'path') "
                    f"on conflict "
                    f"on constraint tags_name_tag_type_id_key "
                    f"do update set active=True returning id;")
        dbc.commit()
        current_tags = current_tags + [dbc.fetchone()[0]]

    result = [(path, level, items)]
    new_image_ids = []
    for i in items:
        dbc.execute(f"insert into images (filename, dir) "
                    f"values ('{i}', '{path}') "
                    f"on conflict on constraint images_filename_dir_key "
                    f"do update set active=True returning id;")
        dbc.commit()
        new_image_ids.append(dbc.fetchone()[0])

    if len(new_image_ids) > 0:
        kv_pairs = ",".join(f"({i}, {t})" for i, t in itertools.product(new_image_ids, current_tags))
        dbc.execute(f"insert into image_tags (image_id, tag_id) values {kv_pairs};")
        dbc.commit()

    for sf in sub_folders:
        result.append(__traverse_path(path=os.path.join(path, sf), dbc=dbc, folder_level_tags=folder_level_tags,
                                      current_tags=current_tags, level=level + 1))
    return result


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    all_image_path = os.getenv("IMAGE_ROOT")
    all_images = sync_image_folder_with_db(all_image_path)
    print(len(all_images))
