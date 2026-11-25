"""Reproducible Module 4 model run. No row identifiers are logged as features."""
from __future__ import annotations
import json
from pathlib import Path
import warnings

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix,
    f1_score, precision_score, recall_score, roc_auc_score, RocCurveDisplay)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
OUT = HERE / "reports"
ART = HERE / "model_artifacts"
PLOTS = OUT / "figures"
OUT.mkdir(parents=True, exist_ok=True); ART.mkdir(parents=True, exist_ok=True); PLOTS.mkdir(parents=True, exist_ok=True)
NUM = ["estimated_lead_days", "item_count", "basket_value", "freight_value"]
CAT = ["category", "customer_region", "seller_region", "purchase_month", "purchase_weekday", "purchase_hour"]
FEATURES = NUM + CAT
REGIONS = {
    "North": "AC AM AP PA RO RR TO", "Northeast": "AL BA CE MA PB PE PI RN SE",
    "Central-West": "DF GO MT MS", "Southeast": "ES MG RJ SP", "South": "PR RS SC",
}


def region(state):
    return next((r for r, states in REGIONS.items() if state in states.split()), "Unknown")


def load_model_table():
    files = {
        "orders": ("olist_orders_dataset.csv", ["order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]),
        "customers": ("olist_customers_dataset.csv", ["customer_id", "customer_state"]),
        "items": ("olist_order_items_dataset.csv", ["order_id", "product_id", "seller_id", "price", "freight_value"]),
        "products": ("olist_products_dataset.csv", ["product_id", "product_category_name"]),
        "sellers": ("olist_sellers_dataset.csv", ["seller_id", "seller_state"]),
        "translation": ("product_category_name_translation.csv", ["product_category_name", "product_category_name_english"]),
    }
    t = {k: pd.read_csv(RAW / filename, usecols=cols) for k, (filename, cols) in files.items()}
    o = t["orders"].drop_duplicates("order_id").copy()
    for col in ["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]:
        o[col] = pd.to_datetime(o[col], errors="coerce", utc=True)
    o = o.merge(t["customers"].drop_duplicates("customer_id"), on="customer_id", how="left", validate="many_to_one")
    it = t["items"].drop_duplicates().merge(t["products"].drop_duplicates("product_id"), on="product_id", how="left", validate="many_to_one")
    it = it.merge(t["translation"].drop_duplicates("product_category_name"), on="product_category_name", how="left", validate="many_to_one")
    it = it.merge(t["sellers"].drop_duplicates("seller_id"), on="seller_id", how="left", validate="many_to_one")
    it["category"] = it["product_category_name_english"].fillna("Unknown")
    item = it.groupby("order_id", as_index=False).agg(
        item_count=("product_id", "size"), basket_value=("price", "sum"), freight_value=("freight_value", "sum"),
        category=("category", lambda s: s.mode().iat[0] if not s.mode().empty else "Unknown"),
        seller_state=("seller_state", lambda s: s.dropna().mode().iat[0] if not s.dropna().mode().empty else "Unknown"))
    o = o.merge(item, on="order_id", how="inner", validate="one_to_one")
    eligible = (o.order_status.eq("delivered") & o.order_purchase_timestamp.notna() &
                o.order_delivered_customer_date.notna() & o.order_estimated_delivery_date.notna())
    o = o.loc[eligible].copy()
    o["late"] = (o.order_delivered_customer_date > o.order_estimated_delivery_date).astype("int8")
    o["estimated_lead_days"] = (o.order_estimated_delivery_date - o.order_purchase_timestamp).dt.total_seconds() / 86400
    o["purchase_month"] = o.order_purchase_timestamp.dt.month.astype(str)
    o["purchase_weekday"] = o.order_purchase_timestamp.dt.dayofweek.astype(str)
    o["purchase_hour"] = o.order_purchase_timestamp.dt.hour.astype(str)
    o["customer_region"] = o.customer_state.map(region).fillna("Unknown")
    o["seller_region"] = o.seller_state.map(region).fillna("Unknown")
    # Keep time solely for the temporal split; never pass timestamps or IDs into model features.
    return o[["order_purchase_timestamp", "late", *FEATURES]].replace([np.inf, -np.inf], np.nan).dropna(subset=NUM + ["late"])


def make_preprocessor():
    return ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUM),
        ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=25))]), CAT),
    ])


