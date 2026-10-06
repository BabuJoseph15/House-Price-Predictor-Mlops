import joblib
import pandas as pd


class PredictionPipeline:

    def __init__(self):
        self.model = joblib.load(
            "artifacts/model.pkl"
        )

        self.preprocessor = joblib.load(
            "artifacts/preprocessor.pkl"
        )

    def predict(self, data):

        transformed_data = self.preprocessor.transform(
            data
        )

        prediction = self.model.predict(
            transformed_data
        )

        return prediction


if __name__ == "__main__":

    sample_data = pd.DataFrame([
        {
            "longitude": -122.23,
            "latitude": 37.88,
            "housing_median_age": 41,
            "total_rooms": 880,
            "total_bedrooms": 129,
            "population": 322,
            "households": 126,
            "median_income": 8.3252,
            "ocean_proximity": "NEAR BAY"
        }
    ])

    predictor = PredictionPipeline()

    result = predictor.predict(sample_data)

    print(
         f"Predicted House Price: ${result[0\\]:,.2f}"   
    )
