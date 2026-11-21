import math
import joblib
import pandas as pd
from pathlib import Path
from datetime import date

class SafeYatraTemperatureModel:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = (
                Path(__file__).resolve().parents[1]
                / "mlmodel"
                / "temperature_model.joblib"
            )
        bundle = joblib.load(model_path)
        self.model = bundle["model"]
        self.feature_names = bundle["feature_names"]
        self.preprocessing = bundle["preprocessing"]
        self.risk = bundle["risk"]
        print("SafeYatra Temperature Model Loaded")
        print("Model:", bundle["model_type"])
        print("Features:", len(self.feature_names))
    def nearest_grid(self, latitude, longitude):
        grid_lat = math.floor(latitude + 0.5)
        grid_lon = math.floor(longitude + 0.5)
        return grid_lat, grid_lon
    def calculate_trend(self, temperatures):
        values = temperatures[-7:]
        if len(values) != 7:
            raise ValueError("7 days required for trend.")
        mean_y = sum(values) / 7
        mean_x = 3
        numerator = sum(
            (i - mean_x) * (values[i] - mean_y)
            for i in range(7)
        )
        denominator = sum(
            (i - mean_x) ** 2
            for i in range(7)
        )
        return numerator / denominator
    def build_features(self,latitude,longitude,target_date,temperatures):
        if len(temperatures) != 30:
            raise ValueError(
                "Exactly 30 consecutive temperature values required."
            )
        grid_lat, grid_lon = self.nearest_grid(
            latitude,
            longitude
        )
        features = {
            "latitude": grid_lat,
            "longitude": grid_lon,
            "month": target_date.month,
            "day_of_year": target_date.timetuple().tm_yday,
            "temp_lag_1": temperatures[-1],
            "temp_lag_2": temperatures[-2],
            "temp_lag_3": temperatures[-3],
            "temp_lag_7": temperatures[-7],
            "temp_lag_14": temperatures[-14],
            "temp_lag_30": temperatures[-30],
            "roll_mean_3": sum(temperatures[-3:]) / 3,
            "roll_mean_7": sum(temperatures[-7:]) / 7,
            "roll_mean_14": sum(temperatures[-14:]) / 14,
            "roll_mean_30": sum(temperatures[-30:]) / 30,
            "trend_7d_slope": self.calculate_trend(temperatures)
        }
        feature_df = pd.DataFrame(
            [[features[name] for name in self.feature_names]],
            columns=self.feature_names,
            dtype="float32"
        )
        return feature_df, grid_lat, grid_lon
    def predict(self,latitude,longitude,target_date,temperatures):
        feature_df, grid_lat, grid_lon = self.build_features(
            latitude,
            longitude,
            target_date,
            temperatures
        )
        predicted_temp = float(
            self.model.predict(feature_df)[0]
        )
        if not math.isfinite(predicted_temp):
            raise ValueError("Invalid model prediction.")
        thresholds = self.risk["thresholds_c"]
        labels = self.risk["labels"]
        if predicted_temp < thresholds[0]:
            risk_label = labels[0]
        elif predicted_temp < thresholds[1]:
            risk_label = labels[1]
        elif predicted_temp < thresholds[2]:
            risk_label = labels[2]
        else:
            risk_label = labels[3]
        score_config = self.risk["score"]
        base = score_config["base_c"]
        per_degree = score_config["per_c"]
        risk_score = math.floor(
            max(
                0,
                min(
                    100,
                    (predicted_temp - base) * per_degree
                )
            )
        )
        margin = self.risk.get(
            "near_threshold_margin_c", 0
        )
        near_threshold = any(
            abs(predicted_temp - threshold) <= margin
            for threshold in thresholds
        )
        return {
            "predicted_max_temperature": round(
                predicted_temp, 2
            ),
            "risk_label": risk_label,
            "risk_score": risk_score,
            "near_threshold": near_threshold,
            "grid_latitude": grid_lat,
            "grid_longitude": grid_lon
        }