def score(y, pred, prob):
    return {"accuracy": float(accuracy_score(y, pred)), "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)), "f1": float(f1_score(y, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, prob)), "pr_auc": float(average_precision_score(y, prob))}


def fairness_table(y, pred, regions):
    rows=[]
    for g in sorted(pd.Series(regions).dropna().unique()):
        m = np.asarray(regions) == g; yy=np.asarray(y)[m]; pp=np.asarray(pred)[m]
        rows.append({"region":g,"n":int(m.sum()),"actual_late_rate":float(yy.mean()),"predicted_positive_rate":float(pp.mean()),
            "tpr":float(((pp==1)&(yy==1)).sum()/max(1,(yy==1).sum())),
            "fpr":float(((pp==1)&(yy==0)).sum()/max(1,(yy==0).sum()))})
    df=pd.DataFrame(rows)
    df["predicted_rate_gap_vs_min"] = df.predicted_positive_rate - df.predicted_positive_rate.min()
    df.to_csv(OUT/"fairness_metrics.csv", index=False)
    summary={"regional_demographic_parity_difference":float(df.predicted_positive_rate.max()-df.predicted_positive_rate.min()),
        "regional_disparate_impact_ratio":float(df.predicted_positive_rate.min()/df.predicted_positive_rate.max()) if df.predicted_positive_rate.max() else None,
        "regional_equalized_odds_gap":float(max(df.tpr.max()-df.tpr.min(), df.fpr.max()-df.fpr.min())),
        "interpretation":"Operational-region diagnostic only; dataset contains no protected demographic attributes."}
    return df,summary


def main():
    import mlflow
    tracking_db=HERE/"mlflow.db"
    mlflow.set_tracking_uri(f"sqlite:///{tracking_db.as_posix()}")
    from mlflow.tracking import MlflowClient
    client=MlflowClient()
    exp=client.get_experiment_by_name("Olist Delivery Risk — Module 4")
    if exp is None:
        client.create_experiment("Olist Delivery Risk — Module 4",artifact_location=(HERE/"mlruns"/"olist_delivery_risk").as_uri())
    mlflow.set_experiment("Olist Delivery Risk — Module 4")
    run=mlflow.start_run(run_name="Olist model development and validation")
    mlflow.log_params({"data_source":"Olist public historical dataset","split":"chronological 80/20","random_seed":42,"positive_class":"actual delivery after estimated date","feature_count":len(FEATURES)})
    data=load_model_table()
    if len(data)<5000: raise ValueError(f"Expected at least 5,000 eligible labeled rows; got {len(data)}")
    data=data.sort_values("order_purchase_timestamp").reset_index(drop=True)
    cut=int(len(data)*0.8); train=data.iloc[:cut].copy(); test=data.iloc[cut:].copy()
    Xtr=train[FEATURES]; ytr=train.late; Xte=test[FEATURES]; yte=test.late
    prep=make_preprocessor()
    baseline=DummyClassifier(strategy="most_frequent").fit(np.zeros((len(ytr),1)),ytr)
    baseline_pred=baseline.predict(np.zeros((len(yte),1))); baseline_prob=np.zeros(len(yte))
    models={"Logistic Regression":Pipeline([("prep",make_preprocessor()),("model",LogisticRegression(max_iter=1200,class_weight="balanced",random_state=42))]),
            "Random Forest":Pipeline([("prep",make_preprocessor()),("model",RandomForestClassifier(n_estimators=120,min_samples_leaf=12,max_features="sqrt",class_weight="balanced_subsample",n_jobs=1,random_state=42))])}
    # Train-only stratified cross-validation compares a small, declared logistic C grid.
    lr=GridSearchCV(models["Logistic Regression"],{"model__C":[0.3,1.0,3.0]},scoring="average_precision",cv=StratifiedKFold(3,shuffle=True,random_state=42),n_jobs=1,refit=True)
    lr.fit(Xtr,ytr); models["Logistic Regression"]=lr.best_estimator_
    models["Random Forest"].fit(Xtr,ytr)
    results={"rows_total":int(len(data)),"train_rows":int(len(train)),"test_rows":int(len(test)),
        "train_period_start":str(train.order_purchase_timestamp.min()),"train_period_end":str(train.order_purchase_timestamp.max()),
        "test_period_start":str(test.order_purchase_timestamp.min()),"test_period_end":str(test.order_purchase_timestamp.max()),
        "target_late_rate":float(data.late.mean()),"test_target_late_rate":float(yte.mean()),
        "baseline_majority":score(yte,baseline_pred,baseline_prob),"best_logistic_C":float(lr.best_params_["model__C"]),"models":{}}
    fitted={}
    for name,model in models.items():
        prob=model.predict_proba(Xte)[:,1]; pred=(prob>=0.5).astype(int)
        results["models"][name]=score(yte,pred,prob); fitted[name]=(model,prob,pred)
    # Select using training-only CV, never test performance.
    best_name="Logistic Regression"; best,prob,pred=fitted[best_name]
    results["selection_rule"]="Logistic Regression selected using training-only 3-fold CV average precision; later chronological hold-out is reserved for evaluation."
    results["selected_model"]=best_name; results["threshold"]=0.5
    results["confusion_matrix"] = confusion_matrix(yte,pred).tolist()
    # Broad region is an operational diagnostic and a model input, not a protected-class label.
    groups=data.iloc[cut:]["customer_region"].to_numpy()
    fair,fs=fairness_table(yte,pred,groups); results["fairness_summary"]=fs
    # Figures and model artifact.
    fig,ax=plt.subplots(figsize=(6,5)); RocCurveDisplay.from_predictions(yte,prob,ax=ax); ax.set_title(f"ROC Curve — {best_name}"); fig.tight_layout(); fig.savefig(PLOTS/"roc_curve.png",dpi=170); plt.close(fig)
    cm=np.asarray(results["confusion_matrix"]); fig,ax=plt.subplots(figsize=(5,4)); ax.imshow(cm,cmap="Blues"); ax.set(xticks=[0,1],yticks=[0,1],xlabel="Predicted",ylabel="Actual",title="Confusion Matrix at 0.50")
    for (i,j),v in np.ndenumerate(cm): ax.text(j,i,str(v),ha="center",va="center")
    fig.tight_layout(); fig.savefig(PLOTS/"confusion_matrix.png",dpi=170); plt.close(fig)
    joblib.dump(best,ART/"delivery_risk_model.joblib")
    # SHAP global and local explanation on a bounded test sample.
    transformed=best.named_steps["prep"].transform(Xte.iloc[:600])
    clf=best.named_steps["model"]
    feature_names=best.named_steps["prep"].get_feature_names_out()
    background=best.named_steps["prep"].transform(Xtr.iloc[:300])
    explainer=shap.LinearExplainer(clf,background)
    sv=explainer(transformed)
    positive=sv.values
    shap.summary_plot(positive,transformed,feature_names=feature_names,show=False,max_display=15)
    plt.title("SHAP Global Feature Effects"); plt.tight_layout(); plt.savefig(PLOTS/"shap_summary.png",dpi=170,bbox_inches="tight"); plt.close()
    # Local waterfall for the first test row; output values are in model score space.
    one=transformed[:1]
    exp=explainer(one)
    vals=exp.values
    base=exp.base_values
    local=shap.Explanation(values=np.asarray(vals)[0],base_values=float(np.asarray(base).reshape(-1)[0]),data=np.asarray(one.toarray() if hasattr(one,"toarray") else one)[0],feature_names=feature_names)
    shap.plots.waterfall(local,max_display=12,show=False); plt.tight_layout(); plt.savefig(PLOTS/"shap_local.png",dpi=170,bbox_inches="tight"); plt.close()
    # Scenario sensitivity: vary the checkout estimate only; descriptive, not an instruction to change a customer's order.
    sample=Xte.iloc[:200].copy(); sens=[]
    for delta in [-3,-1,0,1,3]:
        s=sample.copy(); s["estimated_lead_days"]=(s.estimated_lead_days+delta).clip(lower=0)
        sens.append({"lead_time_shift_days":delta,"mean_predicted_risk":float(best.predict_proba(s)[:,1].mean())})
    pd.DataFrame(sens).to_csv(OUT/"sensitivity_analysis.csv",index=False)
    # Threshold-based closest contrast for an example. The only varied field is a fixed checkout promise, so this is explanatory, not actionable recourse.
    example=Xte.iloc[[0]].copy(); initial=float(best.predict_proba(example)[0,1]); counter=None
    for d in np.arange(0.5,15.1,0.5):
        alt=example.copy(); alt["estimated_lead_days"]+=d
        p=float(best.predict_proba(alt)[0,1])
        if (initial>=0.5 and p<0.5) or (initial<0.5 and p>=0.5): counter={"initial_risk":initial,"changed_feature":"estimated_lead_days","scenario_change_days":float(d),"new_risk":p,"caveat":"Model contrast only; promised lead time is not customer recourse and causal effects are untested."}; break
    results["counterfactual_scenario"]=counter or {"initial_risk":initial,"result":"No threshold-crossing scenario found in tested range","caveat":"Perturbation is descriptive, not causal or actionable."}
    results["fairness_groups"]=fair.to_dict(orient="records")
    results["leakage_controls"]=["Prediction inputs are restricted to checkout-time basket, planned lead time, regions, category, and purchase calendar fields.","Actual delivery timestamp is used only to form the retrospective target.","Order/customer/seller identifiers, reviews, order status, and post-purchase fields are excluded.","Chronological hold-out: later 20% of eligible orders by purchase timestamp."]
    (OUT/"metrics.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    # The run began before data preparation/training so its timestamps reflect the actual experiment.
    mlflow.log_params({"selected_model":best_name,"threshold":0.5,"features":",".join(FEATURES),"cv_best_logistic_C":lr.best_params_["model__C"],"train_rows":len(train),"test_rows":len(test)})
    mlflow.log_metrics({f"{name}_{metric}":value for name,m in results["models"].items() for metric,value in m.items()})
    mlflow.log_metrics({f"fairness_{k}":v for k,v in fs.items() if isinstance(v,(int,float)) and v is not None})
    info=mlflow.sklearn.log_model(best,name="model",registered_model_name="OlistDeliveryRisk",skops_trusted_types=["numpy.dtype"])
    version=getattr(info,"registered_model_version",None)
    if version is not None:
        try:
            from mlflow.tracking import MlflowClient
            MlflowClient().transition_model_version_stage(name="OlistDeliveryRisk",version=str(version),stage="Staging",archive_existing_versions=True)
        except Exception as exc:
            warnings.warn(f"Registered the version but could not set Staging: {exc}")
    results["mlflow"]={"tracking_uri":"SQLite backend in module4/mlflow.db; artifacts in module4/mlruns","experiment":"Olist Delivery Risk — Module 4","run_id":run.info.run_id,"registered_model":"OlistDeliveryRisk","model_version":version,"stage":"Staging" if version is not None else "Not recorded"}
    (OUT/"metrics.json").write_text(json.dumps(results,indent=2),encoding="utf-8")
    mlflow.log_artifact(str(OUT/"metrics.json")); mlflow.log_artifact(str(OUT/"fairness_metrics.csv")); mlflow.log_artifacts(str(PLOTS),artifact_path="figures")
    mlflow.end_run()
    print(json.dumps({"rows":len(data),"model":best_name,"metrics":results["models"][best_name],"mlflow":results.get("mlflow")},indent=2))


def load_region_table():
    # The helper returns the matching target rows and broad operational region for subgroup reports.
    orders=pd.read_csv(RAW/"olist_orders_dataset.csv",usecols=["order_id","customer_id","order_status","order_purchase_timestamp","order_delivered_customer_date","order_estimated_delivery_date"])
    cust=pd.read_csv(RAW/"olist_customers_dataset.csv",usecols=["customer_id","customer_state"])
    orders=orders.drop_duplicates("order_id").merge(cust.drop_duplicates("customer_id"),on="customer_id",how="left")
    for c in ["order_purchase_timestamp","order_delivered_customer_date","order_estimated_delivery_date"]: orders[c]=pd.to_datetime(orders[c],errors="coerce",utc=True)
    orders=orders[orders.order_status.eq("delivered")&orders.order_delivered_customer_date.notna()&orders.order_estimated_delivery_date.notna()&orders.order_purchase_timestamp.notna()].copy()
    orders["customer_region"]=orders.customer_state.map(region).fillna("Unknown")
    return orders[["order_purchase_timestamp","customer_region"]]


if __name__=="__main__":
    main()
