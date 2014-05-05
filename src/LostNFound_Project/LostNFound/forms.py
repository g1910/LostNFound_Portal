from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=128)
    address = forms.CharField(max_length=256)

class LostForm(forms.Form):
    itemName = forms.CharField(max_length=128)
    category = forms.CharField(max_length=128)
    desc = forms.CharField(required=False,max_length=256)
    image = forms.ImageField(required=False)
    dateLost = forms.DateField()
    location = forms.CharField(max_length=128)

class FoundForm(forms.Form):
    itemName = forms.CharField(max_length=128)
    anonymity = forms.BooleanField(required=False)
    category = forms.CharField(max_length=128)
    desc = forms.CharField(required=False,max_length=256)
    image = forms.ImageField(required=False)
    location = forms.CharField(max_length=128)
    
class UpdateForm(forms.Form):
	username = forms.CharField(max_length=128)
	address = forms.CharField(max_length=256)
	oldpword = forms.CharField(max_length = 16, required=False)
	pword = forms.CharField(max_length = 16, required=False)
	confpword = forms.CharField(max_length = 16,required=False)

    
    
    
