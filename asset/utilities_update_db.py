# This is to be run weekly
import pandas as pd
import os
import glob

def go_to_parent(path):
	print("type: ", type(path))
	cnt=0
	for i in path:
		if i=='/':
			index = cnt
		cnt=cnt+1
	path_par = path[0:index]
	return path_par	

# os.chdir("..") #cd changed from asset to backend
# os.chdir("..") #cd changed from backend to Alpha_TermProject
path = os.path.abspath(os.curdir)
path = go_to_parent(path)
path = go_to_parent(path)
path+="/Data_reqd/Data/"
print("path: ", path)
#print("type: ", type(path))

csv_files = glob.glob(os.path.join(path, "*.csv"))
cnt=0
df = pd.DataFrame()


####### This is very important and is required
import sys
import os
import django
sys.path.append('/Users/avirajbevli/Desktop/Alpha_TermProject/backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()
from asset.models import Asset
################


for f in csv_files:
	# print(f)
	# read the csv file
	df_temp = pd.read_csv(f)
	f = f[-10:]
	f = f[:6]
	# print(f)
	# print("------------")
	df[f] = df_temp['Open Price']
	cnt = cnt+1

	# save in database
	if Asset.objects.filter(security_id=f).exists():
		continue
	else:
		asset = Asset(security_id=f)
		asset.save()


returns = df.pct_change()
returns.dropna(inplace=True) 
print("++++++++++++++++++++++++++++++++ Returns are  : ")
print(returns.head())
print(returns.shape)


import numpy as np
num_assets = len(returns.columns)
print('Total number of assets: ', num_assets)
cov = returns.cov()
print("!!!!!!!!!!!!!!!!!!!!!!!!!! COV matrix : ")
print(cov.head())
print(cov.shape)

cov_inv = pd.DataFrame(np.linalg.pinv(cov.values), cov.columns, cov.index)
print("--------------------------- COV inv matrix : ")
print(cov_inv.head())
print(cov_inv.shape)

path = os.path.abspath(os.curdir)
path = go_to_parent(path)
path = go_to_parent(path)
path1 = path
path1 += '/Data_reqd/results/cov.pkl'
path2 = path
path2 += '/Data_reqd/results/cov_inv.pkl'
# cov.to_pickle("Data_reqd/results/cov.pkl")
# cov_inv.to_pickle("Data_reqd/results/cov_inv.pkl")


##################### populate the expected returns, expected risk of each asset in database
expected_returns = returns.mean(axis=0).to_numpy()
print("!!!!!!!!!!!!!expected_returns: ", expected_returns)
expected_risks = returns.var(axis=0).to_numpy()
print("!!!!!!!!!!!!!expected_risks: ", expected_risks)

# expected_returns.to_pickle("Data_reqd/results/expected_returns.pkl")
# expected_risks.to_pickle("Data_reqd/results/expected_risks.pkl")
path += '/Data_reqd/results/expected_returns_risks.npy'
with open(path, 'wb') as f:
    np.save(f, expected_returns)
    np.save(f, expected_risks)

#print("COLUMNS: ")
i=0
for column in returns:
    #print(column)
    #print("type(column): ", type(column)) #<class 'str'>
    asset = Asset.objects.get(security_id=column)
    asset.exp_return = expected_returns[i]
    asset.exp_risk = expected_risks[i]
    asset.save()
    i=i+1

