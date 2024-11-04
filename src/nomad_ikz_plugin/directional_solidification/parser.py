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
import io
from collections.abc import Iterable
from datetime import datetime
from typing import Union
from zoneinfo import ZoneInfo
import h5py

from nomad.datamodel.hdf5 import HDF5Reference

import pandas as pd
import numpy as np
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.parsing import MatchingParser
from nomad.units import ureg
from nomad_material_processing.utils import create_archive

from nomad_ikz_plugin.directional_solidification.schema import (
    DirectionalSolidificationExperiment,
    Trafo,
    HeaterCoil,
    HeaterAcCurrent,
    HeaterDcCurrent,
    HeaterFrequency,
    HeaterPhase,
    HeaterPower,
    HeaterTemperature,
    HeaterAcCurrentDP,
    HeaterDcCurrentDP,
    HeaterFrequencyDP,
    HeaterPhaseDP,
    HeaterPowerDP,
    HeaterTemperatureDP,
    DSProtocol,
    DSProtocolReference,
    HeaterParameters,
)
from nomad_ikz_plugin.utils import (
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


class DSManualProtocolParserIKZ(MatchingParser):
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
        archive.data.manual_protocol = DSProtocolReference()

        dig_prot_data = DSProtocol()
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


class DSDigitalProtocolParserIKZ(MatchingParser):
    # def is_mainfile(
    #     self,
    #     filename: str,
    #     mime: str,
    #     buffer: bytes,
    #     decoded_buffer: str,
    #     compression: str = None,
    # ) -> Union[bool, Iterable[str]]:
    #     is_mainfile = super().is_mainfile(
    #         filename=filename,
    #         mime=mime,
    #         buffer=buffer,
    #         decoded_buffer=decoded_buffer,
    #         compression=compression,
    #     )
    #     if is_mainfile:
    #         try:
    #             # try to resolve mainfile keys from parser
    #             mainfile_keys = ['test']
    #             self.creates_children = True
    #             return mainfile_keys
    #         except Exception:
    #             return is_mainfile
    #     return is_mainfile

    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        child_archives: dict(test=EntryArchive),  ###### to test multiple archives
        logger,
    ) -> None:
        data_file = mainfile.split('/')[-1]
        data_file_with_path = mainfile.split('raw/')[-1]
        # xlsx = pd.ExcelFile(mainfile)
        # xlsx_sheet = pd.read_excel(
        #     xlsx,
        #     'Sheet1',
        #     comment='#',
        # )

        filetype = 'json'
        filename = f'{data_file[:-5]}.archive.{filetype}'

        # digital_protocol = EntryArchive(
        #     data=DSProtocol(),
        #     metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
        # )

        df_csv = pd.read_csv(mainfile, sep=';', decimal=',', engine='python')

        # start_time = datetime.strptime(
        #     df_csv["T Ist H1 Time"][0],
        #     "%d.%m.%Y %H:%M:%S",
        # ).replace(tzinfo=ZoneInfo(timezone))
        # timestamp = [
        #     (
        #         datetime.strptime(
        #             dt,
        #             "%d.%m.%Y %H:%M:%S",
        #         ).replace(tzinfo=ZoneInfo(timezone))
        #     )
        #     for dt in df_csv["T Ist H1 Time"]
        # ]
        # elapsed_time = np.array(
        #     [
        #         (
        #             datetime.strptime(
        #                 dt,
        #                 "%d.%m.%Y %H:%M:%S",
        #             ).replace(tzinfo=ZoneInfo(timezone))
        #             - start_time
        #         ).total_seconds()
        #         for dt in df_csv["T Ist H1 Time"]
        #     ]
        # )
        # clean repeated Time columns
        for i in df_csv:
            if 'Time' in i and 'T Ist H1 Time' not in i:
                del df_csv[i]
        for i in df_csv:
            if '/' in i:
                new_i = i.replace('/', ' ')
                df_csv[new_i] = df_csv[i]
                del df_csv[i]

        # for _, col in df_csv.items():
        # with archive.m_context.raw_file(filename, 'w') as newfile:
        with h5py.File(f'{mainfile[:-4]}.h5', 'w') as hdf:
            # Iterate through the DataFrame columns and write each to the HDF5 file
            for column in df_csv.columns:
                hdf.create_dataset(column.replace(' ', '_'), data=df_csv[column].values)

        archive.data = DSProtocol()
        archive.data.heaters = []
        archive.data.temperature_1_2 = HeaterTemperatureDP()
        archive.data.temperature_1_3 = HeaterTemperatureDP()
        archive.data.temperature_1_4 = HeaterTemperatureDP()
        archive.data.temperature_pyrometer = HeaterTemperatureDP()
        archive.data.temperature_tp = HeaterTemperatureDP()

        # archive.data.elapsed_time = ureg.Quantity(elapsed_time, ureg("s"))
        # archive.data.timestamp = timestamp
        # archive.data.start_time = start_time

        # path = f"{data_file[:-5]}.h5#/time"
        # HDF5Reference.write_dataset(
        #     archive, ureg.Quantity(elapsed_time, ureg("K")), path
        # )
        # archive.data.temperature_1_2.time = path
        # archive.data.temperature_1_3.time = path

        # path = f"{data_file[:-5]}.h5#/temperature_1_2"
        # HDF5Reference.write_dataset(
        #     archive, ureg.Quantity(df_csv["T12 ValueY"].values, ureg("K")), path
        # )
        # archive.data.temperature_1_2.value = path

        # archive.data.temperature_1_2.time = (
        #     archive.data.elapsed_time  # child_archives['test'].data.elapsed_time
        # )

        # archive.data.temperature_1_3.value = ureg.Quantity(
        #     df_csv['T13 ValueY'].values, ureg('K')
        # )
        # archive.data.temperature_1_3.time = archive.data.elapsed_time

        # archive.data.temperature_1_4.value = ureg.Quantity(
        #     df_csv['T14 ValueY'].values, ureg('K')
        # )
        # archive.data.temperature_1_4.time = archive.data.elapsed_time

        # heater_number = 9
        # for heater in range(heater_number):
        #     archive.data.heaters.append(HeaterParameters())
        #     archive.data.heaters[heater].name = f'heater {heater + 1}'
        #     archive.data.heaters[heater].f1 = HeaterCoil()
        #     archive.data.heaters[heater].f2 = HeaterCoil()
        #     archive.data.heaters[heater].sum_current = HeaterDcCurrentDP()
        #     archive.data.heaters[heater].dc_current = HeaterDcCurrentDP()
        #     archive.data.heaters[heater].power = HeaterPowerDP()
        #     archive.data.heaters[heater].temperature = HeaterTemperatureDP()
        #     archive.data.heaters[heater].f1.ac_current = HeaterAcCurrentDP()
        #     archive.data.heaters[heater].f1.phase = HeaterPhaseDP()
        #     archive.data.heaters[heater].f1.frequency = HeaterFrequencyDP()
        #     archive.data.heaters[heater].f2.ac_current = HeaterAcCurrentDP()
        #     archive.data.heaters[heater].f2.phase = HeaterPhaseDP()
        #     archive.data.heaters[heater].f2.frequency = HeaterFrequencyDP()
        #     archive.data.trafo_1_m = Trafo()
        #     archive.data.trafo_1_p = Trafo()
        #     archive.data.trafo_2_m = Trafo()
        #     archive.data.trafo_2_p = Trafo()

        #     archive.data.heaters[heater].f1.ac_current.value = ureg.Quantity(
        #         df_csv[f'AC_F1 H{heater +1} ValueY'].values,
        #         ureg('A'),
        #     )
        #     archive.data.heaters[heater].f1.ac_current.time = archive.data.elapsed_time

        #     archive.data.heaters[heater].f2.ac_current.value = ureg.Quantity(
        #         df_csv[f'AC_F2 H{heater +1} ValueY'].values,
        #         ureg('A'),
        #     )
        #     archive.data.heaters[heater].f2.ac_current.time = archive.data.elapsed_time

        #     archive.data.heaters[heater].dc_current.value = ureg.Quantity(
        #         df_csv[f'I DC Ist H{heater +1} ValueY'].values,
        #         ureg('A'),
        #     )
        #     archive.data.heaters[heater].dc_current.time = archive.data.elapsed_time

        #     archive.data.heaters[heater].temperature.value = ureg.Quantity(
        #         df_csv[f'T Ist H{heater +1} ValueY'].values,
        #         ureg('K'),
        #     )
        #     archive.data.heaters[heater].temperature.time = archive.data.elapsed_time

        #     archive.data.heaters[heater].power.value = ureg.Quantity(
        #         df_csv[f'P Ist H{heater +1} ValueY'].values,
        #         ureg('W'),
        #     )
        #     archive.data.heaters[heater].power.time = archive.data.elapsed_time

        #     archive.data.heaters[heater].sum_current.value = ureg.Quantity(
        #         df_csv[f'I Summe H{heater +1} ValueY'].values,
        #         ureg('A'),
        #     )
        #     archive.data.heaters[heater].sum_current.time = archive.data.elapsed_time

        #     archive.data.trafo_1_p.value = df_csv['Trafo 1 P ValueY'].values
        #     archive.data.trafo_1_p.time = archive.data.elapsed_time

        #     archive.data.trafo_1_m.value = df_csv['Trafo 1 M ValueY'].values
        #     archive.data.trafo_1_m.time = archive.data.elapsed_time

        #     archive.data.trafo_2_p.value = df_csv['Trafo 2 P ValueY'].values
        #     archive.data.trafo_2_p.time = archive.data.elapsed_time

        #     archive.data.trafo_2_m.value = df_csv['Trafo 2 M ValueY'].values
        #     archive.data.trafo_2_m.time = archive.data.elapsed_time

        # archive.data = DSProtocol()

        # create_archive(
        #     digital_protocol.m_to_dict(),
        #     archive.m_context,
        #     filename,
        #     filetype,
        #     logger,
        # )
