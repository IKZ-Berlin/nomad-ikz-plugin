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
test_files = glob.glob(
    os.path.join(
        os.path.dirname(__file__),
        'data/deprecated/characterization/setup_aliases.archive.json',
    )
)


@pytest.mark.parametrize(
    'parsed_json_archive, caplog',
    [(file, log_level) for file in test_files for log_level in log_levels],
    indirect=True,
)
def test_patch_for_activating_aliases(parsed_json_archive, caplog):
    """
    A patch for activating aliases. NOMAD parser only matches the aliases used in
    `m_def` as long as the given schema package is previously loaded with the original
    paths.

    Args:
        parsed_json_archive (pytest.fixture): Fixture to setup the archive.
    """
    normalize_all(parsed_json_archive)


test_files = glob.glob(
    os.path.join(
        os.path.dirname(__file__),
        'data/deprecated/characterization',
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
    Tests the backcompatibility of the normalizer.

    Args:
        parsed_measurement_archive (pytest.fixture): Fixture to setup the archive.
    """
    normalize_all(parsed_json_archive)
