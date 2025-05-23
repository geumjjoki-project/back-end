import os
import json
import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from articles.models import Article, Comment, ArticleLike, CommentLike
from accounts.models import User
from django.conf import settings


fixture_dir = os.path.join(settings.BASE_DIR, "articles", "fixtures")


class Command(BaseCommand):
    help = "샘플 게시글, 댓글, 좋아요 생성 (sample_articles.json 및 sample_comment_contents.json 필요)"

    def handle(self, *args, **kwargs):
        users = list(User.objects.all())
        if not users:
            self.stdout.write(
                self.style.ERROR("유저가 존재하지 않습니다. 먼저 유저를 생성하세요.")
            )
            return

        with open(
            os.path.join(fixture_dir, "sample_articles.json"), encoding="utf-8"
        ) as f:
            article_data = json.load(f)
        with open(
            os.path.join(fixture_dir, "sample_comment_contents.json"), encoding="utf-8"
        ) as f:
            comment_contents = json.load(f)

        now = datetime.now()

        def random_datetime_within(days):
            delta = timedelta(
                days=random.randint(0, days),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            return make_aware(now - delta)

        def get_random_user():
            return random.choice(users)

        all_articles = article_data["long"] + article_data["short"]
        random.shuffle(all_articles)

        article_objs = []
        for entry in all_articles:
            created = random_datetime_within(30)
            updated = created + timedelta(hours=random.randint(1, 48))
            user = get_random_user()
            article = Article.objects.create(
                title=entry["title"],
                content=entry["content"],
                user=user,
                created_at=created,
                updated_at=updated,
                views=random.randint(0, 100),
            )
            article_objs.append(article)

            for u in random.sample(users, k=random.randint(0, min(5, len(users)))):
                ArticleLike.objects.get_or_create(article=article, user=u)

        comment_objs = []
        for article in article_objs:
            for _ in range(random.randint(1, 3)):
                parent_created = article.created_at + timedelta(
                    hours=random.randint(1, 72)
                )
                parent_user = get_random_user()
                content = random.choice(comment_contents)
                parent_comment = Comment.objects.create(
                    article=article,
                    user=parent_user,
                    content=content,
                    created_at=parent_created,
                    updated_at=parent_created
                    + timedelta(minutes=random.randint(1, 120)),
                )
                comment_objs.append(parent_comment)

                for _ in range(random.randint(0, 3)):
                    CommentLike.objects.get_or_create(
                        comment=parent_comment, user=get_random_user()
                    )

                for _ in range(random.randint(0, 2)):
                    reply_created = parent_comment.created_at + timedelta(
                        minutes=random.randint(5, 120)
                    )
                    reply_user = get_random_user()
                    reply_content = random.choice(comment_contents)
                    reply = Comment.objects.create(
                        article=article,
                        user=reply_user,
                        content=reply_content,
                        parent_comment=parent_comment,
                        created_at=reply_created,
                        updated_at=reply_created
                        + timedelta(minutes=random.randint(1, 60)),
                    )
                    comment_objs.append(reply)

                    for _ in range(random.randint(0, 3)):
                        CommentLike.objects.get_or_create(
                            comment=reply, user=get_random_user()
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(article_objs)}개 게시글, {len(comment_objs)}개 댓글/대댓글, 좋아요 포함 생성 완료"
            )
        )
