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
from nomad.metainfo import (
    Quantity,
)

import pandas as pd
import numpy as np
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.datamodel.data import ArchiveSection, EntryData
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
    Resistance,
    GasFlux,
    Pressure,
    Concentration,
    PP1,
    CrucibleBottom,
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
                xlsx_sheet[f'phi{heater + 1}_F1'].to_numpy(),
                ureg('deg'),
            )
            dig_prot_data.heaters[heater].f1.phase.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].f2.phase.value = ureg.Quantity(
                xlsx_sheet[f'phi{heater + 1}_F2'].to_numpy(),
                ureg('deg'),
            )
            dig_prot_data.heaters[heater].f2.phase.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].f1.frequency.value = ureg.Quantity(
                xlsx_sheet[f'f{heater + 1}_F1'].to_numpy(),
                ureg('Hz'),
            )
            dig_prot_data.heaters[heater].f1.frequency.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].f2.frequency.value = ureg.Quantity(
                xlsx_sheet[f'f{heater + 1}_F2'].to_numpy(),
                ureg('Hz'),
            )
            dig_prot_data.heaters[heater].f2.frequency.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].f1.ac_current.value = ureg.Quantity(
                xlsx_sheet[f'Iac{heater + 1}_F1'].to_numpy(),
                ureg('A'),
            )
            dig_prot_data.heaters[heater].f1.ac_current.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].f2.ac_current.value = ureg.Quantity(
                xlsx_sheet[f'Iac{heater + 1}_F2'].to_numpy(),
                ureg('A'),
            )
            dig_prot_data.heaters[heater].f2.ac_current.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].dc_current.value = ureg.Quantity(
                xlsx_sheet[f'Iges{heater + 1}'].to_numpy(),
                ureg('A'),
            )
            dig_prot_data.heaters[heater].dc_current.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].temperature.value = ureg.Quantity(
                xlsx_sheet[f'Iges{heater + 1}'].to_numpy(),
                ureg('K'),
            )
            dig_prot_data.heaters[heater].temperature.time = ureg.Quantity(
                elapsed_time,
                ureg('s'),
            )
            dig_prot_data.heaters[heater].power.value = ureg.Quantity(
                xlsx_sheet[f'P{heater + 1}'].to_numpy(),
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


class RawFileDigitalProtocolDS(EntryData):
    csv_file = Quantity(
        type=str,
        description='The path to the csv file',
        a_eln={'component': 'FileEditQuantity'},
    )


class DSDigitalProtocolParserIKZ(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger,
    ) -> None:
        data_file = mainfile.split('/')[-1]
        data_file_with_path = mainfile.split('raw/')[-1]

        df_csv = pd.read_csv(mainfile, sep=';', decimal=',', engine='python')
        # delete the repeated Time columns in csv
        for df in df_csv:
            if 'Time' in df and 'T Ist H1 Time' not in df:
                del df_csv[df]
        for df in df_csv:
            if '/' in df:
                new_i = df.replace('/', ' ')
                df_csv[new_i] = df_csv[df]
                del df_csv[df]

        start_time = datetime.strptime(
            df_csv['T Ist H1 Time'][0],
            '%d.%m.%Y %H:%M:%S',
        ).replace(tzinfo=ZoneInfo(timezone))
        timestamp = [
            (
                datetime.strptime(
                    dt,
                    '%d.%m.%Y %H:%M:%S',
                ).replace(tzinfo=ZoneInfo(timezone))
            )
            for dt in df_csv['T Ist H1 Time']
        ]
        elapsed_time = np.array([(dt - start_time).total_seconds() for dt in timestamp])

        filetype = 'yaml'
        digi_protocol_filename = f'{data_file[:-4]}.archive.{filetype}'

        digi_protocol_archive = EntryArchive(
            m_context=archive.m_context,
            metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
        )

        digi_protocol_archive.data = DSProtocol()
        digi_protocol_archive.data.heaters = []
        digi_protocol_archive.data.temperature_1_2 = HeaterTemperatureDP()
        digi_protocol_archive.data.temperature_1_3 = HeaterTemperatureDP()
        digi_protocol_archive.data.temperature_1_4 = HeaterTemperatureDP()
        digi_protocol_archive.data.temperature_pyrometer = HeaterTemperatureDP()
        digi_protocol_archive.data.resistance_hz_4 = Resistance()
        digi_protocol_archive.data.resistance_hz_5 = Resistance()
        digi_protocol_archive.data.resistance_hz_6 = Resistance()
        digi_protocol_archive.data.gasfluss_df2 = GasFlux()
        digi_protocol_archive.data.gasfluss_df3 = GasFlux()
        digi_protocol_archive.data.gasfluss_df4 = GasFlux()
        digi_protocol_archive.data.co_messwert_vol = Concentration()
        digi_protocol_archive.data.co_messwert_ppm = Concentration()
        digi_protocol_archive.data.no_messwert_ppm = Concentration()
        digi_protocol_archive.data.tiegelboden = CrucibleBottom()
        digi_protocol_archive.data.pp1 = PP1()
        digi_protocol_archive.data.druck_rezipient = Pressure()
        digi_protocol_archive.data.trafo_1_m = Trafo()
        digi_protocol_archive.data.trafo_1_p = Trafo()
        digi_protocol_archive.data.trafo_2_m = Trafo()
        digi_protocol_archive.data.trafo_2_p = Trafo()

        # create a simple, plain, hdf5 file
        hdf_filename = f'{data_file[:-4]}.h5'
        heater_number = 9
        with archive.m_context.raw_file(hdf_filename, 'w') as newfile:
            with h5py.File(newfile.name, 'a') as hdf:
                all_params = hdf.create_group('all_parameters')
                all_params.create_dataset('time', data=elapsed_time)
                hdf.attrs['NX_class'] = 'NXroot'
                # all_params.attrs['NX_class'] = 'NXdata'
                for _, df in df_csv.items():
                    group_name = (
                        df.name.replace('ValueY', '').strip().replace(' ', '_').lower()
                    )
                    group = all_params.create_group(group_name)
                    hdf[f'/all_parameters/{group_name}/time'] = hdf[
                        '/all_parameters/time'
                    ]
                    group.create_dataset('value', data=df.values)
                    group.attrs['NX_class'] = 'NXdata'
                    group.attrs['axes'] = 'time'
                    group.attrs['signal'] = 'value'

                # create the heater groups linking the existing datasets
                for i in range(1, heater_number + 1):
                    hdf.create_group(f'heater_{i}')
                    hdf[f'/heater_{i}/time'] = hdf['/all_parameters/time']

                heaters_params = [
                    't_ist',
                    'p_ist',
                    'i_dc_ist',
                    'ac_f1',
                    'ac_f2',
                    'i_summe',
                    'phase_f1',
                    'phase_f2',
                ]

                for name, obj in hdf['/all_parameters'].items():
                    if isinstance(obj, h5py.Group):
                        name = name.replace('all_parameters/', '').replace('/', '')
                        if (
                            any(s in name for s in heaters_params)
                            and 'time' not in name
                        ):
                            heater_number = str(name)[-1]
                            group_name = f'heater_{heater_number}'
                            hdf[f'/{group_name}/{name}'] = hdf[
                                f'/all_parameters/{name}/value'
                            ]

        digi_protocol_archive.data.temperature_1_2.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/t12/time'
        digi_protocol_archive.data.temperature_1_2.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/t12/value'
        digi_protocol_archive.data.temperature_1_3.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/t13/time'
        digi_protocol_archive.data.temperature_1_3.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/t13/value'
        digi_protocol_archive.data.temperature_1_4.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/t14/time'
        digi_protocol_archive.data.temperature_1_4.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/t14/value'
        digi_protocol_archive.data.temperature_pyrometer.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/t_pyrometer/time'
        digi_protocol_archive.data.temperature_pyrometer.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/t_pyrometer/value'
        digi_protocol_archive.data.resistance_hz_4.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/widerstand_hz_4/time'
        digi_protocol_archive.data.resistance_hz_4.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/widerstand_hz_4/value'
        digi_protocol_archive.data.resistance_hz_5.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/widerstand_hz_5/time'
        digi_protocol_archive.data.resistance_hz_5.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/widerstand_hz_5/value'
        digi_protocol_archive.data.resistance_hz_6.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/widerstand_hz_6/time'
        digi_protocol_archive.data.resistance_hz_6.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/widerstand_hz_6/value'
        digi_protocol_archive.data.trafo_1_m.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/trafo_1_m/time'
        digi_protocol_archive.data.trafo_1_m.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/trafo_1_m/value'
        digi_protocol_archive.data.trafo_2_m.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/trafo_2_m/time'
        digi_protocol_archive.data.trafo_2_m.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/trafo_2_m/value'
        digi_protocol_archive.data.trafo_1_p.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/trafo_1_p/time'
        digi_protocol_archive.data.trafo_1_p.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/trafo_1_p/value'
        digi_protocol_archive.data.trafo_2_p.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/trafo_2_p/time'
        digi_protocol_archive.data.trafo_2_p.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/trafo_2_p/value'
        digi_protocol_archive.data.gasfluss_df2.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/gasfluss_df2/time'
        digi_protocol_archive.data.gasfluss_df2.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/gasfluss_df2/value'
        digi_protocol_archive.data.gasfluss_df3.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/gasfluss_df3/time'
        digi_protocol_archive.data.gasfluss_df3.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/gasfluss_df3/value'
        digi_protocol_archive.data.gasfluss_df4.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/gasfluss_df4/time'
        digi_protocol_archive.data.gasfluss_df4.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/gasfluss_df4/value'
        digi_protocol_archive.data.co_messwert_vol.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/co-messwert_[vol_%]/time'
        digi_protocol_archive.data.co_messwert_vol.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/co-messwert_[vol_%]/value'
        digi_protocol_archive.data.co_messwert_ppm.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/co-messwert_[ppm]/time'
        digi_protocol_archive.data.co_messwert_ppm.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/co-messwert_[ppm]/value'
        digi_protocol_archive.data.no_messwert_ppm.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/no-messwert_[ppm]/time'
        digi_protocol_archive.data.no_messwert_ppm.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/no-messwert_ppm/value'
        digi_protocol_archive.data.tiegelboden.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/no-messwert_ppm/time'
        digi_protocol_archive.data.tiegelboden.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/no-messwert_ppm/value'
        digi_protocol_archive.data.pp1.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/pp1/time'
        digi_protocol_archive.data.pp1.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/pp1/value'
        digi_protocol_archive.data.druck_rezipient.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/druck_rezipient/time'
        digi_protocol_archive.data.druck_rezipient.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/druck_rezipient/value'

        for heater in range(int(heater_number)):
            heater_index = heater + 1
            digi_protocol_archive.data.heaters.append(HeaterParameters())
            digi_protocol_archive.data.heaters[heater].name = f'heater {heater_index}'
            digi_protocol_archive.data.heaters[heater].f1_parameters = HeaterCoil()
            digi_protocol_archive.data.heaters[heater].f2_parameters = HeaterCoil()
            digi_protocol_archive.data.heaters[heater].sum_current = HeaterDcCurrentDP()
            digi_protocol_archive.data.heaters[heater].dc_current = HeaterDcCurrentDP()
            digi_protocol_archive.data.heaters[heater].power = HeaterPowerDP()
            digi_protocol_archive.data.heaters[
                heater
            ].temperature = HeaterTemperatureDP()
            digi_protocol_archive.data.heaters[
                heater
            ].f1_parameters.ac_current = HeaterAcCurrentDP()
            digi_protocol_archive.data.heaters[
                heater
            ].f1_parameters.phase = HeaterPhaseDP()
            digi_protocol_archive.data.heaters[
                heater
            ].f1_parameters.frequency = HeaterFrequencyDP()
            digi_protocol_archive.data.heaters[
                heater
            ].f2_parameters.ac_current = HeaterAcCurrentDP()
            digi_protocol_archive.data.heaters[
                heater
            ].f2_parameters.phase = HeaterPhaseDP()
            digi_protocol_archive.data.heaters[
                heater
            ].f2_parameters.frequency = HeaterFrequencyDP()

            digi_protocol_archive.data.heaters[
                heater
            ].f1_parameters.ac_current.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/ac_f1_h{heater_index}/time'
            digi_protocol_archive.data.heaters[
                heater
            ].f1_parameters.ac_current.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/ac_f1_h{heater_index}/value'
            digi_protocol_archive.data.heaters[
                heater
            ].f2_parameters.ac_current.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/ac_f2_h{heater_index}/time'
            digi_protocol_archive.data.heaters[
                heater
            ].f2_parameters.ac_current.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/ac_f2_h{heater_index}/value'
            digi_protocol_archive.data.heaters[
                heater
            ].sum_current.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/i_summe_h{heater_index}/time'
            digi_protocol_archive.data.heaters[
                heater
            ].sum_current.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/i_summe_h{heater_index}/value'
            digi_protocol_archive.data.heaters[
                heater
            ].dc_current.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/i_dc_ist_h{heater_index}/time'
            digi_protocol_archive.data.heaters[
                heater
            ].dc_current.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/i_dc_ist_h{heater_index}/value'
            digi_protocol_archive.data.heaters[
                heater
            ].power.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/p_ist_h{heater_index}/time'
            digi_protocol_archive.data.heaters[
                heater
            ].power.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/p_ist_h{heater_index}/value'
            digi_protocol_archive.data.heaters[
                heater
            ].temperature.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/t_ist_h{heater_index}/time'
            digi_protocol_archive.data.heaters[
                heater
            ].temperature.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/t_ist_h{heater_index}/value'

            if heater <= 6:
                digi_protocol_archive.data.heaters[
                    heater
                ].f1_parameters.phase.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/phase_f1_h{heater_index}/time'
                digi_protocol_archive.data.heaters[
                    heater
                ].f1_parameters.phase.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/phase_f1_h{heater_index}/value'
                digi_protocol_archive.data.heaters[
                    heater
                ].f2_parameters.phase.time = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/phase_f2_h{heater_index}/time'
                digi_protocol_archive.data.heaters[
                    heater
                ].f2_parameters.phase.value = f'/uploads/{archive.m_context.upload_id}/raw/{hdf_filename}#/all_parameters/phase_f2_h{heater_index}/value'

        create_archive(
            digi_protocol_archive.m_to_dict(),
            archive.m_context,
            digi_protocol_filename,
            filetype,
            logger,
        )

        archive.data = RawFileDigitalProtocolDS(csv_file=data_file_with_path)
