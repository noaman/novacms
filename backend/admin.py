from unicodedata import category
from django.contrib import admin
from requests import request

from .models import *

# Register your models here.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import *
from import_export import resources
from django.utils.crypto import get_random_string
from html import unescape
from django.utils.html import strip_tags

class ProductsResource(resources.ModelResource):

    class Meta:
        model = Products
        import_id_fields = ('name',)
        exclude = ('created_at','updated_at','slug','id')
        
    def before_save_instance(self, instance, using_transactions, dry_run):
        
        instance.slug = slugify(instance.name)  # Or generate a unique slug in your own way



class BlogPostResource(resources.ModelResource):
    author_post_id =1
    tags_arr=[]
    class Meta:
        model = BlogPost
        import_id_fields = ('title',)
        exclude = ('created','updated','slug','id','author','claps','views','status','read_time','tags','image','image768_url', 'image480_url', 'image320_url', 'image240_url', 'image120_url')
    
    def before_import_row(self, row, **kwargs):
        self.author_post_id = kwargs['user'].id
        self.tags_arr=row['keywords'].split(',')
        print(self.tags_arr)

    # def after_import_row(self, row, row_result, **kwargs):
    #     instance = self._meta.model.objects.get(pk=row_result.object_id)
    #     print(row["tags"])
    #     instance.tags.set(*row['tags'].split(','))
        
        

    def before_save_instance(self, instance, using_transactions, dry_run):
        print("user hewre",self.author_post_id)

        instance.author =User.objects.get(id=self.author_post_id)
        
        instance.slug = slugify(instance.title)  # Or generate a unique slug in your own way
        rand_claps = random.randrange(20, 99)
        instance.claps=rand_claps
        rand_views = random.randrange(rand_claps, rand_claps*2)
        instance.views=rand_views
        instance.status='published'
        instance.read_time = get_read_time(instance.post)

    def after_save_instance(self, instance, using_transactions, dry_run):
        print("in after save")
        print(get_read_time(instance.post))
        instance.tags.set(["tag","mag","bg"])
        
        return super().after_save_instance(instance, using_transactions, dry_run)

class ProductCategoryResource(resources.ModelResource):
    
    class Meta:
        model = ProductCategory
        import_id_fields = ('name',)
        exclude = ('created_at','updated_at','id','slug')
    
    def before_save_instance(self, instance, using_transactions, dry_run):
        instance.slug = slugify(instance.name)  # Or generate a unique slug in your own way

class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    ordering = ["email",]

    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    group.short_description = 'Groups'

    list_display = ('username', 'role', 'is_superuser', 'group')
    list_filter = ('is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'role', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Group Permissions', {'fields': ('groups',)}),  # Only groups here
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'email', 'role', 'password1', 'password2')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        # ('Group Permissions', {'fields': ('groups',)}),  # Only groups here
    )

admin.site.register(User, CustomUserAdmin)


  

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
#    list_display = (['cat_img','id','name'])
#f.name for f in BlogCategory._meta.fields
   list_display  = ['id','name','slug']
   prepopulated_fields = {'slug':('name',)}


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
#    list_display = (['cat_img','id','name'])
#f.name for f in BlogCategory._meta.fields
   list_display  = ['id','name','slug']
   prepopulated_fields = {'slug':('name',)}


def get_read_time(html_text):
    string = unescape(strip_tags(html_text))
    total_words = len((string).split())
    return round(total_words / 200)



# @admin.register(BlogPost)
# class BlogAdmin(admin.ModelAdmin):
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.is_superuser or request.user.role=="ADMIN":
#             return qs
#         return qs.filter(author=request.user)

#     def save_model( self, request, obj, form, change ):
#         #pre save stuff here
#         if(not request.user.is_superuser):
#             try:
#                 author_original=obj.user
#                 obj.author =request.user=author_original
#             except:
#                 obj.author =request.user

#         obj.read_time=get_read_time(obj.post)

#         obj.save()
#         #post save stuff here

#     def get_form(self, request, obj=None, **kwargs):
#         self.exclude = []

