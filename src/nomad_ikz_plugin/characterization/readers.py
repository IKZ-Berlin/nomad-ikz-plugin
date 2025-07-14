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
from typing import TYPE_CHECKING, Any

from brukeropus import read_opus

if TYPE_CHECKING:
    from structlog.stdlib import (
        BoundLogger,
    )


def reader_ir_brucker(file_path: str, logger: 'BoundLogger' = None) -> dict[str, Any]:
    """
    Function for reading the IR transmission data from Bruker *.0.

    Args:
        file_path (str): The path to the transmission data file.
        logger (BoundLogger, optional): A structlog logger. Defaults to None.

    Returns:
        Dict[str, Any]: The transmission data and metadata in a Python dictionary.
    """
    if not file_path.endswith('.0'):
        if logger:
            logger.error(f'Unsupported file format: {file_path}')
            return
        else:
            raise ValueError(f'Unsupported file format: {file_path}')

    opus_file = read_opus(file_path)

    output = {}

    output['measured_wavelength'] = opus_file.a.x
    output['measured_ordinate'] = opus_file.a.y

    # TODO: get the required metadata from the OPUS file parameters
    # opus_file.print_parameters()

    return output
