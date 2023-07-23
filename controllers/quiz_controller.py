from managers.image_manager import ImageCacheManager
from random import sample, shuffle
from connectors import db_connector as dbc
from models.db_models import Image, ImageCategory


def random_question(num_choices=4):
    correct_cat = sample(ImageCacheManager.get_image_categories(exclude_main=True), 1)[0]
    image = sample(ImageCacheManager.get_images()[correct_cat], 1)[0]
    all_cats = ImageCacheManager.get_image_categories()

    similar_cats = list(filter(lambda _: _.parent_category_id == correct_cat.parent_category_id, all_cats))
    return image, similar_cats


def image_treasure_hunt(size=25, treasure_count=5, main_category_id=-1):
    if main_category_id == -1:
        def flt(_):
            return _.parent_category_id is not None
    elif main_category_id is None:
        def flt(_):
            return _.parent_category_id is None
    else:
        def flt(_):
            return _.parent_category_id == main_category_id
    treasure_cat_id = sample(list(filter(flt, ImageCacheManager.get_image_categories())), 1)[0].id
    treasures = list(map(lambda _: Image(_),
                         dbc.select_all("select * from images "
                                        "where image_category_id = %s and active = true "
                                        "order by random() limit %s;", [treasure_cat_id, treasure_count])))
    other = list(map(lambda _: Image(_),
                     dbc.select_all("select * from images "
                                    "where image_category_id != %s and active = true "
                                    "order by random() limit %s;", [treasure_cat_id, size - treasure_count])))
    all_img = treasures + other
    shuffle(all_img)
    return all_img, list(map(lambda _: _.image_category_id == treasure_cat_id, all_img))


if __name__ == "__main__":
    ImageCacheManager.update_cache()
    q, a = random_question()
    print("Question:", q)
    print(*a, sep="\n")

    durian = list(filter(lambda _: _.name == "durian", ImageCacheManager.get_image_categories()))[0]
    a, b = image_treasure_hunt(25, 5, durian.id)
    for x, y in zip(a, b):
        print(y, x)
