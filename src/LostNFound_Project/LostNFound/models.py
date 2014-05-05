from django.db import models
import datetime
from django.utils import timezone

class Tags(models.Model):
	tag = models.CharField(max_length=128)
	def __str__(self):
		return self.tag

class Categories(models.Model):
	category = models.CharField(max_length=128)
	def __str__(self):
		return self.category

class UserDetails(models.Model):
	name = models.CharField(max_length=128)
	address = models.CharField(max_length=256)			#(optional)
	password = models.CharField(max_length=128)
	def __str__(self):
		return self.name

class User(models.Model):
	email = models.CharField(max_length=64)
	userDetails = models.ForeignKey(UserDetails,blank=True,null=True)
	isRegistered = models.BooleanField(default=False)
	def __str__(self):
		return self.email

class Lost(models.Model):
	user = models.ForeignKey(User)
	itemName = models.CharField(max_length=128)
	category = models.ForeignKey(Categories)
	desc = models.CharField(max_length=256,blank=True,null=True)
	image = models.ImageField(upload_to='pic',blank=True,null=True)
	dateLost = models.DateField()
	location = models.CharField(max_length=128)
	timestamp = models.DateTimeField(auto_now_add=True)
	tag = models.ManyToManyField(Tags,blank=True,null=True)
	def isExpired(self):
		return self.timestamp <= timezone.now() - datetime.timedelta(days=30)
	def __str__(self):
		return self.itemName

class Found(models.Model):
	user = models.ForeignKey(User)
	itemName = models.CharField(max_length=128)
	anonymity = models.BooleanField(default=False)
	category = models.ForeignKey(Categories)
	desc = models.CharField(max_length=128,blank=True,null=True)
	image = models.ImageField(upload_to='pic',blank=True,null=True)
	location = models.CharField(max_length=128)
	tag = models.ManyToManyField(Tags,blank=True,null=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	def isExpired(self):
		return self.timestamp <= timezone.now() - datetime.timedelta(days=30)
	def __str__(self):
		return self.itemName
