import numpy as np

# paper uses RMSE

def rmse(pred, target):
    """RMSE"""
    return np.sqrt(np.mean((pred - target) ** 2))

def rmse_seq(seq1, seq2):
    """RMSE for sequences"""
    len_seq = len(seq1)
    rmses = {}
    for frame in range(len_seq):
        rmses[frame] = rmse(seq1[frame], seq2[frame])
        
    return rmses