from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render,render_to_response
from django.contrib.auth.hashers import make_password,check_password
from LostNFound.models import Tags, Categories, UserDetails, User, Lost, Found
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
from django import forms
from haystack.query import SearchQuerySet
from LostNFound.forms import RegisterForm, LostForm, FoundForm, UpdateForm
import random,string,os
from django.core import management
from django.core.urlresolvers import reverse

#______________________________________________________Login Page_______________________________________________________
def index(request):
	if request.GET:
		if request.GET['msg']=='success':
			s = 'An Email has been sent to you containing the password'
		elif request.GET['msg']=='retry':
			s = 'Email Id or Password Invalid'
		elif request.GET['msg']=='logout':
			s = 'Successfully Logged Out'
		elif 'email' in request.COOKIES and request.get_full_path=='/lnf/lost_something/':
			return render(request, 'LostNFound/lost_something.html',{'email':request.COOKIES['email']})
		return render(request, 'LostNFound/index.html',{'msg':s})
	if 'email' in request.COOKIES:
		return render(request, 'LostNFound/profile.html',{'username':request.COOKIES['name']})
	return render(request, 'LostNFound/index.html', {})
	
#______________________________________________________Found Something Form_______________________________________________________
def found_something(request):
	if 'email' in request.COOKIES:
		return render(request,'LostNFound/found_something.html',{'categories':Categories.objects.all(),'tags':Tags.objects.all(),'username':request.COOKIES['name']})
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#______________________________________________________Lost Something Form_______________________________________________________
def lost_something(request):
	if 'email' in request.COOKIES:
		return render(request,'LostNFound/lost_something.html',{'categories':Categories.objects.all(),'tags':Tags.objects.all(),'username':request.COOKIES['name']})
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#______________________________________________________Found Something Form validation____________________________________________
def foundform(request):
	if request.POST and 'email' in request.COOKIES:
		p=request.POST
		if not ( p['itemName'] and p['category'] and p['location'] ):
			return HttpResponse("Error")
		form = FoundForm(request.POST,request.FILES)
		if form.is_valid():
			l=Found(itemName=p['itemName'].capitalize(),anonymity=p.get('anonymity', False),category=Categories.objects.filter(category=p['category'])[0],desc=p['desc'],location=p['location'])
			#form = ImageUploadForm(p,request.FILES)
			#if form.is_valid():
			#	l.image = request.FILES['image']
			l.user = User.objects.filter(email=request.COOKIES['email'])[0]
			l.save()
			for t in p.getlist('tag'):
				if not Tags.objects.filter(tag=t):
					tag = Tags(tag=t)
					tag.save()
					l.tag.add(tag)
				else:
					l.tag.add(Tags.objects.filter(tag=t)[0])
			if request.FILES:
				l.image.save('f'+str(l.id),request.FILES['image'])
			l.save()
			sq=SearchQuerySet().models(Lost)
			for word in l.itemName:
				sq.filter(content=word)
			seen = set()
			seen_add = seen.add
			sq = [ x for x in sq if x.id not in seen and not seen_add(x.id)]
			os.system('python manage.py update_index')
			return HttpResponseRedirect('/lnf/found/'+str(l.id)+'/')
		else:
                        return HttpResponse("Form invalid {% for error in form.errors %} error<br> {% endfor %}")
	else:
		return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#______________________________________________________Lost Something Form validation____________________________________________
def lostform(request):
	if request.POST and 'email' in request.COOKIES:
		p=request.POST
		if not ( p['itemName'] and p['category'] and p['location'] and p['dateLost'] ):
			return HttpResponse("Error")
		form = LostForm(request.POST,request.FILES)
		if form.is_valid():
			l=Lost(itemName=p['itemName'].capitalize(),category=Categories.objects.filter(category=p['category'])[0],desc=p['desc'],dateLost=p['dateLost'],location=p['location'])
			
			
			l.user = User.objects.filter(email=request.COOKIES['email'])[0]
			l.save()
			for t in p.getlist('tag'):
				if not Tags.objects.filter(tag=t):
					tag = Tags(tag=t)
					tag.save()
					l.tag.add(tag)
				else:
					l.tag.add(Tags.objects.filter(tag=t)[0])
			if request.FILES:
				l.image.save('l'+str(l.id),request.FILES['image'])
			l.save()
			os.system('python manage.py update_index')
			return HttpResponseRedirect('/lnf/lost/'+str(l.id)+'/')
		else:
                        return HttpResponse("Form invalid {% for error in form.errors %} error<br> {% endfor %}")
	else:
		return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#________________________________________________Email Validation__________________________________________________________
