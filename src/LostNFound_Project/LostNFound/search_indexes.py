from haystack import indexes
from LostNFound.models import Lost,Found

class LostIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	title = indexes.CharField(model_attr='itemName')
	desc = indexes.CharField(model_attr='desc')
	date = indexes.DateField(model_attr='dateLost')
	category = indexes.CharField(model_attr='category')
	oid = indexes.IntegerField(model_attr='id')
	def get_model(self):
		return Lost
	def index_queryset(self,using=None):
		return self.get_model().objects.all()

class FoundIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	title = indexes.CharField(model_attr='itemName')
	desc = indexes.CharField(model_attr='desc')
	date = indexes.DateField(model_attr='timestamp')
	oid = indexes.IntegerField(model_attr='id')
	category = indexes.CharField(model_attr='category')

	def get_model(self):
		return Found
	def index_queryset(self,using=None):
		return self.get_model().objects.all()
