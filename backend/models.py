import datetime
from io import BytesIO
import json
import os
from pydoc import synopsis
from django.db.models import signals
from django.contrib.auth.models import Group, Permission

from django.db import models
from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
# Create your models here.
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .usermanager import UserManager
from django.utils.timezone import now
from django.utils.html import mark_safe
from django.contrib.humanize.templatetags import humanize
from django.db.models.signals import post_save,pre_save
from django.core import files

from django.urls import reverse
from taggit.managers import TaggableManager
from django.utils import timezone
import re
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django import forms

from import_export.admin import ImportExportMixin
from import_export import resources,fields,widgets
from import_export.widgets import ForeignKeyWidget
from django.utils.text import slugify
import random
import requests
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
# from tinymce.widgets import TinyMCE
# from tinymce import models as tinymce_models


from ckeditor.fields import RichTextField


# from tinymce.models import HTMLField

# Create your views here.
from image_optimizer.fields import OptimizedImageField
from django.core.serializers import serialize

import os.path
from django_resized import ResizedImageField
from PIL import Image as PilImage

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 


# create a form field which can input a file
class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
    

class User(AbstractBaseUser, PermissionsMixin):
    groups = models.ManyToManyField(Group, related_name='group')  # Use a unique related name
    user_permissions = models.ManyToManyField(Permission, related_name='permission')  # Unique related name
    is_staff = models.BooleanField(default=True)
    
    username = models.CharField(max_length=150, unique=True, null=True)
    email = models.EmailField(unique=True,max_length=255,blank=False,)
    is_active = models.BooleanField(default=True,help_text=('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'),)
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Joined at")


    SUPERADMIN = 'SUPERADMIN'
    ADMIN = 'ADMIN'
    BLOGGER = 'BLOGGER'
    LEADMANAGER = 'LEADMANAGER'
    MERCHANT = 'MERCHANT'
    MERCHANT_BLOGGER = 'MERCHANT_BLOGGER'
    USER = 'USER'
  
    ROLE_CHOICES = (
        (SUPERADMIN, 'SUPERADMIN'),
        (ADMIN, 'ADMIN'),
        (BLOGGER, 'BLOGGER'),
        (MERCHANT, 'MERCHANT'),
        (MERCHANT_BLOGGER, 'MERCHANT_BLOGGER'),
        (LEADMANAGER, 'LEADMANAGER'),
        (USER, 'USER'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES,default=BLOGGER)
    # role = models.IntegerField(default=5)
    # Add additional fields here if needed
   
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email',]

@receiver(post_save, sender=User)   
def user_post_save_handler(sender, instance, **kwargs):
    # post_save.disconnect(user_post_save_handler, sender=sender)
    try:
        if(instance.role=="LEADMANAGER"):
            leadmanager_group = Group.objects.get(name='leadmanager') 
            if(leadmanager_group):
                instance.groups.add(leadmanager_group)

        if(instance.role=="BLOGGER"):
            print("in here")
            bloggers_group = Group.objects.get(name='blogger') 
            if(bloggers_group):
                print("in here 2")
                instance.groups.add(bloggers_group)
        if(instance.role=="MERCHANT"):
            merchants_group = Group.objects.get(name='merchant') 
            if(merchants_group):
                instance.groups.add(merchants_group)
        if(instance.role=="MERCHANT_BLOGGER"):
            merchants_group = Group.objects.get(name='merchant') 
            bloggers_group = Group.objects.get(name='blogger') 
            if(merchants_group):
                instance.groups.add(merchants_group)
            if(bloggers_group):
                instance.groups.add(bloggers_group)
        if(instance.role=="ADMIN"):
            admin_group = Group.objects.get(name='admin') 
            instance.groups.add(admin_group)

    except Group.DoesNotExist:
                print("ddddd")
                pass
    

# Create your models here.
class BlogCategory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    name = models.CharField(max_length=80, verbose_name="name",default='')
    description=models.TextField(max_length=200,verbose_name="description",null=True,blank=True)
    icon=models.ImageField(upload_to='categoryicons/%Y/%m/%d/',verbose_name="icon",null=True,blank=True) 
    slug = models.SlugField(max_length=255,unique=True,default='')

    def slug_name(self):
        return self.slugs
    
    def cat_img(self):
        if(self.icon):
            return mark_safe('<img src="%s" width="50px" height="50px" />'%(self.icon.url))
        else:
            return ""
    cat_img.short_description = 'Icon'

    class Meta:
        verbose_name = "Blog - Category"
        verbose_name_plural = "Blog - Categories"
        ordering = ('-id',)
    def __str__(self):
        return '%s' % (self.name)   
    def __unicode__(self):
        return '%s' % (self.name)  
    


class Page(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    name = models.CharField(max_length=80, verbose_name="name",default='')
    slug = models.SlugField(max_length=255,unique=True,default='')
    post=RichTextField(help_text="You can add shortcodes in the post e.g[[youtube #videoid# #caption#]], ")

    def slug_name(self):
        return self.slugs
    

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ('-id',)
    def __str__(self):
        return '%s' % (self.name)   
    def __unicode__(self):
        return '%s' % (self.name)  



class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,self).get_queryset().filter(status='published')


    
class BlogPost(models.Model):
    STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('unpublished', 'UnPublished'),
    )

    TYPE_CHOICES = (
    ('article', 'Article'),
    ('howto', 'HowTo'),
    ('codeblog', 'CodeBlog'),
    )
    
    title=models.CharField('Title', max_length=200)
    
    slug = models.SlugField(max_length=255,unique=True,default='')
    

    # post=FroalaField()
    summary=models.TextField(max_length=500,default='',help_text="Please add a summary upto 500 characters")

    # post=TinyMCEModelField()
    post=RichTextField(help_text="You can add shortcodes in the post e.g[[youtube #videoid# #caption#]], ")

    
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='blog_posts',default=1)
    
    created = models.DateTimeField(auto_now_add=True)
    # updated = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=15,choices=TYPE_CHOICES,default='article',blank=True)
    claps = models.IntegerField(default=1)
    views = models.IntegerField(default=1)
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='category',default=1)
    
    
    tags = TaggableManager(blank=True,)
    

    status = models.CharField(max_length=15,choices=STATUS_CHOICES,default='published')
    read_time = models.IntegerField(default=0)
    image = models.ImageField(upload_to='featured_image/%Y/%m/',blank=True)
    image768_url = models.CharField(null=True,max_length=200,blank=True)
    image480_url = models.CharField(null=True,max_length=200,blank=True)
    image320_url = models.CharField(null=True,max_length=200,blank=True)
    image240_url = models.CharField(null=True,max_length=200,blank=True)
    image120_url = models.CharField(null=True,max_length=200,blank=True)

    # image = models.ImageField(upload_to='featured_image/%Y/%m/%d/',null=True,blank=True) 

    # image = OptimizedImageField(
    #     upload_to="featured_image/%Y/%m/%d",
    #     optimized_image_output_size=(600, 450),
    #     optimized_image_resize_method="contain"  #  "crop", "cover", "contain", "width", "height", "thumbnail" or None
    # )

    #image_main = ResizedImageField(size=[640, 640],force_format="WEBP", quality=75, upload_to="featured_image/")
    
    

        
    class Meta:
        
        verbose_name = "Blog - Post"
        verbose_name_plural = "Blog - Posts"
        # ordering = ('-created_at',)
        
    
    def __str__(self):
        return self.title
    

    # @property
    # def id(self):
    #     return self.pk

    @property
    def synopsis(self):
        return _filter_visible_text(self.post)[:150]
  
    @property
    def post_html(self):
        return html.unescape(self.post)

    @property
    def tags_list(self):
        return self.tags.values_list('name', flat=True)
        # return self.tags.all()
    @property
    def created_ago(self):
        return humanize.naturaltime(self.created)  

    # objects = models.Manager() # The default manager.
    # published = PublishedManager()




    def get_absolute_url(self):
        return reverse('blog:post_detail',args=[self.slug])

    def incrementViewCount(self):
        self.views =self.views+1
        self.save()

    def __unicode__(self):
        return '%s %s' % (self.title, self.body) 

