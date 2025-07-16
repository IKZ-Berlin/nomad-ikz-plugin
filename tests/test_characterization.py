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
from nomad.client import normalize_all

log_levels = ['error', 'critical']


@pytest.mark.parametrize(
    'parsed_measurement_archive, caplog',
    [
        (file, log_levels)
        for file in glob.glob(
            os.path.join(
                os.path.dirname(__file__), 'data/characterization/transmission', '*.asc'
            )
        )
    ],
    indirect=True,
)
def test_uv_vis_transmission(parsed_measurement_archive, caplog):
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


@pytest.mark.parametrize(
    'parsed_measurement_archive, caplog',
    [
        (file, log_levels)
        for file in glob.glob(
            os.path.join(
                os.path.dirname(__file__), 'data/characterization/transmission', '*.0'
            )
        )
    ],
    indirect=True,
)
def test_ir_transmission(parsed_measurement_archive, caplog):
    """
    Tests the normalization of the parsed archive.

    Args:
        parsed_archive (pytest.fixture): Fixture to handle the parsing of archive.
        caplog (pytest.fixture): Fixture to capture errors from the logger.
    """
    normalize_all(parsed_measurement_archive)
    assert parsed_measurement_archive.metadata.entry_type == 'ELNIRTransmission'
    assert parsed_measurement_archive.data.results[0].wavelength is not None
    assert len(parsed_measurement_archive.data.figures) > 0
