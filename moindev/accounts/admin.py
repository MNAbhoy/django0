from django.contrib import admin
# from django.contrib.auth.models import User
from accounts.models import Customer,Product,Order,Tag

# Register your models here.
admin.site.register(Customer)
admin.site.register(Tag)
admin.site.register(Product)
admin.site.register(Order)
# admin.site.register(User)