@receiver(post_save, sender=BlogPost)
def blogpost_post_save(sender, instance, *args, **kwargs):
    ##this part only execute on first create
    updates = {}
    if kwargs.get('created', False) and instance.claps <= 1:
        rand_claps = random.randrange(20, 99)
        updates["claps"] = rand_claps
        rand_views = random.randrange(rand_claps, rand_claps*2)
        updates["views"] = rand_views
     ##this part executes on create and update
     # Convert the post to a JSON representation
    

    if(instance.image):
        path_768=save_resized_image(instance,768)
        path_480=save_resized_image(instance,480)
        path_320=save_resized_image(instance,320)
        path_240=save_resized_image(instance,240)
        path_120=save_resized_image(instance,120)

        updates["image768_url"] = path_768
        updates["image480_url"] = path_480
        updates["image320_url"] = path_320
        updates["image240_url"] = path_240
        updates["image120_url"] = path_120

    

        post_data = {
            "id": instance.pk,
            "title": instance.title,
            "post": instance.post,
            "image": instance.image.url if instance.image else None,
            "image768_url":updates["image768_url"],
            "image480_url":updates["image480_url"],
            "image320_url":updates["image320_url"],
            "image240_url":updates["image240_url"],
            "image120_url":updates["image120_url"],
            
        }
    else:
        post_data = {
            "id": instance.pk,
            "title": instance.title,
            "post": instance.post,
            "image": instance.image.url if instance.image else None,
            
            
        }

    

    # post_data = serialize('json', [instance])
    
    # Write to a JSON file
    # with open(f'json/{instance.slug}.json', 'w') as json_file:
    # with open(f'{root_path}/json/{instance.slug}.json', 'w') as json_file:
    #    json_file.write(json.dumps(post_data))

    BlogPost.objects.filter(pk=instance.pk).update(**updates)

