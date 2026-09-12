import joblib
import pandas as pd


class SafeYatraRiskModel:
    def __init__(self, model_path="./mlmodel/safeyatra_risk_model.joblib"):
        bundle = joblib.load(model_path)

        self.rf_model = bundle["rf_model"]
        self.weights = bundle["weights"]
        self.norm_stats = bundle["norm_stats"]
        self.features = bundle["features"]
        self.label_map = bundle["label_map"]

        self.district_lookup = bundle["district_lookup"].copy()

        self.district_lookup["_key"] = (
            self.district_lookup["district_name"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    def _get_row(self, district_name, state_name=None):
        key = district_name.strip().lower()

        matches = self.district_lookup[
            self.district_lookup["_key"] == key
        ]

        if state_name is not None:
            matches = matches[
                matches["state_name"]
                .astype(str)
                .str.strip()
                .str.lower()
                == state_name.strip().lower()
            ]

        if matches.empty:
            raise ValueError(
                f"No district found matching '{district_name}'"
                + (
                    f" in state '{state_name}'"
                    if state_name
                    else ""
                )
            )

        if len(matches) > 1:
            options = ", ".join(
                f"{r.district_name} ({r.state_name})"
                for r in matches.itertuples()
            )

            raise ValueError(
                f"Multiple districts named '{district_name}' found: "
                f"{options}. Pass state_name to disambiguate."
            )

        return matches.iloc[0]

    def _risk_score(self, row):
        score = 0.0

        for rate_col, weight in self.weights.items():
            cmin = self.norm_stats[rate_col]["min"]
            cmax = self.norm_stats[rate_col]["max"]

            norm_val = (
                (row[rate_col] - cmin)
                / (cmax - cmin + 1e-9)
            )

            score += norm_val * weight

        return float(score)

    def predict(self, district_name, state_name=None):
        row = self._get_row(district_name, state_name)

        risk_score = self._risk_score(row)

        feature_vec = pd.DataFrame(
            [row[self.features].astype(float)]
        )

        pred_idx = int(
            self.rf_model.predict(feature_vec)[0]
        )

        risk_label = self.label_map[pred_idx]

        return {
            "district_name": row["district_name"],
            "state_name": row["state_name"],
            "safety_score": round(100 - (risk_score * 100), 2),
            "risk_label": risk_label,
        }