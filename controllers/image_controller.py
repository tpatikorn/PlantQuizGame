import os
from dotenv import load_dotenv
from connectors.db_connector import DBConnector


# traverse through path and put image folders to db
# only 2 levels of directories are stored:
# - main_cat_level: used to identify the main category of image
# - main_cat_level + 1: the level directly within main_cat_level as subcategories
# return list of (path_to_folder, level, list of files) of all sub-folders
def sync_image_folder_with_db(path, main_cat_level=-1, level=0, image_category=None):
    conn, cur = DBConnector().get_connector_cursor()
    items = os.listdir(path)
    sub_folders = list(filter(lambda i: os.path.isdir(os.path.join(path, i)), items))
    items = list(filter(lambda i: i not in sub_folders, items))
    new_cat_id = None
    if level == main_cat_level:
        main_cat_name = os.path.basename(path)
        cur.execute(f"insert into image_categories (name, description, parent_category_id) "
                    f"values ('{main_cat_name}', '', NULL) "
                    f"on conflict on constraint image_categories_name_parent_category_id_key "
                    f"do update set name=excluded.name returning id;")
        conn.commit()
        new_cat_id = cur.fetchone()[0]
        print("new_cat_id", new_cat_id)

    result = [(path, level, items)]
    if image_category is not None:
        for i in items:
            cur.execute(f"insert into images (filename, image_category_id, path) "
                        f"values ('{i}', {image_category}, '{os.path.join(path, i)}') on conflict do nothing;")
        conn.commit()

    for sf in sub_folders:
        print(sf, level, main_cat_level)
        new_image_cat_id = image_category  # use a new variable to not contaminate the input argument
        if level == main_cat_level:
            cur.execute(f"insert into image_categories (name, description, parent_category_id) "
                        f"values ('{sf}', '', {new_cat_id})"
                        f"on conflict on constraint image_categories_name_parent_category_id_key "
                        f"do update set name=excluded.name returning id;")
            conn.commit()
            new_image_cat_id = cur.fetchone()[0]
        result.append(sync_image_folder_with_db(os.path.join(path, sf), main_cat_level, level + 1, new_image_cat_id))
    return result


if __name__ == "__main__":
    load_dotenv()
    root_path = os.getenv("IMAGE_ROOT")
    plant_type_level = 1
    all_images = sync_image_folder_with_db(root_path, plant_type_level)
    print(all_images)
