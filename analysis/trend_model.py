import numpy as np
from collections import defaultdict
from datetime import datetime

def compute_trends(records, embeddings):
    # Example: monthly embedding centroid
    monthly = defaultdict(list)

    for rec, emb in zip(records, embeddings):
        if rec["date"] is None:
            continue
        month = rec["date"][:7]  # "YYYY-MM"
        monthly[month].append(np.array(emb))

    monthly_trends = {
        month: np.mean(vectors, axis=0).tolist()
        for month, vectors in monthly.items()
    }

    return monthly_trends
