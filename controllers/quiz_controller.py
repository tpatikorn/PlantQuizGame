from managers.image_manager import ImageCacheManager
from random import sample


def random_question(num_choices=4):
    correct_cat = sample(list(ImageCacheManager.get_images().keys()), 1)[0]
    image = sample(ImageCacheManager.get_images()[correct_cat], 1)[0]
    all_cats = ImageCacheManager.get_image_categories()

    similar_cats = list(filter(lambda _: _.parent_category_id == correct_cat.parent_category_id, all_cats))
    return image, similar_cats


if __name__ == "__main__":
    ImageCacheManager.update_cache()
    q, a = random_question()
    print("Question:", q)
    print(*a, sep="\n")
