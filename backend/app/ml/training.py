from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from category_encoders import TargetEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.ml.artifact import save_model_artifact
from app.ml.constants import ALL_FEATURES, CATEGORICAL_COLS
from app.ml.feature_engineering import (
    build_poi_stats,
    build_region_stats,
    engineer_features,
    load_interactions,
)
from app.ml.tracking import log_training_run, maybe_start_training_run


def top_k_accuracy(model: Pipeline, features: pd.DataFrame, y_true: pd.Series, k: int) -> float:
    proba = model.predict_proba(features)
    classes = model.classes_
    top_k = np.argsort(proba, axis=1)[:, -k:]
    correct = 0
    for index, label in enumerate(y_true):
        class_indices = np.where(classes == label)[0]
        if class_indices.size and class_indices[0] in top_k[index]:
            correct += 1
    return correct / max(len(y_true), 1)


def train_recommender(
    *,
    interaction_data_path: Path,
    model_artifact_path: Path,
    sample_rows: int,
    top_n: int,
    candidate_pool_size: int,
) -> dict[str, Any]:
    training_params = {
        "interaction_data_path": str(interaction_data_path),
        "sample_rows": sample_rows,
        "top_n": top_n,
        "candidate_pool_size": candidate_pool_size,
        "categorical_cols": ",".join(CATEGORICAL_COLS),
        "all_features": ",".join(ALL_FEATURES),
        "test_size": 0.2,
        "random_state": 42,
        "n_estimators": 120,
        "max_depth": 20,
        "min_samples_leaf": 5,
        "encoder_min_samples_leaf": 20,
        "encoder_smoothing": 1.0,
    }

    with maybe_start_training_run(
        run_name="poi-recommender-training",
        tags={
            "dataset": interaction_data_path.name,
            "model_family": "random-forest-target-encoder",
        },
    ) as tracking_active:
        raw_df = load_interactions(interaction_data_path, sample_rows=sample_rows)
        df = engineer_features(raw_df)

        top_pois = df["poi_id"].value_counts().head(top_n).index.tolist()
        df_model = df[df["poi_id"].isin(top_pois)].copy()
        if df_model["poi_id"].nunique() < 2:
            raise ValueError("Not enough POI classes available to train the recommender.")

        features = df_model[ALL_FEATURES]
        target = df_model["poi_id"]

        x_train, x_test, y_train, y_test = train_test_split(
            features,
            target,
            test_size=0.2,
            random_state=42,
            stratify=target,
        )

        pipeline = Pipeline(
            steps=[
                (
                    "encoder",
                    TargetEncoder(
                        cols=CATEGORICAL_COLS,
                        smoothing=1.0,
                        min_samples_leaf=20,
                        handle_unknown="value",
                        handle_missing="value",
                    ),
                ),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=120,
                        max_depth=20,
                        min_samples_leaf=5,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        )
        pipeline.fit(x_train, y_train)

        y_pred = pipeline.predict(x_test)
        training_summary = {
            "sample_rows": int(len(df)),
            "training_rows": int(len(df_model)),
            "classes": int(df_model["poi_id"].nunique()),
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "top_3_accuracy": float(top_k_accuracy(pipeline, x_test, y_test, k=3)),
            "top_5_accuracy": float(top_k_accuracy(pipeline, x_test, y_test, k=5)),
        }

        artifact = {
            "model": pipeline,
            "all_features": ALL_FEATURES,
            "candidate_pool_size": candidate_pool_size,
            "training_summary": training_summary,
        }
        save_model_artifact(model_artifact_path, artifact)

        poi_stats_df = build_poi_stats(df, candidate_pool_size=candidate_pool_size)
        region_stats_df = build_region_stats(df)
        if tracking_active:
            log_training_run(
                model=pipeline,
                training_params=training_params,
                training_summary=training_summary,
                feature_sample=x_train,
                poi_stats_df=poi_stats_df,
                region_stats_df=region_stats_df,
                model_artifact_path=model_artifact_path,
            )

        return {
            "training_summary": training_summary,
            "poi_stats_rows": poi_stats_df.to_dict(orient="records"),
            "region_stats_rows": region_stats_df.to_dict(orient="records"),
        }
