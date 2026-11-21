import joblib
import pandas as pd

class SafeYatraTemperatureModel:
    def __init__(self,model_path="./mlmodel/temperature_model.joblib"):
        self.model = joblib.load(model_path)
        
    def predict(self, temperature):
        feature_vec = pd.DataFrame(
            [[float(temperature)]],
            columns=["temperature"]
        )
        pred = self.model.predict(feature_vec)[0]
        risk_label = str(pred)

        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(feature_vec)[0]
            risk_score = round(float(max(probabilities)) * 100, 2)
        else:
            risk_score = None

        return {
            "predicted_max_temperature": float(temperature),
            "risk_label": risk_label,
            "risk_score": risk_score
        }