def email_validate(mailId):
	u = User.objects.filter(email=mailId)
	if u:
		return u[0]
	return None

#________________________________________________Login Validation___________________________________________________________
def login(request):
	if 'email' in request.COOKIES:
		return HttpResponseRedirect('/lnf/')
	if request.POST:
		u=email_validate(request.POST['email'])
		if u and u.isRegistered and check_password(request.POST['pword'],u.userDetails.password):
			response = HttpResponseRedirect("/lnf/")
			response.set_cookie('email',u.email)
			response.set_cookie('name',u.userDetails.name)
			return response
		return HttpResponseRedirect('/lnf/?msg=retry')
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#________________________________________________Register Form___________________________________________________________
def register(request):
	if(request.POST):
		u=email_validate(request.POST['email'])
		if u:
			if not u.isRegistered:
				return render(request, 'LostNFound/register.html',{'email':u.email})
			return HttpResponse("You have already been registered")
		return HttpResponse("Email Invalid")
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

def randomword(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

#________________________________________________Registration Validation___________________________________________________________
def regcheck(request):
	if(request.POST):
		p=request.POST
		u=email_validate(p['email'])
		if u:
			if not u.isRegistered:
                                form = RegisterForm(request.POST)
                                if form.is_valid():
                                        pword=randomword(8)
                                        ud = UserDetails(name=form.cleaned_data['username'],address=form.cleaned_data['address'],password=make_password(pword,'namak'))
                                        ud.save()
                                        send_mail("[LostNFound] Registration password",'Your registration was Successful\npassword: '+pword,settings.EMAIL_HOST_USER,[u.email])
                                        u.isRegistered=True
                                        u.userDetails=ud
                                        u.save()
                                        return HttpResponseRedirect('/lnf/?msg=success')
                                else:
                                        return HttpResponse("<h1>Form not valid!<h1>")
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")
	
#________________________________________________Search Query___________________________________________________________
def search(request,name):
	if 'email' in request.COOKIES:
		if request.GET:
			sq=SearchQuerySet().models(Lost if 'lost'==name else Found)
			for word in request.GET['searchquery'].split(' '):
				sq=sq.filter(content=word)
			keyvalue = {'name':'title','latest':'-date'}
			if request.GET['order'] != 'relevance':
				sq=sq.order_by(keyvalue[request.GET['order']])
			if request.GET['category']!='all':
				a = [ x for x in sq if x.category == request.GET['category'] ]
			else:
				a=sq
			seen = set()
			seen_add = seen.add
			a = [ x for x in a if x.id not in seen and not seen_add(x.id)]
			return render(request,'LostNFound/search.html',{'object':a,'type':name,'categories':Categories.objects.all(),'username':request.COOKIES['name']})
		return render(request,'LostNFound/search.html',{'type':name,'categories':Categories.objects.all(),'username':request.COOKIES['name']})
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#_______________________________________________Lost Object Description___________________________________________________________
def lostobject(request,oid):
	if 'email' in request.COOKIES:
		l=Lost.objects.get(id=oid)
		msg=''
		if request.GET:
			if request.GET['msg']=='email':
				msg='Email Sent'
			elif request.GET['msg']=='edit':
				msg='Item Edited'
		if request.COOKIES['email']==l.user.email:
			sq=SearchQuerySet().models(Found)
			for word in l.itemName.split(' '):
				sq=sq.filter(content=word)
			for word in l.tag.all():
				sq=sq.filter(content=word)
			seen = set()
			seen_add = seen.add
			sq = [ x for x in sq if x.id not in seen and not seen_add(x.id)]
			return render(request,'LostNFound/object.html',{'type':'lost','othertype':'found','object':l,'anonymous':'false','similarlist':'true','items':sq,'msg':msg,'username':request.COOKIES['name']})
		return render(request,'LostNFound/object.html',{'type':'lost','object':l,'anonymous':'false','msg':msg,'username':request.COOKIES['name']})
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#_______________________________________________Found Object Description___________________________________________________________
def foundobject(request,oid):
	if 'email' in request.COOKIES:
		f=Found.objects.get(id=oid)
		msg=''
		if request.GET:
			if request.GET['msg']=='email':
				msg='Email Sent'
			elif request.GET['msg']=='edit':
				msg='Item Edited'
		if request.COOKIES['email']==f.user.email:
			sq=SearchQuerySet().models(Lost)
			for word in f.itemName.split(' '):
				sq=sq.filter(content=word)
			for word in f.tag.all():
				sq=sq.filter(content=word)
			seen = set()
			seen_add = seen.add
			sq = [ x for x in sq if x.id not in seen and not seen_add(x.id)]
			return render(request,'LostNFound/object.html',{'type':'found','othertype':'lost','object':f,'anonymous':'false','similarlist':'true','items':sq,'msg':msg,'username':request.COOKIES['name']})
	if f.anonymity:
		return render(request,'LostNFound/object.html',{'type':'found','object':f,'msg':msg,'username':request.COOKIES['name']})
	else:
		return render(request,'LostNFound/object.html',{'type':'found','object':f,'anonymous':'false','msg':msg,'username':request.COOKIES['name']})

#_______________________________________________Lost Objects by user________________________________________________________
def lost(request):
	if 'email' in request.COOKIES:
		l=User.objects.get(email=request.COOKIES['email'])
		l=l.lost_set.all()
		return render(request,'LostNFound/myitems.html',{'type':'lost','object':l,'username':request.COOKIES['name']})
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#_______________________________________________Found Objects by user________________________________________________________
def found(request):
	if 'email' in request.COOKIES:
		f=User.objects.get(email=request.COOKIES['email'])
		f=f.found_set.all()
		return render(request,'LostNFound/myitems.html',{'type':'found','object':f,'username':request.COOKIES['name']})
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#_______________________________________________Lost Email by user________________________________________________________
def emailLost(request,oid):
	if 'email' in request.COOKIES and request.POST:
		subject='[LostNFound] Query by user'
		string='Hey<br>'+User.objects.get(email=request.COOKIES['email']).userDetails.name+' ('+request.COOKIES['email']+') wants to query about the item <a href='+request.build_absolute_uri('../')+'>'+Lost.objects.get(id=oid).itemName+'</a> lost by you.<br>Message:<br>'+request.POST['content']
		mail=Lost.objects.get(id=oid).user.email
		msg = EmailMultiAlternatives(subject, string, request.COOKIES['email'], [mail])
		msg.attach_alternative(string, "text/html")
		msg.send()
		return HttpResponseRedirect('../?msg=email')
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#_______________________________________________Found Email by user________________________________________________________
def emailFound(request,oid):
	if 'email' in request.COOKIES and request.POST:
		subject='[LostNFound] Query by user'
		string='Hey<br>'+User.objects.get(email=request.COOKIES['email']).userDetails.name+' ('+request.COOKIES['email']+') wants to query about the item <a href='+request.build_absolute_uri('../')+'>'+Found.objects.get(id=oid).itemName+'</a> found by you.<br>Message:<br>'+request.POST['content']
		mail=Found.objects.get(id=oid).user.email
		msg = EmailMultiAlternatives(subject, string, request.COOKIES['email'], [mail])
		msg.attach_alternative(string, "text/html")
		msg.send()
		return HttpResponseRedirect('../?msg=email')
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#_______________________________________________Edit Lost Items________________________________________________________
def editLost(request,oid):
	if 'email' in request.COOKIES and request.COOKIES['email']==Lost.objects.get(id=oid).user.email:
		if request.POST:
			p=request.POST
			if not ( p['itemName'] and p['category'] and p['location'] and p['dateLost']):
				return HttpResponse("Error")
			form = LostForm(request.POST,request.FILES)
			if form.is_valid():
				l = Lost.objects.get(id=request.POST['oid'])
				l.itemName = form.cleaned_data['itemName']
				l.category = Categories.objects.filter(category=form.cleaned_data['category'])[0]
				l.desc = form.cleaned_data['desc']
				l.location = form.cleaned_data['location']
				l.dateLost = form.cleaned_data['dateLost']
				l.save()
				for t in p.getlist('tag'):
					if not Tags.objects.filter(tag=t):
						tag = Tags(tag=t)
						tag.save()
						l.tag.add(tag)
					else:
						l.tag.add(Tags.objects.filter(tag=t)[0])
				if request.FILES:
					if l.image:
						fullname = os.path.join(settings.MEDIA_ROOT,l.image.name)
						os.remove(fullname)
					l.image.save('l'+str(l.id),request.FILES['image'])
				l.save()
				management.call_command('rebuild_index', interactive=False, verbosity=0)
				return HttpResponseRedirect('../?msg=edit')
			else:
		                return HttpResponse("Form invalid {% for error in form.errors %} error<br> {% endfor %}")
		l = Lost.objects.get(id=oid)
		return render(request,'LostNFound/edit_lost.html',{'categories':Categories.objects.all(),'tags':Tags.objects.all(),'object':l,'username':request.COOKIES['name']})
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#_______________________________________________Delete Lost Items________________________________________________________
def deleteLost(request,oid):
	if 'email' in request.COOKIES and request.COOKIES['email']==Lost.objects.get(id=oid).user.email:
		Lost.objects.get(id=oid).delete()
		management.call_command('rebuild_index', interactive=False, verbosity=0)
		return HttpResponseRedirect('/lnf/lost/')
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#_______________________________________________Delete Found Items________________________________________________________
def deleteFound(request,oid):
	if 'email' in request.COOKIES and request.COOKIES['email']==Found.objects.get(id=oid).user.email:
		Found.objects.get(id=oid).delete()
		management.call_command('rebuild_index', interactive=False, verbosity=0)
		return HttpResponseRedirect('/lnf/found/')
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#_______________________________________________Edit Found Items________________________________________________________
def editFound(request,oid):
	if 'email' in request.COOKIES and request.COOKIES['email']==Found.objects.get(id=oid).user.email:
		if request.POST:
			p=request.POST
			if not ( p['itemName'] and p['category'] and p['location']):
				return HttpResponse("Error")
			form = FoundForm(request.POST,request.FILES)
			if form.is_valid():
				f = Found.objects.get(id=request.POST['oid'])
				f.itemName = form.cleaned_data['itemName']
				f.category = Categories.objects.filter(category=form.cleaned_data['category'])[0]
				f.desc = form.cleaned_data['desc']
				f.location = form.cleaned_data['location']
				f.anonymity=p.get('anonymity', False)
				f.save()
				for t in p.getlist('tag'):
					if not Tags.objects.filter(tag=t):
						tag = Tags(tag=t)
						tag.save()
						f.tag.add(tag)
					else:
						f.tag.add(Tags.objects.filter(tag=t)[0])
				if request.FILES:
					if f.image:
						fullname = os.path.join(settings.MEDIA_ROOT,f.image.name)
						os.remove(fullname)
					f.image.save('f'+str(f.id),request.FILES['image'])
				f.save()
				management.call_command('rebuild_index', interactive=False, verbosity=0)
				return HttpResponseRedirect('../?msg=edit')
			else:
		                return HttpResponse("Form invalid {% for error in form.errors %} error<br> {% endfor %}")
		f = Found.objects.get(id=oid)
		return render(request,'LostNFound/edit_found.html',{'categories':Categories.objects.all(),'tags':Tags.objects.all(),'object':f,'username':request.COOKIES['name']})
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#_______________________________________________Logout________________________________________________________
def logout(request):
	response = HttpResponseRedirect("/lnf/?msg=logout")
	response.delete_cookie('email')
	response.delete_cookie('name')
	return response

#_______________________________________________Edit and display profile________________________________________________________
def profile(request):
	if 'email' in request.COOKIES:
		if request.POST:
			p = request.POST
			form = UpdateForm(p)
			if form.is_valid():
				if not ( form.cleaned_data['username'] and form.cleaned_data['address']):
					return HttpResponse("Form invalid")
				u = User.objects.get(email = request.COOKIES['email']).userDetails
				u.name = form.cleaned_data['username']
				u.address = form.cleaned_data['address']
				u.save()
				if form.cleaned_data['oldpword']:
					if not (form.cleaned_data['oldpword'] and check_password(form.cleaned_data['oldpword'],u.password)):
						return HttpResponseRedirect("error/?msg=invalid")
					if form.cleaned_data['pword'] and len(form.cleaned_data['pword'])>= 5 and form.cleaned_data['pword']==form.cleaned_data['confpword']:
						u.password=make_password(form.cleaned_data['pword'],'namak')
						u.save()
					else:
						return HttpResponseRedirect("error/?msg=invalid")
			else:
				return HttpResponseRedirect("error/?msg=invalid")
		return render(request,'LostNFound/myprofile.html',{'object':User.objects.get(email=request.COOKIES['email']),'username':request.COOKIES['name']})
	return HttpResponse("<h1>Fatal Error 404: Not Found</h1>")

#_______________________________________________Error Page________________________________________________________
def error(request):
	s='Error'
	if request.GET:
		s=request.GET['msg']
		if s=='invalid':
			msg='Invalid Password'
	return render(request,'LostNFound/error.html',{'msg':msg})
