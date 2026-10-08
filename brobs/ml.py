"""Optional sklearn time-series classification baseline; research only."""
def evaluate_direction_model(closes,train_fraction=0.7):
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import make_pipeline
    except ImportError as e:
        raise RuntimeError("Install optional dependency: pip install scikit-learn") from e
    if len(closes)<100 or any(p<=0 for p in closes): raise ValueError("Need 100+ positive closes")
    if not 0.5<=train_fraction<=0.85: raise ValueError("Invalid split")
    features=[];labels=[]
    for i in range(10,len(closes)-1):
        features.append([(closes[i]/closes[i-j]-1) for j in (1,3,5,10)])
        labels.append(int(closes[i+1]>closes[i]))
    split=int(len(features)*train_fraction)
    if len(set(labels[:split]))<2: return {"status":"insufficient_train_classes"}
    model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=500))
    model.fit(features[:split],labels[:split])
    accuracy=model.score(features[split:],labels[split:])
    baseline=max(sum(labels[split:])/len(labels[split:]),1-sum(labels[split:])/len(labels[split:]))
    return {"status":"research_only","test_samples":len(labels)-split,"out_of_sample_accuracy":round(accuracy,4),"majority_class_baseline":round(baseline,4)}
