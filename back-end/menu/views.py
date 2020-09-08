from django.shortcuts import render
from rest_framework.views import APIView, View
from rest_framework.response import Response
from .models import Menu, BaseMenu, MenuIngredient
from .serializers import MenuSerializer, MenuPostSerializer, MenuDetailSerializer, TagListSerializer, BaseMenuWriteSerializer, IngredientWriteSerializer
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny # 로그인 여부
from rest_framework_jwt.authentication import JSONWebTokenAuthentication # JWT인증
from django.http import Http404
from rest_framework import viewsets
from rest_framework import permissions
from taggit.models import Tag
from django.db.models import Count
from accounts.models import CustomUser as User
import json
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, JSONParser


class MenuListView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    # def post(self, request, format=None):
    #     serializer = MenuPostSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(writer=self.request.user)
    #         return Response({'data':serializer.data, 'message':'성공적으로 등록되었습니다.'}, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        brand = self.request.query_params.get('brand', None)
        sort = self.request.query_params.get('sort', None)
        query_sort='-created_date'

        if sort:
            if sort=='latest':
                query_sort = '-created_date'
            elif sort=='rank':
                query_sort = '-rating'
            elif sort=='hit':
                query_sort = '-hits'

        if brand:
            if brand=='all':
                queryset = Menu.objects.exclude(deleted=True).order_by(query_sort)
            elif brand=='subway':
                queryset = Menu.objects.filter(brand='서브웨이').exclude(deleted=True).order_by(query_sort)
        else:
            queryset = Menu.objects.exclude(deleted=True).order_by('-created_date')

        if queryset:
            serializer = MenuSerializer(queryset, many=True)
            return Response({'data':serializer.data})
        else:
            return Response({'data':None, 'message':'등록된 메뉴가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)


class MenuWriteView(APIView):
    # parser_classes = (MultiPartParser, JSONParser,)

    def get(self, request, format=None):
        brand = self.request.query_params.get('brand', None)
        if brand is not None:
            if brand =='subway':
                base_menu_queryset = BaseMenu.objects.filter(brand='서브웨이')
                ingredient_queryset = MenuIngredient.objects.filter(brand='서브웨이')

        if base_menu_queryset is not None and ingredient_queryset is not None:
            base_menu_serializer = BaseMenuWriteSerializer(base_menu_queryset, many=True)
            ingredient_serializer = IngredientWriteSerializer(ingredient_queryset, many=True)

            context = {
                'base_menu':base_menu_serializer.data,
                'ingredient':ingredient_serializer.data
            }
            return Response({'data':context})

    def post(self, request, format=None):
        serializer = MenuPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(writer=self.request.user)
            return Response({'data':serializer.data, 'message':'성공적으로 등록되었습니다.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuSearchView(APIView):
    def get(self, request, format=None):
        keyword = self.request.query_params.get('keyword', None)
        if len(keyword) > 1 :
            queryset = Menu.objects.filter(
                Q (brand__icontains=keyword) |
                Q (title__icontains=keyword)
                # Q (base_menu__icontains=keyword)
            ).exclude(deleted=True).order_by('-created_date')

            if queryset:
                serializer = MenuSerializer(queryset, many=True)
                return Response({'data':serializer.data, 'message':str(queryset.count())+'개의 메뉴가 검색되었습니다.'})
            else:
                return Response({'data':None, 'message':'검색결과가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'data':None, 'message':'검색어는 2글자 이상 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)


class MenuDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        try:
            return Menu.objects.get(pk=pk)
        except Menu.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        Menu = self.get_object(pk)
        Menu.hits += 1
        Menu.save()
        serializer = MenuDetailSerializer(Menu)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        writer = self.request.user
        try:
            menu = Menu.objects.get(pk=pk, writer=writer)
        except Menu.DoesNotExist:
            return Response({'data':None, 'message':'본인 게시글이 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = MenuPostSerializer(menu, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data':serializer.data, 'message':'성공적으로 수정되었습니다.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        writer = self.request.user
        try:
            menu = Menu.objects.get(pk=pk, writer=writer)
        except Menu.DoesNotExist:
            return Response({'data':None, 'message':'본인 게시글이 아닙니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        menu.deleted = True
        menu.save()
        # Menu.delete()
        return Response({'data':None, 'message':'성공적으로 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)


class TagListView(APIView):
    def get(self, request, format=None):
        queryset = Tag.objects.all()
        queryset_count = queryset.annotate(tag_count=Count('taggit_taggeditem_items')).order_by('-tag_count')[:30]
        # tag_dict = {}
        # for tag in queryset_count:
        #     tag_dict[tag.name] = tag.tag_count
        # print(tag_dict)
        serializer = TagListSerializer(queryset_count, many=True)
        return Response({'data':serializer.data})

    def post(self, request, format=None):
        # tags = self.request.query_params.get('tag', None)
        tags = self.request.GET.getlist('tag', None)
        tagParams = []
        if tags is not None:
            for tag in tags:
                tagParams.append(int(tag))

        user_email = self.request.user
        user = User.objects.get(email=user_email)
        # user.preference_keyword = json.loads(request.body)['preference_keyword']
        user.preference_keyword = tagParams
        user.save()
        return Response({'data':user.preference_keyword,'message':'성공적으로 등록되었습니다.'})


class MenuLikeView(APIView):
    def post(self, request, pk, format=None):
        user = self.request.user
        try:
            menu = Menu.objects.get(pk=pk, writer=user)
        except Menu.DoesNotExist:
            menu = Menu.objects.get(pk=pk)
            if menu.likes.filter(id=user.id):
                menu.likes.remove(user.id)
                return Response({'data':None, 'message':'해당 메뉴 찜을 취소했습니다.'}, status=status.HTTP_200_OK)
            else:
                menu.likes.add(user.id)
                return Response({'data':None, 'message':'해당 메뉴를 찜했습니다.'}, status=status.HTTP_200_OK)

        return Response({'data':None, 'message':'본인 메뉴는 찜할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)


class MenuRatingView(APIView):
    def post(self, request, pk, format=None):
        user = self.request.user
        try:
            menu = Menu.objects.get(pk=pk, writer=user)
        except Menu.DoesNotExist:
            menu = Menu.objects.get(pk=pk)
            if menu.rating_user.filter(id=user.id):
                return Response({'data':None, 'message':'이미 별점을 등록하셨습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            else:  
                tmp_rating = menu.rating * menu.rating_user.count()
                menu.rating_user.add(user.id)
                rating = json.loads(request.body)['rating']
                menu.rating = (tmp_rating + rating) / menu.rating_user.count()
                menu.save()
                return Response({'data':None, 'message':'해당 메뉴에 별점을 등록했습니다.'}, status=status.HTTP_200_OK)

        return Response({'data':None, 'message':'본인 메뉴에는 별점을 등록할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)


class LikeMenuView(APIView):
    def get(self, request, format=None):
        queryset = Menu.objects.filter(likes=request.user.id).exclude(deleted=True)
        if queryset:
            serializer = MenuSerializer(queryset, many=True)
            return Response({'data':serializer.data})
        else:
            return Response({'data':None, 'message':'찜한 메뉴가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)


class WriteMenuView(APIView):
    def get(self, request, format=None):
        queryset = Menu.objects.filter(writer=request.user.id).exclude(deleted=True)
        if queryset:
            serializer = MenuSerializer(queryset, many=True)
            return Response({'data':serializer.data})
        else:
            return Response({'data':None, 'message':'작성한 메뉴가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)