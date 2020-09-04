import os
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from uuid import uuid4
from taggit.managers import TaggableManager
from menu.choice import BRAND_CHOICES


class MenuIngredient(models.Model):
    brand = models.CharField(max_length=64, verbose_name='브랜드')
    name = models.CharField(max_length=64, verbose_name='재료이름')
    ingredient_type = models.PositiveIntegerField(verbose_name='재료타입', default='0')
    ingredient_image = models.ImageField(upload_to="ingredient/", null=True, blank=True, verbose_name='재료이미지')

    def __str__(self):
        return '%s - %s' % (self.brand, self.name)
 
    def upload_image_delete(self, *args, **kargs):
        if self.ingredient_image:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.ingredient_image.path))
        super(Menu, self).delete(*args, **kargs)

    class Meta:
        db_table = '커스텀메뉴 재료'
        verbose_name = '커스텀메뉴 재료'
        verbose_name_plural = '커스텀메뉴 재료'


class Menu(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='작성자')
    # brand = models.CharField(choices=BRAND_CHOICES, null=True, max_length=64, verbose_name='브랜드')
    brand = models.CharField(max_length=64, verbose_name='브랜드')
    title = models.CharField(max_length=64, verbose_name='커스텀메뉴')
    base_menu = models.CharField(max_length=255, verbose_name='원본메뉴')
    # ingredient = models.CharField(max_length=255, verbose_name='재료')
    ingredient = models.ManyToManyField(MenuIngredient, related_name='ingredient', verbose_name='재료', blank=True)
    price = models.PositiveIntegerField(verbose_name='가격', default='0')
    tip = models.TextField(verbose_name='팁')
    rating = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='별점', default=0.0)
    rating_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rating_user', verbose_name='별점 등록 사용자', blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes', verbose_name='찜', blank=True)
    hits = models.PositiveIntegerField(verbose_name='조회수', default=0)
    comments = models.PositiveIntegerField(verbose_name='댓글수', default='0')
    upload_image = models.ImageField(upload_to="image_file/%Y/%m/%d", null=True, blank=True, verbose_name='이미지파일')
    # filename = models.CharField(max_length=64, null=True, verbose_name='이미지첨부파일명')
    tags = TaggableManager(blank=True, verbose_name='태그') 
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='수정일')
    deleted = models.BooleanField(default=False, verbose_name='삭제여부')

    def __str__(self):
        return '%s - %s' % (self.brand, self.title)
 
    def upload_image_delete(self, *args, **kargs):
        if self.upload_image:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.upload_image.path))
        super(Menu, self).delete(*args, **kargs)

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def created_string(self):
        time = datetime.now(tz=timezone.utc) - self.created_date

        if time < timedelta(minutes=1):
            return '방금 전'
        elif time < timedelta(hours=1):
            return str(int(time.seconds / 60)) + '분 전'
        elif time < timedelta(days=1):
            return str(int(time.seconds / 3600)) + '시간 전'
        elif time < timedelta(days=7):
            time = datetime.now(tz=timezone.utc).date() - self.created_date.date()
            return str(time.days) + '일 전'
        else:
            return False

    class Meta:
        db_table = '커스텀메뉴'
        verbose_name = '커스텀메뉴'
        verbose_name_plural = '커스텀메뉴'

    
class MenuComment(models.Model):
    post = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name='게시글')
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='댓글작성자')
    content = models.TextField(verbose_name='댓글내용')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='comment_likes', verbose_name='댓글추천', blank=True)
    reply = models.IntegerField(verbose_name='답글위치', default=0)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='댓글등록일')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='댓글수정일')
    deleted = models.BooleanField(default=False, verbose_name='댓글삭제여부')

    def __str__(self):
        return '%s - %s' % (self.post, self.content)

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def created_string(self):
        time = datetime.now(tz=timezone.utc) - self.created_date

        if time < timedelta(minutes=1):
            return '방금 전'
        elif time < timedelta(hours=1):
            return str(int(time.seconds / 60)) + '분 전'
        elif time < timedelta(days=1):
            return str(int(time.seconds / 3600)) + '시간 전'
        elif time < timedelta(days=7):
            time = datetime.now(tz=timezone.utc).date() - self.created_date.date()
            return str(time.days) + '일 전'
        else:
            return False 

    class Meta:
        db_table = '커스텀메뉴 댓글'
        verbose_name = '커스텀메뉴 댓글'
        verbose_name_plural = '커스텀메뉴 댓글'