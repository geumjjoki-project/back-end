import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from articles.models import Article, Comment, ArticleLike, CommentLike

User = get_user_model()

class Command(BaseCommand):
    help = "기존 사용자 기반으로 게시글, 댓글, 좋아요 더미 데이터를 생성합니다."

    def add_arguments(self, parser):
        parser.add_argument("--articles", type=int, default=50)
        parser.add_argument("--comments", type=int, default=100)

    def handle(self, *args, **options):
        article_count = options["articles"]
        comment_count = options["comments"]

        users = list(User.objects.all()[:100])
        if not users:
            self.stdout.write(self.style.ERROR("❌ 사용자 없음. 먼저 유저 생성 필요"))
            return

        # 게시글 생성
        articles = []
        for i in range(article_count):
            article = Article.objects.create(
                user=random.choice(users),
                title=f"샘플 제목 {i}",
                content="내용입니다." * random.randint(2, 5),
                views=random.randint(0, 100)
            )
            articles.append(article)

        # 댓글 생성 (parent_comment가 있어 bulk_create 사용 불가)
        comments = []
        for _ in range(comment_count):
            article = random.choice(articles)
            user = random.choice(users)
            parent = random.choice(comments) if comments and random.random() < 0.2 else None
            comment = Comment.objects.create(
                article=article,
                user=user,
                parent_comment=parent,
                content="댓글입니다." * random.randint(1, 2)
            )
            comments.append(comment)

        # 게시글 좋아요 생성
        article_likes = []
        for article in articles:
            liked_users = random.sample(users, k=random.randint(0, min(5, len(users))))
            for user in liked_users:
                article_likes.append(ArticleLike(article=article, user=user))
        ArticleLike.objects.bulk_create(article_likes, ignore_conflicts=True)

        # 댓글 좋아요 생성
        comment_likes = []
        for comment in comments:
            liked_users = random.sample(users, k=random.randint(0, min(5, len(users))))
            for user in liked_users:
                comment_likes.append(CommentLike(comment=comment, user=user))
        CommentLike.objects.bulk_create(comment_likes, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS("✅ 더미 데이터 생성 완료"))
