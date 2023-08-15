from managers.image_manager import fetch_images, fetch_image_tags
from random import sample, shuffle
from connectors import db_connector as dbc
from models.db_modelsx import ImageX, TagX


def random_question(num_choices=4):
    all_cats = fetch_image_tags()
    correct_cat = sample(fetch_image_tags(), 1)[0]
    print(correct_cat)
    image = sample(fetch_images({"tag_ids": tuple([correct_cat.id])}), 1)[0]

    similar_cats = list(filter(lambda _: _.tag_type_id == correct_cat.tag_type_id, all_cats))
    return image, similar_cats


# pick 1 ImageCategory as the target
# if main_category_id is provided, find ImageCategory of that id
# if main_category_id is -1, find a random ImageCategory that's a sub-category
# if main_category_id is None, find a random ImageCategory that's a main category
# TODO: this is a terrible idea. The whole categories things should be changed
def pick_target_from_main_category_id(treasure_cat_id: int) -> TagX:
    if treasure_cat_id == -1:
        return sample(list(filter(lambda _: _.tag_type_id is not None,
                                  fetch_image_tags())), 1)[0]
    elif treasure_cat_id is None:
        return sample(list(filter(lambda _: _.tag_type_id is None,
                                  fetch_image_tags())), 1)[0]
    else:
        return sample(list(filter(lambda _: _.id == treasure_cat_id,
                                  fetch_image_tags())), 1)[0]


def image_treasure_hunt(size=25, treasure_count=5, main_category_id=-1):
    treasure_cat_id = pick_target_from_main_category_id(main_category_id).id
    print(treasure_cat_id)
    treasures = list(map(lambda _: ImageX(_),
                         dbc.select_all("select images.id, images.filename, images.dir, images.active, "
                                        "STRING_AGG(itags.tag_id::text, ',') as tag_id "
                                        "from images inner join image_tags itags on images.id = itags.image_id "
                                        "where itags.tag_id = %s and images.active = true and itags.active = true "
                                        "group by images.id, images.filename, images.dir, images.active "
                                        "order by random() limit %s;", [treasure_cat_id, treasure_count])))
    other = list(map(lambda _: ImageX(_),
                     dbc.select_all("select images.id, images.filename, images.dir, images.active, "
                                    "STRING_AGG(itags.tag_id::text, ',') as tag_id "
                                    "from images inner join image_tags itags on images.id = itags.image_id "
                                    "where itags.tag_id != %s and images.active = true and itags.active = true "
                                    "group by images.id, images.filename, images.dir, images.active "
                                    "order by random() limit %s;", [treasure_cat_id, size - treasure_count])))
    all_img = treasures + other
    shuffle(all_img)
    return all_img, treasure_cat_id


def image_quick_draw(n_rounds=10, n_choices=2, treasure_cat_id=-1) -> tuple[list[list[ImageX]], int]:
    treasure_cat_id = pick_target_from_main_category_id(treasure_cat_id).id
    treasures = list(map(lambda _: ImageX(_),
                         dbc.select_all("select images.id, images.filename, images.dir, images.active, "
                                        "STRING_AGG(itags.tag_id::text, ',') as tag_id "
                                        "from images inner join image_tags itags on images.id = itags.image_id "
                                        "where itags.tag_id = %s and images.active = true and itags.active = true "
                                        "group by images.id, images.filename, images.dir, images.active "
                                        "order by random() limit %s;", [treasure_cat_id, n_rounds])))
    other = list(map(lambda _: ImageX(_),
                     dbc.select_all("select images.id, images.filename, images.dir, images.active, "
                                    "STRING_AGG(itags.tag_id::text, ',') as tag_id "
                                    "from images inner join image_tags itags on images.id = itags.image_id "
                                    "where itags.tag_id != %s and images.active = true and itags.active = true "
                                    "group by images.id, images.filename, images.dir, images.active "
                                    "order by random() limit %s;", [treasure_cat_id, n_rounds * (n_choices - 1)])))

    all_img = [[t] + [other.pop() for _ in range(n_choices - 1)] for t in treasures]
    [shuffle(_) for _ in all_img]  # shuffle choices of each problem
    shuffle(all_img)  # shuffle problems
    return all_img, treasure_cat_id


if __name__ == "__main__":
    q, a = random_question()
    print("Question:", q)
    print(*a, sep="\n")

    durian = list(filter(lambda _: _.name == "durian", fetch_image_tags()))[0]
    print("drr", durian)
    a, b = image_treasure_hunt(25, 5, durian.id)
    for x, y in zip(a, b):
        print(y, x)
