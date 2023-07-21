import os
from dotenv import load_dotenv
from connectors import db_connector as dbc


def inactivate_folder_images() -> None:
    dbc.execute_commit("update image_categories set is_active=FALSE WHERE TRUE")
    dbc.execute_commit("update images set is_active=FALSE WHERE TRUE")


# traverse through path and put image folders to db
# set all existing images and image_categories that don't have corresponding files/folders to False
# only 2 levels of directories are stored:
# - main_cat_level: used to identify the main category of image
# - main_cat_level + 1: the level directly within main_cat_level as subcategories
# return list of (path_to_folder, level, list of files) of all sub-folders
def sync_image_folder_with_db(path: str, main_cat_level: int = -1) -> list[tuple[str, int, list[str]]]:
    inactivate_folder_images()
    return _traverse_path(path, main_cat_level)


# helper function for traversing path
# only 2 levels of directories are stored:
# - main_cat_level: used to identify the main category of image
# - main_cat_level + 1: the level directly within main_cat_level as subcategories
# return list of (path_to_folder, level, list of files) of all sub-folders
def _traverse_path(path: str, main_cat_level: int = -1, level: int = 0,
                   image_category: str = None) -> list[tuple[str, int, list[str]]]:
    items = os.listdir(path)
    sub_folders = list(filter(lambda _: os.path.isdir(os.path.join(path, _)), items))
    items = list(filter(lambda _: _ not in sub_folders, items))
    new_cat_id = None
    if level == main_cat_level:
        main_cat_name = os.path.basename(path)
        new_cat_id = dbc.execute_commit_fetch(f"insert into image_categories "
                                              f"(name, description, parent_category_id) "
                                              f"values ('{main_cat_name}', '', NULL) "
                                              f"on conflict "
                                              f"on constraint image_categories_name_parent_category_id_key "
                                              f"do update set is_active=True returning id;")[0]

    result = [(path, level, items)]
    if image_category is not None:
        for i in items:
            dbc.execute_commit(f"insert into images (filename, image_category_id, path) "
                               f"values ('{i}', {image_category}, '{os.path.join(path, i)}') "
                               f"on conflict on constraint images_filename_image_category_id_key "
                               f"do update set is_active=True;")

    for sf in sub_folders:
        print(sf, level, main_cat_level)
        new_image_cat_id = image_category  # use a new variable to not contaminate the input argument
        if level == main_cat_level:
            new_image_cat_id = dbc.execute_commit_fetch(f"insert into image_categories "
                                                        f"(name, description, parent_category_id) "
                                                        f"values ('{sf}', '', {new_cat_id}) "
                                                        f"on conflict "
                                                        f"on constraint image_categories_name_parent_category_id_key "
                                                        f"do update set is_active=True returning id;")[0]
        result.append(_traverse_path(os.path.join(path, sf), main_cat_level, level + 1, new_image_cat_id))
    return result


if __name__ == "__main__":
    load_dotenv()
    all_image_path = os.getenv("IMAGE_ROOT")
    all_images = sync_image_folder_with_db(all_image_path, main_cat_level=1)
    print(all_images)
