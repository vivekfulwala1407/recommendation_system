from ..models.post import Post
from django.contrib.auth import get_user_model
from ..models.post_metadata import PostMetadata
import random
import logging
import nltk
from collections import Counter, defaultdict
from nltk.corpus import wordnet as wn

nltk.download('wordnet')

logger = logging.getLogger(__name__)

User = get_user_model()

CATEGORY_GROUPS = {
    "food": ["food"],
    "vehicles": ["vehicles"], 
    "animals": ["animals"],
    "sports": ["sports"],
    "technology": ["technology"],
    "clothing": ["clothing"],
    "furniture": ["furniture"],
    "nature": ["nature"],
    "general": ["general"]
}

def get_related_categories(category):
    category_lower = category.lower().strip()
    related = set([category_lower])
    for main_cat, sub_cats in CATEGORY_GROUPS.items():
        if category_lower in sub_cats or category_lower == main_cat:
            related.add(main_cat)
            related.update(sub_cats)
            break
    try:
        synsets = wn.synsets(category, pos=wn.NOUN)
        if synsets and synsets[0]:
            for lemma in synsets[0].lemma_names():
                related.add(lemma.replace("_", " ").lower())
            hypernyms = synsets[0].hypernyms()
            level = 0
            while hypernyms and level < 2:
                hypernym_name = hypernyms[0].lemma_names()[0].replace("_", " ").lower()
                related.add(hypernym_name)
                hypernyms = hypernyms[0].hypernyms()
                level += 1
    except Exception as e:
        logger.debug(f"WordNet lookup failed for {category}: {str(e)}")
    return related

def build_personalized_feed(user):
    posts = list(Post.objects.all().order_by('-created_at'))
    interests = user.interests if user.interests else {}
    logger.info(f"Building feed for user {user.username} with interests: {interests}")
    
    try:
        if not interests:
            random.shuffle(posts)
            return posts[:10]
        
        total_weight = sum(interests.values())
        categorized_posts = defaultdict(list)
        other_posts = []
        
        for post in posts:
            metadata = PostMetadata.objects(post_id=post.pk).first()  # type: ignore
            if not metadata:
                continue
                
            category = metadata.category.lower()
            if category in interests:
                categorized_posts[category].append(post)
            else:
                other_posts.append(post)
        
        weighted_feed = []
        target_length = 10
        interested_count = int(target_length * 0.7)  
        random_count = target_length - interested_count  
        
        for category, score in interests.items():
            if category in categorized_posts:
                category_weight = score / total_weight
                category_count = int(interested_count * category_weight)
                category_posts = categorized_posts[category]
                random.shuffle(category_posts)
                weighted_feed.extend(category_posts[:category_count])
        
        while len(weighted_feed) < interested_count and any(categorized_posts.values()):
            for category in interests:
                if category in categorized_posts and categorized_posts[category]:
                    weighted_feed.append(categorized_posts[category].pop())
                    if len(weighted_feed) >= interested_count:
                        break
        
        random.shuffle(other_posts)
        weighted_feed.extend(other_posts[:random_count])
        
        random.shuffle(weighted_feed)
        
        final_categories = []
        for post in weighted_feed:
            metadata = PostMetadata.objects(post_id=post.pk).first()  # type: ignore
            if metadata:
                final_categories.append(metadata.category)
        logger.info(f"Final feed category distribution: {Counter(final_categories)}")
        return weighted_feed[:target_length]  
    except Exception as e:
        logger.error(f"Error building personalized feed: {str(e)}")
        return []