def save_resized_image(instance, width):

    print("*********** PATH",instance.image.path)
    # Open the original image using Pillow
    with PilImage.open(instance.image.path) as img:
        # Calculate height maintaining the aspect ratio
        aspect_ratio = img.height / img.width
        new_height = int(aspect_ratio * width)
        
        # Resize the image
        img = img.resize((width, new_height), PilImage.ADAPTIVE)
        
        base_name, _ = os.path.splitext(os.path.basename(instance.image.name))
        new_filename = f'w{width}_' + base_name + ".webp"
        new_path = os.path.join(os.path.dirname(instance.image.path), new_filename)
        dir_name = os.path.dirname(instance.image.name)
        new_relative_path = os.path.join(dir_name, new_filename)
        # Save the image in WEBP format
        img.convert("RGB").save(new_path, "WEBP")
        
        print("NEW RELATIVE PATH ------------------",dir_name," ------- ",new_relative_path)
        return new_relative_path


   

class ProductCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)
    slug=  models.SlugField(max_length=255,unique=True,default='')
    description	=  models.TextField(max_length=300,verbose_name="description",null=True,blank=True)
    class Meta:
        verbose_name = "Product - Category"
        verbose_name_plural = "Product - Categories"
        ordering = ['name']
    
    def __str__(self):
        return '%s' % (self.name)   
    def __unicode__(self):
        return '%s' % (self.name) 
    


class Products(models.Model):
    TYPES_CHOICES = (
    ('affiliate', 'Affiliate'),
    ('checkout', 'Checkout'),
    ('lead', 'Lead'),
    )
    type = models.CharField(max_length=15,choices=TYPES_CHOICES,default='lead')
    name               =  models.CharField(max_length=200)
    slug               =  models.SlugField(max_length=255,unique=False,default='')
    category = models.ForeignKey(ProductCategory, related_name='products', on_delete=models.CASCADE)
       
    image_cover        = models.ImageField(upload_to='products/cover/%Y/%m/%d/',null=True,blank=True)
    image1             =  models.ImageField(upload_to='products/%Y/%m/%d/',null=True,blank=True)
    image2             =  models.ImageField(upload_to='products/%Y/%m/%d/',null=True,blank=True)
    image3             =  models.ImageField(upload_to='products/%Y/%m/%d/',null=True,blank=True)
    image4             =  models.ImageField(upload_to='products/%Y/%m/%d/',null=True,blank=True)
    image5             =  models.ImageField(upload_to='products/%Y/%m/%d/',null=True,blank=True)
    image6             =  models.ImageField(upload_to='products/%Y/%m/%d/',null=True,blank=True)    
    seo_desc           =  models.TextField(max_length=250,verbose_name="seo meta description",null=True,blank=True)
    short_desc         =  RichTextField(max_length=500,verbose_name="Short desc",null=True,blank=True)
    long_desc          =  RichTextField(max_length=6000,verbose_name="Long desc",null=True,blank=True)
    
    ratings            = models.PositiveIntegerField(default=random.randint(100, 350))
    price              = models.PositiveIntegerField(default=0)
    discount           = models.PositiveIntegerField(default=0, null=True, blank=True)

    
    def get_discountedprice(self):
        if(self.discount > 0 ):
            return self.price +(self.price * (self.discount/100))
        else:
            return self.price
    
    def __str__(self):
        return f"{self.name}"

    class Meta:
       
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['name']

    
@receiver(pre_save, sender=Products)
def product_pre_save(sender, instance, *args, **kwargs):
    rand_num = random.randrange(99, 99999)
    # instance.slug=slugify(instance.prdname+"_"+str(rand_num))
    if(is_string_an_url(instance.image_cover)):
        save_image_from_url(instance.image_cover,instance)
    if(is_string_an_url(instance.image1)):
        save_image_from_url(instance.image1,instance)
    if(is_string_an_url(instance.image2)):
        save_image_from_url(instance.image2,instance)
    if(is_string_an_url(instance.image3)):
        save_image_from_url(instance.image3,instance)
    if(is_string_an_url(instance.image4)):
        save_image_from_url(instance.image4,instance)
    if(is_string_an_url(instance.image5)):
        save_image_from_url(instance.image4,instance)
    if(is_string_an_url(instance.image6)):
        save_image_from_url(instance.image6,instance)