#         if not request.user.is_superuser:
#                 fieldsets = ((None, {'fields': ('category','title','slug','image','status', 'summary','post','author','views','claps')}),)
#         else:
#                 fieldsets = ((None, {'fields': ('category','title','slug','image','status', 'summary','post','views','claps')}),)
    

#         if not request.user.is_superuser:
#             self.exclude.append('author') #here!
#         return super(BlogAdmin, self).get_form(request, obj, **kwargs)

        
#     summernote_fields = ('post',)
#     list_display = (['title','category','author','read_time','views'])
#     prepopulated_fields = {'slug':('title',)}

@admin.register(BlogPost)
class BlogAdmin(ImportExportMixin,admin.ModelAdmin):  # Inherit from SummernoteModelAdmin for summernote_fields
    resource_class = BlogPostResource
    summernote_fields = ('post',)
    list_display = (['title', 'category', 'author','keywords', 'read_time', 'views'])
    prepopulated_fields = {'slug':('title',)}
    

    def keywords(self, post):
        tags = []
        for tag in post.tags.all():
            tags.append(str(tag))
        return ', '.join(tags)
    

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role=="ADMIN":
            return qs
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        # pre save stuff here
        if not request.user.is_superuser:
            try:
                author_original = obj.user
                obj.author = request.user = author_original
            except:
                obj.author = request.user

        obj.read_time = get_read_time(obj.post)

        obj.save()
        # post save stuff here



    def get_form(self, request, obj=None, **kwargs):
        self.exclude = []

        self.fieldsets = (
                (None, {'fields': ('author','category', 'title', 'slug',  'summary', 'post','image','image768_url','image480_url','image320_url','image240_url','image120_url', 'status', 'views','read_time', 'claps','tags')}),
            )
        
        # if not request.user.is_superuser:
        #     self.fieldsets = (
        #         (None, {'fields': ('category', 'title', 'slug', 'image', 'status', 'summary', 'post', 'author', 'views', 'claps')}),
        #     )
        # else:
        #     self.fieldsets = (
        #         (None, {'fields': ('category', 'title', 'slug', 'image', 'status', 'summary', 'post', 'views', 'claps')}),
        #     )

        if not request.user.is_superuser:
            self.exclude.append('author')  # here!
        return super().get_form(request, obj, **kwargs)


@admin.register(MainBanner)
class MainBannerAdmin(admin.ModelAdmin):
    list_display=("name",)


@admin.register(SEOContent)
class SEOContentAdmin(admin.ModelAdmin):
    list_display = ("page_name","block_name")
    prepopulated_fields = {"slug": ("block_name",)}  # new



@admin.register(ProductCategory)
class ProductCategoryAdmin(ImportExportMixin,admin.ModelAdmin):
    resource_class = ProductCategoryResource
    def save_model( self, request, obj, form, change ):
        obj.author =request.user
        obj.save()
        
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = []
        return super(ProductCategoryAdmin, self).get_form(request, obj, **kwargs)

    list_display = (['id','name','slug'])
    prepopulated_fields = {'slug':('name',)}



@admin.register(Lead)
class LeadsAdmin(admin.ModelAdmin):
    list_display = (['created_at','country_shipping','country_ip','country_domain','email','status'])
    search_fields = ('country_ip','status','country_shipping',)
    list_filter = ('created_at','status')
    




@admin.register(Products)
class ProductsAdmin(ImportExportMixin,admin.ModelAdmin):
    resource_class = ProductsResource
    # list_display = (['name','type','cat','subcat'])
    list_display = (['name','slug','type'])
    search_fields = ('name',)
    list_filter = ('type',)
    prepopulated_fields = {'slug':('name',)} 
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role=="ADMIN":
            return qs
        return qs.filter(merchant=request.user)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = []
        # if not request.user.is_superuser:
        self.exclude.append('author')
        self.exclude.append('merchant')
        return super(ProductsAdmin, self).get_form(request, obj, **kwargs)

    def save_model( self, request, obj, form, change ):
        #pre save stuff here
        obj.merchant =request.user
        obj.author =request.user
        # if(not request.user.is_superuser):
        #     try:
        #         merchant_original=obj.user
        #         obj.merchant =request.user=merchant_original
        #     except:
        #         obj.merchant =request.user

        obj.save()

    