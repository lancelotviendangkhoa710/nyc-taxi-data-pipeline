import os

import spark.config as config


def test_setup_java_env_preserves_container_java_home(monkeypatch) -> None:
    monkeypatch.setattr(config, "IS_WINDOWS", False)
    monkeypatch.setenv("JAVA_HOME", "/usr/lib/jvm/java-17-openjdk-amd64")
    monkeypatch.delenv("HADOOP_HOME", raising=False)

    config.setup_java_env()

    assert os.environ["JAVA_HOME"] == "/usr/lib/jvm/java-17-openjdk-amd64"
    assert "HADOOP_HOME" not in os.environ
