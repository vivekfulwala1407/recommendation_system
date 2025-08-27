from rest_framework import serializers
from ..models.post import Post
from ..models.post_metadata import PostMetadata

class PostSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'image', 'category', 'created_at', 'updated_at', 'user', 'likes', 'comments', 'shares']
        read_only_fields = ['user', 'created_at', 'updated_at', 'likes', 'comments', 'shares']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        if 'category' in validated_data:
            instance.category = validated_data.get('category', instance.category)
        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()
        return instance

    def get_category(self, obj):
        metadata = PostMetadata.objects(post_id=obj.id).first() #type: ignore
        return metadata.category if metadata else ""