rfr = 0.05 #risk_free_rate

def go_to_parent(path):
	# print("type: ", type(path))
	cnt=0
	for i in path:
		if i=='/':
			index = cnt
		cnt=cnt+1
	path_par = path[0:index]
	return path_par	


def calculate_delta_sentiment():
	####### This is very important and is required
	import sys
	import os
	import django
	import numpy as np
	sys.path.append('/Users/avirajbevli/Desktop/Alpha_TermProject/backend')
	os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
	django.setup()
	# ################
	# os.chdir("..") #cd changed from asset to backend
	# os.chdir("..") #cd changed from backend to Alpha_TermProject
	path = os.path.abspath(os.curdir)
	# print("path: ", path) # /Users/avirajbevli/Desktop/Alpha_TermProject/backend
	path = go_to_parent(path) #backend to Alpha_TermProject
	path += '/Data_reqd/results/sent_arr50.npy'

	print("-++++++++++++++++++++++++++++++______________+++++++++++++")
	print("path: ", path)
	with open(path, 'rb') as f:
	    sent_arr50 = np.load(f)

	sum=0
	cnt=0
	for sent in sent_arr50:
		sum+=sent
		cnt=cnt+1
		if cnt==30:
			ma30d = sum

	ma30d/=30
	ma50d = sum/50
	print("ma30d: ", ma30d)
	print("ma50d: ", ma50d)
	return ma30d - ma50d
	#return 0.5

def modify_rate(rfr, delta_sentiment):
	if delta_sentiment>0:
		rate = rfr + (2*rfr*delta_sentiment)
	else:
		rate = rfr + (rfr*delta_sentiment)
	return rate

def calculate_rate():
	delta_sentiment = calculate_delta_sentiment()
	reqd_rate = modify_rate(rfr, delta_sentiment)
	return reqd_rate

def is_present(key, asset_list):
	# print("is_present: ")
	for asset_ in asset_list:
		# print(asset_)
		if asset_['asset'] == key:
			return 1
	return 0

