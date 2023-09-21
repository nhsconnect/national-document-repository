import os

from utils.get_aws_region import get_aws_region


def test_get_aws_region_return_aws_region_in_env_var(mocker):
    mocker.patch.dict(os.environ, {"AWS_REGION": "test_aws_region"})

    expected = "test_aws_region"
    actual = get_aws_region()

    assert actual == expected


def test_get_aws_region_by_default_return_eu_west_2(mocker):
    mocker.patch.dict(os.environ, {})

    expected = "eu-west-2"
    actual = get_aws_region()

    assert actual == expected
