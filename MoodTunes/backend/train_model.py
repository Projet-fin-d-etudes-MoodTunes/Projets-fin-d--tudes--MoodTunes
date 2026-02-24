from database import get_db
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
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
    """

    df = pd.read_sql_query(query, db, params=(user_id,))
    db.close()

    return df


def train_model_for_user(user_id):
    df = load_user_dataset(user_id)

    if len(df) < 20:
        print("⚠ Pas assez de données pour entraîner un modèle.")
        return None

    X = df[FEATURE_COLUMNS]
    y = df["liked"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\n=== Rapport de classification ===")
    print(classification_report(y_test, y_pred))

    # Sauvegarder modèle
    joblib.dump(model, f"user_model_{user_id}.pkl")

    print(f"\n✅ Modèle sauvegardé pour utilisateur {user_id}")

    return model


if __name__ == "__main__":
    USER_ID = 1
    train_model_for_user(USER_ID)
