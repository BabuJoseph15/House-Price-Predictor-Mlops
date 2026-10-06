import pandas as pd
from sklearn.model_selection import train_test_split
import os

class DataIngestion:

    def initiate_data_ingestion(self):
        df = pd.read_csv("data/housing.csv")

        os.makedirs("artifacts", exist_ok=True)

        train_set, test_set = train_test_split(
            df,
            test_size=0.2,
            random_state=42
        )

        train_set.to_csv("artifacts/train.csv", index=False)
        test_set.to_csv("artifacts/test.csv", index=False)

        print("Data ingestion completed")

if __name__ == "__main__":
    obj = DataIngestion()
    obj.initiate_data_ingestion()
