import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
import json
import joblib
import os
from dotenv import load_dotenv

load_dotenv()
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, classification_report

EVAL_THRESHOLD = 0.70


def train(
    params: dict,
    data_path: str = "data/train_phase1.csv",
    eval_path: str = "data/eval.csv",
) -> float:
    # TODO 1: Đọc dữ liệu
    df_train = pd.read_csv(data_path)
    df_eval = pd.read_csv(eval_path)

    # TODO 2: Tách đặc trưng và nhãn
    X_train = df_train.drop(columns=["target"])
    y_train = df_train["target"]
    X_eval = df_eval.drop(columns=["target"])
    y_eval = df_eval["target"]

    # Bonus 5: Cảnh báo lệch lạc dữ liệu
    distribution = y_train.value_counts(normalize=True).to_dict()
    print("Label distribution in training set:")
    for label, ratio in distribution.items():
        print(f"  Class {label}: {ratio:.2%}")
        if ratio < 0.10:
            print(f"  WARNING: Class {label} is underrepresented (< 10%)!")

    # Bonus 2: Thí nghiệm với nhiều thuật toán
    model_type = params.pop("model_type", "random_forest")
    
    if model_type == "random_forest":
        model = RandomForestClassifier(**params, random_state=42)
    elif model_type == "gradient_boosting":
        model = GradientBoostingClassifier(**params, random_state=42)
    elif model_type == "logistic_regression":
        model = LogisticRegression(**params, random_state=42, max_iter=1000)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    with mlflow.start_run():
        # TODO 3: Log params
        mlflow.log_param("model_type", model_type)
        mlflow.log_params(params)

        # TODO 4: Khởi tạo và train
        model.fit(X_train, y_train)

        # TODO 5: Đánh giá
        preds = model.predict(X_eval)
        acc = accuracy_score(y_eval, preds)
        f1 = f1_score(y_eval, preds, average="weighted")
        
        # Bonus 3: Thêm precision và recall
        precision = precision_score(y_eval, preds, average="weighted")
        recall = recall_score(y_eval, preds, average="weighted")

        # TODO 6: Log metrics
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.sklearn.log_model(model, "model")

        # TODO 7: In kết quả
        print(f"Model: {model_type}")
        print(f"Accuracy: {acc:.4f} | F1: {f1:.4f}")

        # TODO 8: Lưu metrics.json (Bonus 5: Ghi tỷ lệ phân phối nhãn)
        os.makedirs("outputs", exist_ok=True)
        metrics_data = {
            "accuracy": acc, 
            "f1_score": f1,
            "precision": precision,
            "recall": recall,
            "label_distribution": {str(k): float(v) for k, v in distribution.items()}
        }
        with open("outputs/metrics.json", "w") as f:
            json.dump(metrics_data, f, indent=4)

        # Bonus 3: Báo cáo hiệu suất tự động (report.txt)
        cm = confusion_matrix(y_eval, preds)
        cls_report = classification_report(y_eval, preds)
        with open("outputs/report.txt", "w") as f:
            f.write(f"MODEL TYPE: {model_type}\n")
            f.write("-" * 30 + "\n")
            f.write("CONFUSION MATRIX:\n")
            f.write(np.array2string(cm) if hasattr(np, 'array2string') else str(cm))
            f.write("\n\nCLASSIFICATION REPORT:\n")
            f.write(cls_report)

        # TODO 9: Lưu model.pkl
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")

    # TODO 10: Trả về accuracy
    return acc


if __name__ == "__main__":
    import numpy as np # Needed for confusion matrix string formatting
    with open("params.yaml") as f:
        params = yaml.safe_load(f)
    train(params)