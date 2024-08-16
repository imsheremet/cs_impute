import numpy as np
from matplotlib import pyplot as plt

#### Plot results for sparse missing masks ####

# read in data from csv file
data = np.genfromtxt('tests_results_sparse_1723587183.csv', delimiter=',')

# plot data
plt.figure()
plt.plot(data[:,1], data[:,2], 'o-')
plt.plot(data[:,1], data[:,3], 'o-')
plt.plot(data[:,1], data[:,4], 'o-')
plt.grid(True)
plt.ylim(0,1)
plt.legend(['MAE','RMSE','MRE'])
plt.xlabel('Percent Missing')
plt.savefig('plots/cs_sparse_results.png')

#### Plot results for block missing masks ####

# read in data from csv file
data = np.genfromtxt('tests_results_block_1723594166.csv', delimiter=',')

# plot data
plt.figure()
plt.plot(data[:,1], data[:,2], 'o-')
plt.plot(data[:,1], data[:,3], 'o-')
plt.plot(data[:,1], data[:,4], 'o-')
plt.grid(True)
plt.ylim(0,1.5)
plt.legend(['MAE','RMSE','MRE'])
plt.xlabel('Missing Block Length')
plt.savefig('plots/cs_block_results.png')
