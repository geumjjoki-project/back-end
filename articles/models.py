from django.db import models
from django.conf import settings

# Create your models here.


# 게시글
class Article(models.Model):
    ##################################################
    # 게시글식별자
    article_id = models.BigAutoField(
        primary_key=True,
    )
    # 작성자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # 제목
    title = models.CharField(
        max_length=100,
    )
    # 내용
    content = models.TextField()
    
    # 생성일시
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    # 수정일시
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    # 조회 수
    views = models.IntegerField(
        default=0,
    )
    ##################################################


# 게시글이미지
class ArticleImage(models.Model):
    ##################################################
    # 게시글이미지식별자
    article_image_id = models.BigAutoField(
        primary_key=True,
    )
    # 게시글식별자
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="images",
    )
    # 이미지
    image = models.ImageField(
        upload_to="articles/%Y/%m/%d/",
    )
    # 업로드일시
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )
    ##################################################


# 댓글
class Comment(models.Model):
    ##################################################
    # 댓글식별자
    comment_id = models.BigAutoField(
        primary_key=True,
    )
    # 게시글식별자
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )
    # 작성자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # 대댓글
    parent_comment = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    # 내용
    content = models.TextField()
    # 생성일시
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    # 수정일시
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    ##################################################


# 게시글 좋아요
class ArticleLike(models.Model):
    ##################################################
    # 좋아요식별자
    like_id = models.BigAutoField(
        primary_key=True,
    )
    # 게시글식별자
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    # 사용자식별자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="article_likes",
    )
    # 생성일시
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = ('article', 'user')  # 한 사용자는 한 게시글에 한 번만 좋아요 가능
    ##################################################

class CommentLike(models.Model):
    ##################################################
    # 좋아요식별자
    like_id = models.BigAutoField(
        primary_key=True,
    )
    # 사용자식별자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_likes",
    )
    # 댓글식별자
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    # 생성일시
    created_at = models.DateTimeField(
        auto_now_add=True,
    ) 
    
    class Meta:
        unique_together = ('comment', 'user')  # 한 사용자는 한 댓글에 한 번만 좋아요 가능
    ##################################################
