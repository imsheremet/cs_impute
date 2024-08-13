import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import idct
from scipy.sparse import identity
import torch
import cvxpy as cp
import h5py

# note that SAITS code needs to be present in parent directory
import sys
sys.path.insert(1, '../SAITS')
from modeling.utils import masked_mae_cal, masked_mre_cal, masked_rmse_cal

STATION_NAMES = ['RSAC064', 'RSAC075', 'RSAC081', 'RSAC092', 'RSAN007','RSAN018']
DATASET_FILE_PATH = '../SAITS/generated_datasets/DSM2/datasets.h5'

# size of basis matrix for CS
N = 72

# generate the IDCT basis
P = idct(identity(N).toarray(), axis=0, norm='ortho')

# function for imputing missing samples using compressive sensing formulation
def impute_cs(miss_idx, y):
    # generate observation matrix
    A = np.copy(P)
    A[miss_idx] = 0

    # recover IDCT coeffs from observations with CS
    xr = cp.Variable(N)
    eps = 0.01
    obj = cp.Minimize(cp.norm(xr,1))
    constr = [cp.norm(A@xr-y,2) <= eps]
    prob = cp.Problem(obj, constr)
    result = prob.solve(solver=cp.CVXOPT, verbose=False)

    # calculate recovered signal
    sr = np.matmul(P,xr.value)

    return sr

# read in DSM2 test data
print('Reading in DSM2 data...')
with h5py.File(DATASET_FILE_PATH, "r") as hf1:
    h5_X = hf1["test"]["X"][:]
    h5_X_hat = hf1["test"]["X_hat"][:]
    h5_missing_mask = hf1["test"]["missing_mask"][:]
    h5_indicating_mask = hf1["test"]["indicating_mask"][:]

# fill in missing measurements
print('Imputing missing data...')
num_smpls,num_meas,num_stations = h5_X.shape
Y = np.zeros((num_smpls,num_meas,num_stations))
for sample in range(num_smpls):
    for station in range(num_stations):
        if np.equal(h5_missing_mask[sample,:,station],0).any():
            s_hat = np.zeros(N)
            s_hat[:num_meas] = h5_X_hat[sample,:,station]
            miss_idx = np.where(h5_missing_mask[sample,:,station]==0)[0]
            s_hat[miss_idx] = 0
            sr = impute_cs(miss_idx, s_hat)
            Y[sample,:,station] = h5_X_hat[sample,:,station]
            Y[sample,miss_idx,station] = sr[miss_idx]
        else:
            Y[sample,:,station] = h5_X_hat[sample,:,station]

# convert data to tensors for calculating performance metrics with the same
# code that is used for SAITS
data = (
    torch.tensor(0),
    torch.from_numpy(np.nan_to_num(h5_X_hat).astype("float32")),
    torch.from_numpy(h5_missing_mask.astype("float32")),
    torch.from_numpy(np.nan_to_num(h5_X).astype("float32")),
    torch.from_numpy(h5_indicating_mask.astype("float32"))
)

indices, X, missing_mask, X_holdout, indicating_mask = map(lambda x: x.to('cuda'), data)
inputs = {
    "indices": indices,
    "X": X,
    "missing_mask": missing_mask,
    "X_holdout": X_holdout,
    "indicating_mask": indicating_mask,
}

# calculate performance metrics
print('Calculating performance metrics...')
masked_mae = masked_mae_cal(torch.from_numpy(Y).to('cuda'), X_holdout, indicating_mask)
masked_mrse = masked_rmse_cal(torch.from_numpy(Y).to('cuda'), X_holdout, indicating_mask)
masked_mre = masked_mre_cal(torch.from_numpy(Y).to('cuda'), X_holdout, indicating_mask)

print('masked_mae_cal : ', masked_mae.item())
print('masked_mrse    : ', masked_mrse.item())
print('masked_mre_cal : ', masked_mre.item())

# write result to file
with open('cs_result.txt', 'w') as f:
    f.write(f'imputation_MAE  : {masked_mae.item()}\n')
    f.write(f'imputation_RMSE : {masked_mrse.item()}\n')
    f.write(f'imputation_MRE  : {masked_mre.item()}\n')
