from fastapi import FastAPI, HTTPException
from google.cloud import storage
import joblib
import os

app = FastAPI()

GCS_BUCKET = os.environ["GCS_BUCKET"]
GCS_MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")


def download_model():
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(GCS_MODEL_KEY)
    blob.download_to_filename(MODEL_PATH)
    print(f"Model downloaded to {MODEL_PATH}")


download_model()
model = joblib.load(MODEL_PATH)


class PredictRequest:
    features: list[float]

from pydantic import BaseModel

class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    if len(req.features) != 12:
        raise HTTPException(status_code=400, detail="Expected 12 features (wine quality)")
    pred = model.predict([req.features])[0]
    labels = {0: "thấp", 1: "trung_bình", 2: "cao"}
    return {"prediction": int(pred), "label": labels[int(pred)]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)