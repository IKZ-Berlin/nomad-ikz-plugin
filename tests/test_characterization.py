#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import glob
import os

import pytest
from nomad.client import normalize_all, parse

test_files = glob.glob(
    os.path.join(
        os.path.dirname(__file__), 'data/characterization/transmission', '*.asc'
    )
)
log_levels = ['error', 'critical']


@pytest.mark.parametrize(
    'parsed_measurement_archive, caplog',
    [(file, log_level) for file in test_files for log_level in log_levels],
    indirect=True,
)
def test_normalize_all(parsed_measurement_archive, caplog):
    """
    Tests the normalization of the parsed archive.

    Args:
        parsed_archive (pytest.fixture): Fixture to handle the parsing of archive.
        caplog (pytest.fixture): Fixture to capture errors from the logger.
    """
    normalize_all(parsed_measurement_archive)
    assert (
        parsed_measurement_archive.metadata.entry_type == 'IKZELNUVVisNirTransmission'
    )


test_files = glob.glob(
    os.path.join(
        os.path.dirname(__file__),
        'data/characterization/transmission/backcompatibility',
        '*.archive.json',
    )
)


@pytest.mark.parametrize(
    'parsed_json_archive, caplog',
    [(file, log_level) for file in test_files for log_level in log_levels],
    indirect=True,
)
def test_backcompatibility(parsed_json_archive, caplog):
    """
    Tests the backcompatibility of the parser.

    Args:
        parsed_measurement_archive (pytest.fixture): Fixture to setup the archive.
    """
    normalize_all(parsed_json_archive)
