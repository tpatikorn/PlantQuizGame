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


# pick 1 ImageCategory as the target
# if main_category_id is provided, find ImageCategory of that id
# if main_category_id is -1, find a random ImageCategory that's a sub-category
# if main_category_id is None, find a random ImageCategory that's a main category
# TODO: this is a terrible idea. The whole categories things should be changed
def pick_target_from_main_category_id(main_category_id: int) -> ImageCategory:
    if main_category_id == -1:
        return sample(list(filter(lambda _: _.parent_category_id is not None,
                                  ImageCacheManager.get_image_categories())), 1)[0]
    elif main_category_id is None:
        return sample(list(filter(lambda _: _.parent_category_id is None,
                                  ImageCacheManager.get_image_categories())), 1)[0]
    else:
        return sample(list(filter(lambda _: _.parent_category_id == main_category_id,
                                  ImageCacheManager.get_image_categories())), 1)[0]


def image_treasure_hunt(size=25, treasure_count=5, main_category_id=-1):
    treasure_cat_id = pick_target_from_main_category_id(main_category_id).id
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


def image_quick_draw(n_rounds=10, n_choices=2, main_category_id=-1):
    treasure_cat_id = pick_target_from_main_category_id(main_category_id).id
    treasures = list(map(lambda _: Image(_),
                         dbc.select_all("select * from images "
                                        "where image_category_id = %s and active = true "
                                        "order by random() limit %s;", [treasure_cat_id, n_rounds])))
    other = list(map(lambda _: Image(_),
                     dbc.select_all("select * from images "
                                    "where image_category_id != %s and active = true "
                                    "order by random() limit %s;", [treasure_cat_id, n_rounds * (n_choices - 1)])))

    all_img = [[t] + [other.pop() for _ in range(n_choices - 1)] for t in treasures]
    [shuffle(_) for _ in all_img] # shuffle choices of each problem
    shuffle(all_img) # shuffle problems
    return all_img, treasure_cat_id


if __name__ == "__main__":
    ImageCacheManager.update_cache()
    q, a = random_question()
    print("Question:", q)
    print(*a, sep="\n")

    durian = list(filter(lambda _: _.name == "durian", ImageCacheManager.get_image_categories()))[0]
    a, b = image_treasure_hunt(25, 5, durian.id)
    for x, y in zip(a, b):
        print(y, x)
