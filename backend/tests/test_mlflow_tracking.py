from app.ml.tracking import _update_registered_model_aliases


class _RunData:
    def __init__(self, accuracy):
        self.metrics = {"accuracy": accuracy}


class _Run:
    def __init__(self, accuracy):
        self.data = _RunData(accuracy)


class _Version:
    def __init__(self, version, run_id):
        self.version = version
        self.run_id = run_id


class FakeClient:
    def __init__(self, champion_accuracy=None):
        self.alias_updates = []
        self.champion_accuracy = champion_accuracy

    def set_registered_model_alias(self, *, name, alias, version):
        self.alias_updates.append((name, alias, str(version)))

    def get_model_version_by_alias(self, *, name, alias):
        if self.champion_accuracy is None:
            raise RuntimeError("alias missing")
        return _Version(version="2", run_id="old-run")

    def get_run(self, run_id):
        assert run_id == "old-run"
        return _Run(self.champion_accuracy)


def test_registry_aliases_promote_new_champion_when_accuracy_improves():
    client = FakeClient(champion_accuracy=0.81)

    _update_registered_model_aliases(
        client=client,
        registered_model_name="poi_recommender",
        model_version="3",
        training_summary={"accuracy": 0.92},
        champion_alias="champion",
        latest_alias="candidate",
    )

    assert client.alias_updates == [
        ("poi_recommender", "candidate", "3"),
        ("poi_recommender", "champion", "3"),
    ]


def test_registry_aliases_keep_existing_champion_when_accuracy_drops():
    client = FakeClient(champion_accuracy=0.95)

    _update_registered_model_aliases(
        client=client,
        registered_model_name="poi_recommender",
        model_version="4",
        training_summary={"accuracy": 0.87},
        champion_alias="champion",
        latest_alias="candidate",
    )

    assert client.alias_updates == [
        ("poi_recommender", "candidate", "4"),
    ]
