# This is to be run only once in history


####### This is very important and is required
import sys
import os
import django
import pandas as pd
sys.path.append('/Users/avirajbevli/Desktop/Alpha_TermProject/backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()
from asset.models import Asset
################

def go_to_parent(path):
	# print("type: ", type(path))
	cnt=0
	for i in path:
		if i=='/':
			index = cnt
		cnt=cnt+1
	path_par = path[0:index]
	return path_par	


path = os.path.abspath(os.curdir)
path = go_to_parent(path)
path = go_to_parent(path)
path+="/Data_reqd/Equity.csv"
print("path: ", path)
#print("type: ", type(path))

df = pd.read_csv(path) 
# print(df.head())
for index, row in df.iterrows():
	# print(index, ": ", row['Security Code'])
	# print("type(index): ", type(index)) #type=int
	index = str(index)
	print(index)
	#print("type(index): ", type(index)) #type=str
	if Asset.objects.filter(security_id=index).exists():
		asset = Asset.objects.get(security_id=index)
		asset.ticker_name = row['Security Code']
		asset.save()
