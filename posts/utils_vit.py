from transformers import ViTForImageClassification, ViTFeatureExtractor
from PIL import Image
import torch
from .models_mongo import PostMetadata
import logging
import nltk
from nltk.corpus import wordnet as wn
from .category import CATEGORY_MAPPINGS

nltk.download('wordnet')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

model_name = "google/vit-base-patch16-224"
feature_extractor = ViTFeatureExtractor.from_pretrained(model_name)
model = ViTForImageClassification.from_pretrained(model_name)

def get_super_category(label):
    label_lower = label.lower().strip()
    if label_lower in CATEGORY_MAPPINGS:
        return CATEGORY_MAPPINGS[label_lower]
    for key, category in CATEGORY_MAPPINGS.items():
        if key in label_lower or label_lower in key:
            return category
    synsets = wn.synsets(label, pos=wn.NOUN)
    if synsets and synsets[0]:
        hypernyms = synsets[0].hypernyms()
        level = 0
        while hypernyms and level < 3:
            related = hypernyms[0].lemma_names()[0].replace("_", " ").lower()
            if related in CATEGORY_MAPPINGS:
                return CATEGORY_MAPPINGS[related]
            if "food" in related or "dish" in related or "beverage" in related:
                return "food"
            elif "vehicle" in related or "car" in related or "transport" in related:
                return "vehicles"
            elif "animal" in related or "mammal" in related or "pet" in related:
                return "animals"
            elif "sport" in related or "game" in related:
                return "sports"
            elif "device" in related or "machine" in related or "electronic" in related:
                return "technology"
            hypernyms = hypernyms[0].hypernyms()
            level += 1
    return "general"

def tag_image(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = feature_extractor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        if (
            not hasattr(model, 'config') or
            not hasattr(model.config, 'id2label') or
            model.config.id2label is None
        ):
            logger.error("Model configuration or label mapping not found")
            return {"tags": ["unknown"], "category": "general"}

        predicted_label = model.config.id2label.get(
            predicted_class_idx,
            "unknown"
        ).replace("_", " ").lower()
        logger.info(f"Predicted label: {predicted_label}")
        tags = [predicted_label]
        category = get_super_category(predicted_label)
        logger.info(f"Mapped to category: {category}")
        return {"tags": tags, "category": category}
    except Exception as e:
        logger.error(f"Error in tag_image: {str(e)}")
        return {"tags": ["unknown"], "category": "general"}

def save_metadata(post, image_path):
    metadata = tag_image(image_path)
    existing_metadata = PostMetadata.objects(post_id=post.id).first()  # type: ignore
    if existing_metadata:
        existing_metadata.update(tags=metadata["tags"], category=metadata["category"])
        logger.info(f"Updated metadata for post_id: {post.id} with category: {metadata['category']}")
    else:
        post_metadata = PostMetadata(post_id=post.id, tags=metadata["tags"], category=metadata["category"])
        post_metadata.save()
        logger.info(f"Created metadata for post_id: {post.id} with category: {metadata['category']}")
    return metadata