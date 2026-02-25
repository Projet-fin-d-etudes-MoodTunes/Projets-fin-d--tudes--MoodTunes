from database import get_db
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib


FEATURE_COLUMNS = [
    "energy",
    "valence",
    "danceability",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "tempo",
    "loudness"
]


def load_user_dataset(user_id):
    db = get_db()

    query = f"""
        SELECT 
            t.energy,
            t.valence,
            t.danceability,
            t.acousticness,
            t.instrumentalness,
            t.speechiness,
            t.tempo,
            t.loudness,
            h.liked
        FROM user_history h
        JOIN tracks t ON h.track_id = t.id
        WHERE h.user_id = ?
        AND t.energy >= 0
        AND t.valence >= 0
        AND t.danceability >= 0
        AND t.acousticness >= 0
        AND t.instrumentalness >= 0
        AND t.speechiness >= 0
        AND t.tempo >= 0
    """

    df = pd.read_sql_query(query, db, params=(user_id,))
    db.close()

    return df


def train_model_for_user(user_id):
    df = load_user_dataset(user_id)

    if len(df) < 20:
        print("⚠ Pas assez de données.")
        return None

    X = df[FEATURE_COLUMNS]
    y = df["liked"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Pipeline = scaling + modèle
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    print("\n=== Rapport de classification ===")
    print(classification_report(y_test, y_pred))

    model = pipeline.named_steps["model"]

    print("\n=== Coefficients du modèle ===")
    for feature, coef in zip(FEATURE_COLUMNS, model.coef_[0]):
        print(f"{feature}: {coef:.3f}")

    # Sauvegarder pipeline complet
    joblib.dump(pipeline, f"user_model_{user_id}.pkl")

    print(f"\n✅ Modèle sauvegardé pour utilisateur {user_id}")

    return pipeline


if __name__ == "__main__":
    USER_ID = 1
    train_model_for_user(USER_ID)
