import numpy as np


def entropy(probs):
    terms = probs * np.log2(probs)
    terms[np.isnan(terms)] = 0
    return -np.sum(terms)

def gini(probs):
    return 1 - np.sum(probs ** 2)


def cluster_entropy(y_clusters, y_labels, output='average'):
    
    cluster_entropies = {}

    for cluster in np.unique(y_clusters):
        
        cluster_labels = y_labels[y_clusters == cluster]
        probs = np.bincount(cluster_labels) / len(cluster_labels)
        
        cluster_entropies[cluster] = entropy(probs)
        
    return cluster_entropies


def cluster_gini(y_clusters, y_labels):
    
    cluster_ginis = {}
    
    for cluster in np.unique(y_clusters):
        
        cluster_labels = y_labels[y_clusters == cluster]
        probs = np.bincount(cluster_labels) / len(cluster_labels)

        cluster_ginis[cluster] = gini(probs)
        
    return cluster_ginis