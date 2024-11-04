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
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.parsing import MatchingParser
from nomad.units import ureg
from nomad_material_processing.utils import create_archive

from ikz_plugin.directional_solidification.schema import (
    DirectionalSolidificationExperiment,
    HeaterAcCurrent,
    HeaterCoil,
    HeaterDcCurrent,
    HeaterFrequency,
    HeaterParameters,
    HeaterPhase,
    HeaterPower,
    HeaterTemperature,
    ManualProtocol,
    ManualProtocols,
)
from ikz_plugin.utils import (
    create_archive,
)

timezone = 'Europe/Berlin'


def fill_datetime(date: pd.Series):
    date_array = []
    for i in date:
        date_array.append(
            datetime.strptime(
                i,
                '%Y-%m-%d %H:%M:%S',
            ).replace(tzinfo=ZoneInfo(timezone))
        )
    return date_array


class DSParserIKZ(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        data_file = mainfile.split('/')[-1]
        data_file_with_path = mainfile.split('raw/')[-1]
        xlsx = pd.ExcelFile(mainfile)
        xlsx_sheet = pd.read_excel(
            xlsx,
            'Sheet1',
            comment='#',
        )

        filetype = 'json'
        filename = f'{data_file[:-5]}.archive.{filetype}'

        archive.data = DirectionalSolidificationExperiment()
        archive.data.manual_protocol = ManualProtocols()

        dig_prot_data = ManualProtocol()
        dig_prot_data.heaters = []
        dig_prot_data.timestamp = []
        dig_prot_data.temperature_1_2 = HeaterTemperature()
        dig_prot_data.temperature_1_3 = HeaterTemperature()
        dig_prot_data.temperature_1_4 = HeaterTemperature()
        dig_prot_data.temperature_pyrometer = HeaterTemperature()
        dig_prot_data.temperature_tp = HeaterTemperature()

        dig_prot_data.timestamp = fill_datetime(xlsx_sheet['Ending time'])
        starting_time = datetime.strptime(
            xlsx_sheet['Ending time'][0],
            '%Y-%m-%d %H:%M:%S',
        ).replace(tzinfo=ZoneInfo(timezone))
        elapsed_time = [
            (dt - starting_time).total_seconds() for dt in dig_prot_data.timestamp
        ]

        dig_prot_data.temperature_1_2.value = ureg.Quantity(
            xlsx_sheet['T12'].to_numpy(),
            ureg('K'),
        )
        dig_prot_data.temperature_1_2.time = ureg.Quantity(
            elapsed_time,
            ureg('s'),
        )
        dig_prot_data.temperature_1_3.value = ureg.Quantity(
            xlsx_sheet['T13'].to_numpy(),
            ureg('K'),
        )
        dig_prot_data.temperature_1_3.time = ureg.Quantity(
            elapsed_time,
            ureg('s'),
        )
        dig_prot_data.temperature_1_4.value = ureg.Quantity(
            xlsx_sheet['T14'].to_numpy(),
            ureg('K'),
        )
        dig_prot_data.temperature_1_4.time = ureg.Quantity(
            elapsed_time,
            ureg('s'),
        )
        dig_prot_data.temperature_pyrometer.value = ureg.Quantity(
            xlsx_sheet['Tpyr'].to_numpy(),
            ureg('K'),
        )
        dig_prot_data.temperature_pyrometer.time = ureg.Quantity(
            elapsed_time,
            ureg('s'),
        )
        dig_prot_data.temperature_tp.value = ureg.Quantity(
            xlsx_sheet['Ttp'].to_numpy(),
            ureg('K'),
        )
        dig_prot_data.temperature_tp.time = ureg.Quantity(
            elapsed_time,
            ureg('s'),
        )

        heater_number = 9
        for heater in range(heater_number):
            dig_prot_data.heaters.append(HeaterParameters())
            dig_prot_data.heaters[heater].name = f'heater {heater + 1}'
            dig_prot_data.heaters[heater].f1 = HeaterCoil()
            dig_prot_data.heaters[heater].f2 = HeaterCoil()
            dig_prot_data.heaters[heater].dc_current = HeaterDcCurrent()
            dig_prot_data.heaters[heater].power = HeaterPower()
            dig_prot_data.heaters[heater].temperature = HeaterTemperature()
            dig_prot_data.heaters[heater].f1.ac_current = HeaterAcCurrent()
            dig_prot_data.heaters[heater].f1.phase = HeaterPhase()
            dig_prot_data.heaters[heater].f1.frequency = HeaterFrequency()
            dig_prot_data.heaters[heater].f2.ac_current = HeaterAcCurrent()
            dig_prot_data.heaters[heater].f2.phase = HeaterPhase()
            dig_prot_data.heaters[heater].f2.frequency = HeaterFrequency()

            dig_prot_data.heaters[heater].f1.phase.value = ureg.Quantity(
                xlsx_sheet[f'phi{heater +1}_F1'].to_numpy(),
                ureg('deg'),
            )
            dig_prot_data.heaters[heater].f1.phase.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].f2.phase.value = ureg.Quantity(
                xlsx_sheet[f'phi{heater +1}_F2'].to_numpy(),
                ureg('deg'),
            )
            dig_prot_data.heaters[heater].f2.phase.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].f1.frequency.value = ureg.Quantity(
                xlsx_sheet[f'f{heater +1}_F1'].to_numpy(),
                ureg('Hz'),
            )
            dig_prot_data.heaters[heater].f1.frequency.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].f2.frequency.value = ureg.Quantity(
                xlsx_sheet[f'f{heater +1}_F2'].to_numpy(),
                ureg('Hz'),
            )
            dig_prot_data.heaters[heater].f2.frequency.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].f1.ac_current.value = ureg.Quantity(
                xlsx_sheet[f'Iac{heater +1}_F1'].to_numpy(),
                ureg('A'),
            )
            dig_prot_data.heaters[heater].f1.ac_current.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].f2.ac_current.value = ureg.Quantity(
                xlsx_sheet[f'Iac{heater +1}_F2'].to_numpy(),
                ureg('A'),
            )
            dig_prot_data.heaters[heater].f2.ac_current.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].dc_current.value = ureg.Quantity(
                xlsx_sheet[f'Iges{heater +1}'].to_numpy(),
                ureg('A'),
            )
            dig_prot_data.heaters[heater].dc_current.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].temperature.value = ureg.Quantity(
                xlsx_sheet[f'Iges{heater +1}'].to_numpy(),
                ureg('K'),
            )
            dig_prot_data.heaters[heater].temperature.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].power.value = ureg.Quantity(
                xlsx_sheet[f'P{heater +1}'].to_numpy(),
                ureg('W'),
            )
            dig_prot_data.heaters[heater].power.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )

            # dig_prot_data.heaters[heater].f1.ac_current.time =
            # dig_prot_data.heaters[heater].f1.dc_current.value = xlsx_sheet[f"DC Current H{heater} ValueY"]
            # dig_prot_data.heaters[heater].f1.phase.value = xlsx_sheet[f"Phase H{heater} ValueY"]
            # dig_prot_data.heaters[heater].f1.frequency.value = xlsx_sheet[f"Frequency H{heater} ValueY"]
            # dig_prot_data.heaters[heater].power.value = xlsx_sheet[f"Power H{heater} ValueY"]
            # dig_prot_data.heaters[heater].temperature.value = xlsx_sheet[f"Temperature H{heater} ValueY"]

        dig_prot_archive = EntryArchive(
            data=dig_prot_data,
            # m_context=archive.m_context,
            metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
        )
        create_archive(
            dig_prot_archive.m_to_dict(),
            archive.m_context,
            filename,
            filetype,
            logger,
        )

        # df_csv = pd.read_csv(
        #     file.name, decimal=',', comment='#' #, sep=';',  engine='python'
        # )
        # # Create a pandas Series with datetime data
        # df_csv['T Ist H1 Time'] = pd.to_datetime(df_csv['T Ist H1 Time'])
        # # Access the datetime properties (dt)
        # df_csv['T Ist H1 Time'] = df_csv['T Ist H1 Time'].dt.tz_localize(
        #     tz='cet'
        # )
        # for i in df_csv:
        #     if 'Time' in i and 'T Ist H1 Time' not in i:
        #         del df_csv[i]
        # for i in df_csv:
        #     if '/' in i:
        #         new_i = i.replace('/', ' ')
        #         df_csv[new_i] = df_csv[i]
        #         del df_csv[i]
        # if hasattr(self, 'timestamp'):
        #     setattr(self, 'timestamp', df_csv['T Ist H1 Time'])
        # if hasattr(self, 't_ist_h1'):
        #     setattr(self, 't_ist_h1', df_csv['T Ist H1 ValueY'])
        # if hasattr(self, 't_ist_h2'):
        #     setattr(self, 't_ist_h2', df_csv['T Ist H2 ValueY'])
        # if hasattr(self, 't_ist_h3'):
        #     setattr(self, 't_ist_h3', df_csv['T Ist H3 ValueY'])
        # if hasattr(self, 't_ist_h4'):
        #     setattr(self, 't_ist_h4', df_csv['T Ist H4 ValueY'])
        # if hasattr(self, 't_ist_h5'):
        #     setattr(self, 't_ist_h5', df_csv['T Ist H5 ValueY'])
        # if hasattr(self, 't_ist_h6'):
        #     setattr(self, 't_ist_h6', df_csv['T Ist H6 ValueY'])
        # if hasattr(self, 't_ist_h7'):
        #     setattr(self, 't_ist_h7', df_csv['T Ist H7 ValueY'])
        # if hasattr(self, 't_ist_h8'):
        #     setattr(self, 't_ist_h8', df_csv['T Ist H8 ValueY'])
        # if hasattr(self, 't_ist_h9'):
        #     setattr(self, 't_ist_h9', df_csv['T Ist H9 ValueY'])