# class Products(models.Model):
#     TYPES_CHOICES = (
#     ('affiliate', 'Affiliate'),
#     ('checkout', 'Checkout'),
#     ('lead', 'Lead'),
#     )
#     type = models.CharField(max_length=15,choices=TYPES_CHOICES,default='lead')
#     # id                 =  models.AutoField(primary_key=True)
#     # id = models.AutoField(primary_key=True,auto_created=True)
#     name               =  models.CharField(max_length=200)
#     promo_label        =  models.CharField(max_length=200,null=True,blank=True)
#     slug               =  models.SlugField(max_length=255,unique=False,default='')
#     seo_title          =  models.CharField(max_length=100,null=True,blank=True)
#     cat                =  models.ForeignKey("ProductCategory",to_field='id',on_delete=models.CASCADE,related_name='category_1',default=ProductCategory._check_default_pk)
#     subcat             =  models.ForeignKey("ProductCategory",to_field='id',on_delete=models.CASCADE,related_name='category_2',default=ProductCategory._check_default_pk)
    
    
 
 




def is_string_an_url(url_string: str):
    return True
    # validate_url = URLValidator(verify_exists=True)

    # try:
    #     validate_url(url_string)
    # except:
    #     return False

    # return True


def save_image_from_url(url,sender):
        """
        Save remote images from url to image field.
        Requires python-requests
        """
        try:
            url=str(url)
            resp = requests.get(url)
            if resp.status_code != requests.codes.ok:
                return False

            fp = BytesIO()
            fp.write(resp.content)
            file_name = url.split("/")[-1]  # There's probably a better way of doing this but this is just a quick example
            # file_name=slugify(sender.name)
            sender.image_primary.save(file_name, files.File(fp))

        except BaseException as err:
            print ("Failed downloading image from ", url)
            return False

class MainBanner(models.Model):
    STATUS_CHOICES = (
    ('published', 'published'),
    ('draft', 'draft'),
   
    )
    type = models.CharField(max_length=15,choices=STATUS_CHOICES,default='draft')
    created_at          = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at          = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    name          =  models.CharField(max_length=50,null=True,blank=True,verbose_name="Banner Name")
    image_cover        = models.ImageField(upload_to='banners/%Y/%m/%d/',null=True,blank=True,verbose_name="1740x820 banner")
    subject_title          =  models.CharField(max_length=50,null=True,blank=True)
    main_title          =  models.CharField(max_length=100,null=True,blank=True)
    cta_text          =  models.CharField(max_length=50)
    cta_link          =  models.CharField(max_length=200)

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ['name']


class SEOContent(models.Model):
    created_at          = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at          = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    block_name          =  models.CharField(max_length=150)	
    page_name           = models.CharField(max_length=150,null= False, default="home")	
    slug                =  models.SlugField(max_length=255,unique=False,default='')
    content1    	    =  RichTextField(max_length=4000,verbose_name="content",null=True,blank=True)
    content2    	    =  RichTextField(max_length=4000,verbose_name="content",null=True,blank=True)
    content3    	    =  RichTextField(max_length=4000,verbose_name="content",null=True,blank=True)
    content4    	    =  RichTextField(max_length=4000,verbose_name="content",null=True,blank=True)

    


class Lead(models.Model):

    STATUS_CHOICES = (
    ('open', 'Open'),
    ('hot', 'Hot'),
    ('rejected', 'Rejected'),
    ('inprocess', 'Inprocess'),
    ('closed', 'Closed'),
    )

    RESELLER_CHOICES = (
    ('Y', 'Y'),
    ('N', 'N'),
    
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    city_ip =  models.CharField(max_length=50,null=True,blank=True)
    country_ip =  models.CharField(max_length=50,null=True,blank=True)
    country_domain =  models.CharField(max_length=10,null=True,blank=True)
    country_shipping =  models.CharField(max_length=50,null=False,blank=False)
    email = models.EmailField(null = False, blank=False)
    
    resellerpricing = models.CharField(max_length=15,choices=RESELLER_CHOICES,default='N')
    description =  models.TextField(max_length=600,null=True,blank=True)
    status = models.CharField(max_length=15,choices=STATUS_CHOICES,default='open')
    deal_notes =  models.TextField(max_length=800,null=True,blank=True)
    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "leads"
        ordering = ['created_at']