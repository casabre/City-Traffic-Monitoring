from pathlib import Path

from dagster import config_from_files, job
from dagster_celery import celery_executor

from ..ops.a_weigthing import a_weighting
from ..ops.extract_senml import extract_senml

job_config_yaml_path = (
    Path(__file__).parent / ".." / "data" / "extract_audio_execution.yaml"
)


@job(
    name="extract_audio_meta_information",
    # executor_def=celery_executor,
    # config=config_from_files([str(job_config_yaml_path)]),
)
def extract_audio():
    extracted = extract_senml()
    signals, fs = extracted
    a_weighted = a_weighting(signals, fs)