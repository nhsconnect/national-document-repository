import pytest
from services.lloyd_george_stitch_job_service import LloydGeorgeStitchJobService


@pytest.fixture
def stitch_service(set_env):
    yield LloydGeorgeStitchJobService()
