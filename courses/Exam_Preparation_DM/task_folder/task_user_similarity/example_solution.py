#!function!#
import numpy as np
from scipy.spatial.distance import cosine
def user_similarity(user1, user2, feedback_type='explicit'):
#!prefix!#
    common_items = np.intersect1d(np.where(user1 != 0), np.where(user2 != 0))
    
    if feedback_type == 'explicit':
        if len(common_items) == 0:
            return 0  # No common items, return zero correlation
        
        # Compute means
        mean_user1 = np.nanmean(user1)
        mean_user2 = np.nanmean(user2)
        
        # Compute Pearson Correlation
        numerator = np.sum((user1[common_items] - mean_user1) * (user2[common_items] - mean_user2))
        denominator = np.sqrt(np.sum((user1[common_items] - mean_user1)**2) * np.sum((user2[common_items] - mean_user2)**2))
        
        if denominator == 0:
            return 0  # Avoid division by zero
        
        correlation = numerator / denominator
        return correlation
    
    elif feedback_type == 'implicit':
        if len(common_items) == 0:
            return 0  # No common items, return zero similarity
        
        # Compute Cosine Similarity for binary data
        similarity = cosine(user1[common_items], user2[common_items])
        return similarity
    
    else:
        raise ValueError("Invalid feedback_type. Use 'explicit' or 'implicit'.")
