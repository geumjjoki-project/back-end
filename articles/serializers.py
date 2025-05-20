from rest_framework import serializers
from .models import Article, Comment
from django.utils import timezone
from datetime import datetime


class ArticleCreatePutSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.nickname", read_only=True)
    class Meta:
        model = Article
        fields = [
            "article_id",
            "title",
            "content",
            "author",
            "created_at",
        ]

class ArticleListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.nickname", read_only=True)
    content_preview = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "article_id",
            "title",
            "content_preview",
            "time_ago",
            "author",
            "total_comments",
            "likes_count",
            "is_liked",
        ]

    def get_content_preview(self, obj):
        if len(obj.content) > 60:
            return obj.content[:60] + "..."
        return obj.content

    def get_time_ago(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        minutes = diff.total_seconds() / 60
        if minutes < 60:
            return f"{int(minutes)}분 전"


        hours = diff.total_seconds() / 3600
        if hours < 24:
            return f"{int(hours)}시간 전"
        elif hours < 48:
            return "어제"
        elif hours < 72:
            return "2일 전"
        elif hours < 96:
            return "3일 전"
        else:
            return obj.created_at.strftime("%Y-%m-%d")

    def get_total_comments(self, obj):
        # 댓글 수 + 대댓글 수 계산
        comments = obj.comments.all()
        total = len(comments)
        for comment in comments:
            total += comment.replies.count()
        return total

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request:
            return False
            
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
            
        return obj.likes.filter(user=user).exists()


class ArticleDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.nickname", read_only=True)
    author_profile_image = serializers.CharField(source="user.profile_image", read_only=True)
    time_ago = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            "article_id",
            "title",
            "content",
            "author",
            "author_profile_image",
            "time_ago",
            "likes_count",
            "is_liked",
            "views",
        ]
    
    def get_time_ago(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        minutes = diff.total_seconds() / 60
        if minutes < 60:
            return f"{int(minutes)}분 전"
        
        hours = diff.total_seconds() / 3600
        if hours < 24:
            return f"{int(hours)}시간 전"
        elif hours < 48:
            return "어제"
        elif hours < 72:
            return "2일 전"
        elif hours < 96:
            return "3일 전"
        else:
            return obj.created_at.strftime("%Y-%m-%d")
    
    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request:
            return False
            
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
            
        return obj.likes.filter(user=user).exists()
    
class ReplySerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.nickname", read_only=True)
    author_profile_image = serializers.CharField(source="user.profile_image", read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    def get_time_ago(self, obj):
        return obj.created_at.strftime("%m/%d %H:%M")
    
    class Meta:
        model = Comment
        fields = [
            "reply_id",
            "content",
            "author",
            "author_profile_image",
            "time_ago",
        ]

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.nickname", read_only=True)
    author_profile_image = serializers.CharField(source="user.profile_image", read_only=True)
    time_ago = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    def get_replies(self, obj):
        replies = obj.replies.all()
        return ReplySerializer(replies, many=True).data
    
    def get_time_ago(self, obj):
        return obj.created_at.strftime("%m/%d %H:%M")
    
    class Meta:
        model = Comment
        fields = [
            "comment_id",
            "content",
            "author",
            "author_profile_image",
            "time_ago",
            "replies",
        ]

class CommentCreatePutSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.nickname", read_only=True)
    class Meta:
        model = Comment
        fields = [
            "article_id",
            "comment_id",
            "author",
            "content",
            "created_at",
            "updated_at",
        ]
    
