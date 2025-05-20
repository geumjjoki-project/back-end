from django.shortcuts import render
from django.views import View
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Article, Comment
from .serializers import ArticleListSerializer, ArticleCreatePutSerializer, ArticleDetailSerializer, CommentSerializer, CommentCreatePutSerializer
from django.db.models import Q
import math
from django.core.paginator import Paginator
from rest_framework import serializers


# Create your views here.
class ArticleView(View):
    authentication_classes = [TokenAuthentication]  # 사용하는 인증 방식에 따라 다름
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    # 게시글 목록 조회 api
    def get(self, request):
        try:
            # 파라미터 추출
            try:
                page = int(request.GET.get("page", 1))
                size = int(request.GET.get("size", 10))
            except ValueError:
                return Response(
                    {
                        "status": "error",
                        "message": "페이지 번호와 크기는 정수여야 합니다.",
                        "code": "400",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            sort = request.GET.get("sort", "created_at")
            if sort not in ["created_at", "likes_count"]:
                return Response(
                    {
                        "status": "error",
                        "message": "유효하지 않은 정렬 기준입니다. 'created_at' 또는 'likes_count'만 사용 가능합니다.",
                        "code": "400",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            order = request.GET.get("order", "desc")
            if order not in ["asc", "desc"]:
                return Response(
                    {
                        "status": "error",
                        "message": "유효하지 않은 정렬 순서입니다. 'asc' 또는 'desc'만 사용 가능합니다.",
                        "code": "400",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            search = request.GET.get("search_keyword", "")

            # 게시글 조회
            articles = Article.objects.all()

            # 필터링
            if search:
                articles = articles.filter(
                    Q(title__icontains=search)
                    | Q(content__icontains=search)
                    | Q(user__nickname__icontains=search)
                ).distinct()

            # 정렬
            order_head = "-" if order == "desc" else ""
            articles = articles.order_by(f"{order_head}{sort}")

            # 페이징
            paginator = Paginator(articles, size)
            try:
                page_obj = paginator.page(page)
            except:
                return Response(
                    {
                        "status": "error",
                        "message": "유효하지 않은 페이지입니다.",
                        "code": "404",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 응답 형식 변환
            serializer = ArticleListSerializer(page_obj.object_list, many=True)

            response_data = {
                "status": "success",
                "articles": serializer.data,
                "total_pages": paginator.num_pages,
                "current_page": page,
                "total_items": paginator.count,
                "code": 200,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    "code": "500",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # 게시글 작성 api
    def post(self, request):
        try:
            title = request.data.get("title")
            content = request.data.get("content")
            if not title or not content:
                return Response(
                    {
                        "status": "error",
                        "message": "제목과 내용은 필수 입력 항목입니다.",
                        "code": "400",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = request.user
            if not user.is_authenticated:
                return Response(
                    {
                        "status": "error",
                        "message": "로그인이 필요합니다.",
                        "code": "401",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            article = Article.objects.create(title=title, content=content, user=user)

            serializer = ArticleCreatePutSerializer(article)

            response_data = {
                "status": "success",
                "article": serializer.data,
                "code": 201,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    "code": "500",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ArticleDetailView(View):
    authentication_classes = [TokenAuthentication]  # 사용하는 인증 방식에 따라 다름
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    # 게시글 상세 조회 api
    def get(self, request, article_id):
        try:
            # 게시글 조회
            try:
                article = Article.objects.get(pk=article_id)
            except Article.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "존재하지 않는 게시글입니다.",
                        "code": "404",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 조회수 증가
            article.views += 1
            article.save()

            # 게시글 정보 시리얼라이즈
            article_serializer = ArticleDetailSerializer(article, context={'request': request})
            
            response_data = {
                "status": "success",
                "article": article_serializer.data,
                "code": 200,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    "code": "500",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
    # 게시글 수정 api
    def put(self, request, article_id):
        try:
            title = request.data.get("title")
            content = request.data.get("content")
            if not title or not content:
                return Response(
                    {
                        "status": "error",
                        "message": "제목과 내용은 필수 입력 항목입니다.",
                        "code": "400",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            try:
                article = Article.objects.get(pk=article_id)
            except Article.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "존재하지 않는 게시글입니다.",
                        "code": "404",  
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            article.title = title
            article.content = content
            article.save()
            
            serializer = ArticleCreatePutSerializer(article)
            
            response_data = {
                "status": "success",
                "article": serializer.data,
                "code": 200,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    "code": "500",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # 게시글 삭제 api
    def delete(self, request, article_id):
        try:
            article = Article.objects.get(pk=article_id)
            article.delete()
            response_data = {
                "status": "success",
                "message": "게시글이 삭제되었습니다.",
                "code": 200,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Article.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "존재하지 않는 게시글입니다.",
                    "code": "404",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",  
                    "code": "500",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CommentView(View):
    authentication_classes = [TokenAuthentication]  # 사용하는 인증 방식에 따라 다름
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    # 댓글 목록 조회 api
    def get(self, request, article_id):
        try:
            try:
                article = Article.objects.get(pk=article_id)
            except Article.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "존재하지 않는 게시글입니다.",
                        "code": "404",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 댓글 조회 및 시리얼라이즈
            comments = article.comments.filter(parent_comment=None)  # 대댓글이 아닌 댓글만 조회
            comment_serializer = CommentSerializer(comments, many=True, context={'request': request})

            response_data = {
                "status": "success",
                "comments": comment_serializer.data,
                "comment_count": len(comment_serializer.data),
                "code": 200,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    "code": "500",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # 댓글 작성 api
    def post(self, request, article_id):
        try:
            try:
                article = Article.objects.get(pk=article_id)
            except Article.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "존재하지 않는 게시글입니다.",
                        "code": "404",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            content = request.data.get('content')
            parent_comment_id = request.data.get('parent_comment_id')

            if not content:
                return Response(
                    {
                        "status": "error",
                        "message": "댓글 내용은 필수 입력 항목입니다.",
                        "code": "400",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 대댓글인 경우
            if parent_comment_id:
                try:
                    parent_comment = Comment.objects.get(pk=parent_comment_id)
                    comment = Comment.objects.create(
                        article=article,
                        user=request.user,
                        content=content,
                        parent_comment=parent_comment
                    )
                except Comment.DoesNotExist:
                    return Response(
                        {
                            "status": "error",
                            "message": "존재하지 않는 댓글입니다.",
                            "code": "404",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
            # 일반 댓글인 경우
            else:
                comment = Comment.objects.create(
                    article=article,
                    user=request.user,
                    content=content
                )

            serializer = CommentCreatePutSerializer(comment, context={'request': request})
            
            response_data = {
                "status": "success",
                "comment": serializer.data,
                "code": 201,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    "code": "500",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    # 댓글 수정 api
    def put(self, request, article_id, comment_id):
        try:
            content = request.data.get('content')
            if not content:
                return Response(
                    {
                        "status": "error",
                        "message": "댓글 내용은 필수 입력 항목입니다.",
                        "code": "400",
                    }
                )
            
            try:
                comment = Comment.objects.get(pk=comment_id)
            except Comment.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "존재하지 않는 댓글입니다.",
                        "code": "404",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
                
            user = request.user
            if comment.user != user:
                return Response(
                    {
                        "status": "error",
                        "message": "댓글 수정 권한이 없습니다.",
                        "code": "403",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            
            comment.content = content
            comment.save()
            serializer = CommentCreatePutSerializer(comment, context={'request': request})
            response_data = {
                "status": "success",
                "comment": serializer.data,
                "code": 200,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    "code": "500",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
    # 댓글 삭제 api
    def delete(self, request, article_id, comment_id):
        try:
            try:
                comment = Comment.objects.get(pk=comment_id)
            except Comment.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "존재하지 않는 댓글입니다.",
                        "code": "404",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            user = request.user
            if comment.user != user:
                return Response(
                    {
                        "status": "error",
                        "message": "댓글 삭제 권한이 없습니다.",
                        "code": "403",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            comment.delete()
            response_data = {
                "status": "success",
                "message": "댓글이 삭제되었습니다.",
                "code": 200,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    "code": "500",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )