from database import get_db
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import matplotlib.pyplot as plt
import numpy as np
import os

# Colonnes utilisees pour l'entrainement et le scoring ML
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

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Chargement des données dans le dataset associé à l'utilisateur
# On sélectionne le user history pour les intéractions


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

# Utilisation du LogisticRegression pour entrainer le ML modèle


def train_model_for_user(user_id):
    # Charger les likes/dislikes du user
    df = load_user_dataset(user_id)

    # On n'entraine pas le modele ML si il n'y a pas 20 intéractions
    if len(df) < 20:
        print("⚠ Pas assez de données.")
        return None

    # X = features audio
    # y = cible like/dislike
    X = df[FEATURE_COLUMNS]
    y = df["liked"]

    # Split train/test pour mesurer rapidement la qualite (20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Normalise sur la même base les audio features pour qu'elles soient comparables
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=1000, class_weight="balanced", C=0.5))
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
    # On sauvegarde scaler + modele pour pouvoir faire des prédiction
    model_path = os.path.join(MODEL_DIR, f"user_model_{user_id}.pkl")
    joblib.dump(pipeline, model_path)

    print(f"\n✅ Modèle sauvegardé pour utilisateur {user_id}")

    # Visualisation graphique

    # coefficients = model.coef_[0]
    # features = FEATURE_COLUMNS

    # # Graphique 1 — direction + importance
    # plt.figure(figsize=(10, 6))
    # plt.barh(features, coefficients)
    # plt.axvline(0)
    # plt.title("Importance des Audio Features (direction)")
    # plt.xlabel("Coefficient (influence sur le like)")
    # plt.tight_layout()
    # plt.show()

    # # Graphique 2 — magnitude seulement
    # plt.figure(figsize=(10, 6))
    # plt.barh(features, np.abs(coefficients))
    # plt.title("Magnitude des influences (valeur absolue)")
    # plt.xlabel("Force de l'influence")
    # plt.tight_layout()
    # plt.show()

    return pipeline


if __name__ == "__main__":
    USER_ID = 1  # En phaase de teste quand je lance le script manuellement ca va le faire pour le user 1, sinon le route dans app.py envoie le user id
    train_model_for_user(USER_ID)