def MV2(assets): #assets is a list of dict
	####### This is very important and is required
	import sys
	import os
	import django
	sys.path.append('/Users/avirajbevli/Desktop/Alpha_TermProject/backend')
	os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
	django.setup()
	################
	print("----------------Inside MV2")
	directory = os.getcwd()
	print("CWD: ", directory) #cd: backend

	import numpy as np
	import pandas as pd
	num_assets = len(assets) 

	reqd_return = calculate_rate() 
	print("####################### reqd_return: ", reqd_return, " #########################")
	e = np.ones(num_assets, dtype=float)
	# cov = pd.read_pickle("../Data_reqd/results/cov.pkl")
	# cov_inv = pd.read_pickle("../Data_reqd/results/cov_inv.pkl")

	# print("BEFORE!!!!!!!!!!!!!!!!")
	# with open('../Data_reqd/results/test.npy', 'rb') as f:
	#     miu = np.load(f)
	#     expected_risks = np.load(f)
	# print("!!!!!!!!!!!!!!!!!AFTER")

	################ THIS IS NOT CORRECT because of the dimension mismatch
	################ Wanna reshape cov, miu, cov_inv acc to the selected assets

	# mat_den = np.array([ [np.transpose(miu)@cov_inv@miu, np.transpose(miu)@cov_inv@e],
	#                      [np.transpose(e)@cov_inv@miu, np.transpose(e)@cov_inv@e] ])
	# mat1 = np.array([ [2*reqd_return, np.transpose(miu)@cov_inv@e],
	#                     [2, np.transpose(e)@cov_inv@e] ])
	# mat2 = np.array([ [np.transpose(miu)@cov_inv@miu, 2*reqd_return],
	#                     [np.transpose(e)@cov_inv@miu, 2] ])

	# lambda1 = np.linalg.det(mat1) / np.linalg.det(mat_den)
	# lambda2 = np.linalg.det(mat2) / np.linalg.det(mat_den)

	# print('lambda1: ',lambda1, ', lambda2: ',lambda2)
	# w_star = ((lambda1/2)*(cov_inv@miu)) + ((lambda2/2)*(cov_inv@e))

	# # Total return of Portfolio ->
	# tot_return = np.transpose(w_star) @ miu
	# print('Total return: ', tot_return)

	# # Total risk of Portfolio ->
	# tot_risk = np.transpose(w_star) @ cov @ w_star
	# print('Total Risk: ',tot_risk)


	## Solution ->
	asset_indices_selected = []

	import pandas as pd
	import glob

	# os.chdir("..") #cd changed from backend to Alpha_TermProject
	path = os.path.abspath(os.curdir)
	print("path: ", path)
	path = go_to_parent(path)
	path+="/Data_reqd/Data/"
	print("path: ", path)
	#print("type: ", type(path))

	# df will be a dataframe only consisting of selected assets info
	df = pd.DataFrame()
	csv_files = glob.glob(os.path.join(path, "*.csv"))
	for f in csv_files:
		df_temp = pd.read_csv(f)
		f = f[-10:]
		f = f[:6]
		if is_present(f, assets):
			df[f] = df_temp['Open Price']

	#print("@@@@@@@@@@@@@@@@@@@@@@@@    DF: ", df)
	returns = df.pct_change()
	returns.dropna(inplace=True) 
	print("++++++++++++++++++++++++++++++++ Returns are  : ")
	print(returns.head())
	print(returns.shape)


	import numpy as np
	num_assets = len(returns.columns)
	print('Total number of assets: ', num_assets)
	asset_cov = returns.cov()
	print("!!!!!!!!!!!!!!!!!!!!!!!!!! COV matrix : ")
	print(asset_cov.head())
	print(asset_cov.shape)

	asset_cov_inv = pd.DataFrame(np.linalg.pinv(asset_cov.values), asset_cov.columns, asset_cov.index)
	print("--------------------------- COV inv matrix : ")
	print(asset_cov_inv.head())
	print(asset_cov_inv.shape)


	##################### populate the expected returns, expected risk of each asset in database
	asset_miu = returns.mean(axis=0).to_numpy()
	print("!!!!!!!!!!!!!asset_miu: ", asset_miu)

	mat_den = np.array([ [np.transpose(asset_miu)@asset_cov_inv@asset_miu, np.transpose(asset_miu)@asset_cov_inv@e],
	                     [np.transpose(e)@asset_cov_inv@asset_miu, np.transpose(e)@asset_cov_inv@e] ])
	mat1 = np.array([ [2*reqd_return, np.transpose(asset_miu)@asset_cov_inv@e],
	                    [2, np.transpose(e)@asset_cov_inv@e] ])
	mat2 = np.array([ [np.transpose(asset_miu)@asset_cov_inv@asset_miu, 2*reqd_return],
	                    [np.transpose(e)@asset_cov_inv@asset_miu, 2] ])

	lambda1 = np.linalg.det(mat1) / np.linalg.det(mat_den)
	lambda2 = np.linalg.det(mat2) / np.linalg.det(mat_den)

	print('lambda1: ',lambda1, ', lambda2: ',lambda2)
	w_star = ((lambda1/2)*(asset_cov_inv@asset_miu)) + ((lambda2/2)*(asset_cov_inv@e))

	# Total return of Portfolio ->
	tot_return = np.transpose(w_star) @ asset_miu
	print('Total return: ', tot_return)

	# Total risk of Portfolio ->
	tot_risk = np.transpose(w_star) @ asset_cov @ w_star
	print('Total Risk: ',tot_risk)

	print("sanity check, sum of weights: _________________ ", w_star.sum())

	portfolio = []
	i=0
	for asset in assets:
		dict_temp = {
			'asset':asset['asset'],
			'weight':w_star[i],
		}
		i=i+1
		portfolio.append(dict_temp)
	return portfolio



def calculate_portfolio(assets):
	num_assets = len(assets) 
	weights = []
	key = 1/num_assets

	# print("type: ", type(assets))
	# print("The selected assets are : ")
	# for asset in assets:
	# 	db_asset = Asset.objects.get(ticker_id=asset)
	# 	print(asset, "(", db_asset.exp_return, ",", db_asset.exp_risk, ")")
	# 	weights.append(key)
	# return weights

	print("num_assets: ", num_assets)
	our_assets = []
	from asset.models import Asset
	for asset in assets:
		db_asset = Asset.objects.get(security_id=asset)
		print(asset, "(", db_asset.exp_return, ",", db_asset.exp_risk, ")")
		dict_temp = {
			'asset':asset,
			'exp_return':db_asset.exp_return,
			'exp_risk':db_asset.exp_risk,
		}
		our_assets.append(dict_temp)
	portfolio = MV2(our_assets)
	return portfolio
	
	# our_assets = []
	# from asset.models import Asset
	# for asset in assets:
	# 	db_asset = Asset.objects.get(security_id=asset)
	# 	#print(asset, "(", db_asset.exp_return, ",", db_asset.exp_risk, ")")
	# 	dict_temp = {
	# 		'asset':asset,
	# 		'exp_return':db_asset.exp_return,
	# 		'exp_risk':db_asset.exp_risk,
	# 		'weight':key,
	# 	}
	# 	our_assets.append(dict_temp)
	# return our_assets
