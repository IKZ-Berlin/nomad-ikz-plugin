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
from collections import defaultdict
from typing import TYPE_CHECKING, Any

from brukeropus import read_opus
from nomad.units import ureg

if TYPE_CHECKING:
    from structlog.stdlib import (
        BoundLogger,
    )


def reader_ir_brucker(
    file_path: str, logger: 'BoundLogger' = None
) -> dict[str, Any] | None:
    """
    Function for reading the IR transmission data from Bruker `*.0` OPUS files.

    Args:
        file_path (str): The path to the transmission data file.
        logger (BoundLogger, optional): A structlog logger. Defaults to None.

    Returns:
        dict[str, Any] | None: The transmission data and metadata in a Python
            dictionary.
    """
    if not file_path.endswith('.0'):
        if logger:
            logger.error(f'Unsupported file format: {file_path}')
            return
        else:
            raise ValueError(f'Unsupported file format: {file_path}')

    opus_file = read_opus(file_path)

    output = defaultdict(lambda: None)

    try:
        # measurment data
        for data in opus_file.iter_data():
            # picks Absorbance (first priority) or Transmittance data
            if data.label not in ['Absorbance', 'Transmittance']:
                continue
            output['ordinate_type'] = data.label
            output['measured_ordinate'] = data.y * ureg('dimensionless')
            if data.dxu == 'WN':
                output['measured_wavelength'] = ((1 / data.x) * ureg('cm')).to('m')
            elif data.dxu == 'WL':
                output['measured_wavelength'] = (data.x * ureg('micrometer')).to('m')
            else:
                raise ValueError(f'Unsupported wavelength unit: {data.dxu}')
            output['start_datetime'] = data.params.datetime
            break

        # instrument metadata
        output['instrument_name'] = opus_file.params.ins
        output['instrument_serial_number'] = opus_file.params.srn
        output['instrument_firmware_version'] = opus_file.params.vsn

        # sample parameters
        output['sample_id'] = opus_file.params.snm
        output['analyst_name'] = opus_file.params.cnm
        output['experiment_name'] = opus_file.params.exp
        output['experiment_folder_path'] = opus_file.params.xpp

        # optical parameters
        output['aperture_setting'] = ureg(opus_file.params.apt)
        output['beamsplitter_setting'] = opus_file.params.bms
        output['measurement_channel'] = opus_file.params.chn
        output['detector_setting'] = opus_file.params.dtc
        output['high_pass_filter'] = opus_file.params.hpf
        output['low_pass_filter'] = opus_file.params.lpf
        output['variable_low_pass_filter'] = opus_file.params.lpv * ureg('cm^-1')
        output['optical_filter_setting'] = opus_file.params.opf
        output['preamplifier_gain'] = ureg(opus_file.params.pgn) * ureg('dimensionless')
        output['source_setting'] = opus_file.params.src
        output['scanner_velocity'] = opus_file.params.vel

        # aquisition settings
        output['acquisition_mode'] = opus_file.params.aqm
        output['wanted_high_frequency_limit'] = opus_file.params.hfw
        output['wanted_low_frequency_limit'] = opus_file.params.lfw
        output['sample_scans'] = opus_file.params.nss
        output['result_spectrum'] = opus_file.params.plf
        output['resolution'] = opus_file.params.res

        return output

    except Exception as e:
        if logger:
            logger.error(f'Error reading file {file_path}: {e}')
        else:
            raise ValueError(f'Error reading file {file_path}: {e}') from e
