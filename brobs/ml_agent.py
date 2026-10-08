"""Optional local scikit-learn model. Abstains without a measured holdout edge."""
from math import isfinite

def predict(closes):
    if len(closes)<150 or any(not isfinite(p) or p<=0 for p in closes):
        return dict(agent='ml',action='unknown',reason='Need 150+ valid prices')
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        return dict(agent='ml',action='unknown',reason='Optional scikit-learn dependency not installed')
    features=[];labels=[]
    for i in range(10,len(closes)-1):
        features.append([closes[i]/closes[i-j]-1 for j in (1,3,5,10)])
        labels.append(int(closes[i+1]>closes[i]))
    split=int(len(features)*.7)
    train_end=split-1  # Purge the boundary label.
    if len(set(labels[:train_end]))<2:return dict(agent='ml',action='unknown',reason='Training has only one class')
    model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=500,random_state=0))
    model.fit(features[:train_end],labels[:train_end])
    accuracy=model.score(features[split:],labels[split:])
    majority=max(sum(labels[split:])/len(labels[split:]),1-sum(labels[split:])/len(labels[split:]))
    action='unknown'
    if accuracy>majority+.02:
        action='buy' if model.predict([[closes[-1]/closes[-1-j]-1 for j in (1,3,5,10)]])[0] else 'sell'
    return dict(agent='ml',action=action,reason='Chronological local model; no calibrated win probability',
        holdout_accuracy=round(accuracy,4),majority_baseline=round(majority,4),test_samples=len(labels)-split)
