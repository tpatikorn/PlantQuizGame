from managers.image_manager import fetch_images, fetch_tags, fetch_images_with_tags
from random import sample, shuffle
from models.db_models import Image, Tag


def random_question(num_choices=4):
    correct_cat = sample(fetch_tags(limit=1), 1)[0]
    image = sample(fetch_images(Tag.id == correct_cat.id), 1)[0]
    similar_cats = fetch_tags(Tag.tag_type_id == correct_cat.tag_type_id, limit=num_choices + 1)
    return image, similar_cats + [correct_cat]


# pick 1 ImageCategory as the target
# if main_category_id is provided, find ImageCategory of that id
# if main_category_id is -1, find a random ImageCategory that's a sub-category
# if main_category_id is None, find a random ImageCategory that's a main category
# TODO: this is a terrible idea. The whole categories things should be changed
def pick_target_from_main_category_id(treasure_cat_id: int) -> Tag:
    if treasure_cat_id == -1:
        return sample(fetch_tags(Tag.tag_type_id == 2), 1)[0]
    elif treasure_cat_id is None:
        return sample(fetch_tags(), 1)[0]
    else:
        return sample(fetch_tags(Tag.id == treasure_cat_id), 1)[0]


def image_treasure_hunt(size=25, treasure_count=5, main_category_id=-1):
    treasure_cat_id = pick_target_from_main_category_id(main_category_id).id
    print(treasure_cat_id)

    treasures = fetch_images_with_tags(include_tags=treasure_cat_id, limit=treasure_count)
    other = fetch_images_with_tags(exclude_tags=treasure_cat_id, limit=size - treasure_count)
    all_img = treasures + other
    answers = ([1] * treasure_count) + ([0] * (size - treasure_count))
    temp = list(zip(all_img, answers))
    shuffle(temp)
    all_img, answers = zip(*temp)
    return all_img, answers


def image_quick_draw(n_rounds=10, n_choices=2, treasure_cat_id=-1) -> tuple[list[list[Image]], list[list[int]]]:
    treasure_cat_id = pick_target_from_main_category_id(treasure_cat_id).id
    treasures = fetch_images_with_tags(include_tags=treasure_cat_id, limit=n_rounds)
    other = fetch_images_with_tags(exclude_tags=treasure_cat_id, limit=n_rounds * (n_choices - 1))
    all_img = [[t] + [other.pop() for _ in range(n_choices - 1)] for t in treasures]
    answers = [[1] + ([0] * (n_choices - 1))] * n_rounds

    for i in range(n_rounds):
        temp = list(zip(all_img[i], answers[i]))
        shuffle(temp)
        all_img[i], answers[i] = zip(*temp)
        all_img[i], answers[i] = list(all_img[i]), list(answers[i])

    temp = list(zip(all_img, answers))
    shuffle(temp)
    all_img, answers = zip(*temp)
    all_img, answers = list(all_img), list(answers)
    return all_img, answers


if __name__ == "__main__":
    def to_test():
        q, a = random_question()
        print("Question:", q)
        print(*a, sep="\n")

        durian = list(filter(lambda _: _.name == "durian", fetch_tags()))[0]
        print("drr", durian)
        a, b = image_treasure_hunt(25, 5, durian.id)
        print(a, b)

    def to_test2():
        from flask import g
        from sqlalchemy import text
        # query for finding a set of "n_rounds" targets
        # then, for each target, find incorrect choices equal to "n_choices"
        # where incorrect choices have the same tags with tag_type_id=1, but different tags with tag_type_id=2
        # e.g. both are durian leaves, but different diseases
        sql_query = text("""
with 
img as (select it.image_id, 
array_agg(t.id) filter(where t.tag_type_id = 1) l1, 
array_agg(t.id) filter(where t.tag_type_id = 2) l2 
from image_tags it inner join tags t on it.tag_id = t.id group by it.image_id order by random()),
correct as (select * from img limit :n_rounds)
select 
correct.image_id, correct.l1, correct.l2, count(*),
array_agg(wrong.image_id) alt_imgs, 
array_agg(wrong.l2) alt_l2 
from correct 
inner join lateral 
(select img.* from img where (img.l1 && correct.l1) and not (img.l2 && correct.l2) limit :n_choices) wrong using (l1)
group by correct.image_id, correct.l1, correct.l2
order by correct.image_id;""")

        result = (
            g.session.execute(sql_query, {"n_rounds": 10, "n_choices": 10})
        ).fetchall()

        for r in result:
            print(r)


    from util.simple_main_test import test_this

    test_this(to_test)
    test_this(to_test2)
