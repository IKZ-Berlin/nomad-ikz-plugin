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

import pandas as pd
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    PubChemPureSubstanceSection,
    PureSubstanceComponent,
    PureSubstanceSection,
)
from nomad.metainfo import (
    Quantity,
    Section,
)
from nomad.parsing import MatchingParser
from nomad.units import ureg
from nomad.utils import hash
from nomad_material_processing.general import (
    SubstrateReference,
    ThinFilmReference,
)
from nomad_material_processing.vapor_deposition.cvd.general import (
    FlashEvaporator,
    FlashSource,
    GasLineEvaporator,
    GasLineSource,
    Rotation,
)
from nomad_material_processing.vapor_deposition.general import (
    Pressure,
    Temperature,
    VolumetricFlowRate,
)

from nomad_ikz_plugin.general.schema import (
    LiquidComponent,
    Solution,
)
from nomad_ikz_plugin.movpe.schema import (
    ChamberEnvironmentMovpe,
    ExperimentMovpeIKZ,
    FilamentTemperature,
    GrowthMovpeIKZ,
    GrowthMovpeIKZReference,
    GrowthStepMovpeIKZ,
    PrecursorsPreparationIKZ,
    PrecursorsPreparationIKZReference,
    SampleParametersMovpe,
    ShaftTemperature,
    SystemComponentIKZ,
    ThinFilmMovpeIKZ,
    ThinFilmStackMovpe,
    ThinFilmStackMovpeReference,
)
from nomad_ikz_plugin.utils import (
    clean_dataframe_headers,
    create_archive,
    get_hash_ref,
    row_timeseries,
)


class RawFileMovpeDepositionControl(EntryData):
    m_def = Section(
        a_eln=None,
        label='Raw File Growth Run Deposition Control',
    )
    name = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    growth_run_deposition_control = Quantity(
        type=ExperimentMovpeIKZ,
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
        shape=['*'],
    )


class ParserMovpe1IKZ(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        from nomad.search import MetadataPagination, search

        filetype = 'yaml'
        xlsx = pd.ExcelFile(mainfile)
        data_file = mainfile.split('/')[-1]
        data_file_with_path = mainfile.split('raw/')[-1]
        # Read the file without headers
        parameter_sheet = pd.read_excel(
            xlsx, 'Ti Sr Parameter', comment='#', header=None
        )

        deposition_control_list = []

        for index, dep_control_run in enumerate(parameter_sheet['Sample ID']):

            # check if experiment archive exists already
            search_experiments = search(
                owner='user',
                query={
                    'results.eln.sections:any': ['ExperimentMovpeIKZ'],
                    'results.eln.methods:any': ['MOVPE 1 experiment'],
                    'upload_id:any': [archive.m_context.upload_id],
                },
                pagination=MetadataPagination(page_size=10000),
                user_id=archive.metadata.main_author.user_id,
            )
            # check if experiment entries are already indexed
            matches = {
                'lab_id': [],
                'entry_id': [],
                'entry_name': [],
                'upload_id': [],
            }
            if search_experiments.pagination.total >= 1:
                for match in search_experiments.data:
                    if (
                        f'{dep_control_run} experiment'
                        in match['results']['eln']['lab_ids']
                    ):
                        matches['lab_id'].extend(match['results']['eln']['lab_ids'])
                        matches['entry_id'].append(match['entry_id'])
                        matches['entry_name'].append(match['entry_name'])
                        matches['upload_id'].append(match['upload_id'])
                if len(matches['entry_id']) == 1:
                    logger.warning(
                        f'One entry with lab_id {set(matches["lab_id"])} and entry_id {set(matches["entry_id"])} already exists. '
                        f'Please check the upload with upload id {set(matches["upload_id"])}.'
                    )
                    continue
                elif len(matches['entry_id']) > 1:
                    logger.warning(
                        f'Some entries with lab_id {set(matches["lab_id"])} and entry_id {set(matches["entry_id"])} are duplicated. Please check them.'
                    )
                    continue
            elif search_experiments.pagination.total == 0:
                # creating ThinFiln and ThinFilmStack archives
                layer_filename = (
                    f'{dep_control_run}_{index}.ThinFilm.archive.{filetype}'
                )
                layer_archive = EntryArchive(
                    data=ThinFilmMovpeIKZ(
                        name=dep_control_run + 'layer',
                        lab_id=dep_control_run + 'layer',
                    ),
                    m_context=archive.m_context,
                    metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
                )
                create_archive(
                    layer_archive.m_to_dict(),
                    archive.m_context,
                    layer_filename,
                    filetype,
                    logger,
                )
                grown_sample_filename = (
                    f'{dep_control_run}.ThinFilmStackMovpe.archive.{filetype}'
                )
                grown_sample_archive = EntryArchive(
                    data=ThinFilmStackMovpe(
                        name=dep_control_run + 'stack',
                        lab_id=dep_control_run,
                        substrate=SubstrateReference(
                            lab_id=parameter_sheet['Substrate ID'].loc[index],
                        ),
                        layers=[
                            ThinFilmReference(
                                reference=f'../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, layer_filename)}#data'
                            )
                        ],
                    ),
                    m_context=archive.m_context,
                    metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
                )
                create_archive(
                    grown_sample_archive.m_to_dict(),
                    archive.m_context,
                    grown_sample_filename,
                    filetype,
                    logger,
                )

                # parsing arrays from excel file
                uniform_setval = pd.Series(
                    [
                        parameter_sheet['Set of argon uniform gas'].loc[index]
                        * ureg('cm ** 3 / minute').to('meter ** 3 / second').magnitude
                    ]
                )

                fil_temp_setval = pd.Series([parameter_sheet['Set Fil T'].loc[index]])
                fil_temp_time, fil_temp_val = row_timeseries(
                    parameter_sheet, 'Fil time', 'Read Fil T', index
                )
                fil_temp_time = fil_temp_time * ureg('minute').to('second').magnitude

                shaft_temp_setval = pd.Series([parameter_sheet['Set Shaft T'].loc[index]])
                shaft_temp_time, shaft_temp_val = row_timeseries(
                    parameter_sheet, 'Shaft time', 'Read Shaft T', index
                )
                shaft_temp_time = (
                    shaft_temp_time * ureg('minute').to('second').magnitude
                )

                pressure_setval = pd.Series(
                    [
                        (
                            parameter_sheet['Set Chamber P'].loc[index]
                            if 'Set Chamber P' in parameter_sheet.columns
                            else None
                        )
                    ]
                )
                pressure_time, pressure_val = row_timeseries(
                    parameter_sheet, 'Chamber pressure time', 'Read Chamber Pressure', index
                )
                pressure_time = pressure_time * ureg('minute').to('second').magnitude

                throttle_time, throttle_val = row_timeseries(
                    parameter_sheet, 'TV time', 'Read throttle valve', index
                )

                rot_setval = pd.Series(
                    [
                        (
                            parameter_sheet['Set Rotation S'].loc[index]
                            if 'Set Rotation S' in parameter_sheet.columns
                            else None
                        )
                    ]
                )
                rot_time, rot_val = row_timeseries(
                    parameter_sheet, 'rot time', 'Read rotation', index
                )
                rot_time = rot_time * ureg('minute').to('second').magnitude

                fe1_pressure_time, fe1_pressure_val = row_timeseries(
                    parameter_sheet, 'BP FE1 time', 'BP FE1', index
                )
                fe1_pressure_time = (
                    fe1_pressure_time * ureg('minute').to('second').magnitude
                )

                fe1_temp_setval = pd.Series(
                    [
                        (
                            parameter_sheet['Set FE1 Temp'].loc[index]
                            if 'Set FE1 Temp' in parameter_sheet.columns
                            else None
                        )
                    ]
                )

                fe1_ar_push_setval = pd.Series(
                    [
                        (
                            parameter_sheet['Set Ar Push 1'].loc[index]
                            if 'Set Ar Push 1' in parameter_sheet.columns
                            else None
                        )
                    ]
                )

                fe1_ar_purge_setval = pd.Series(
                    [
                        (
                            parameter_sheet['Set Ar Purge 1'].loc[index]
                            if 'Set Ar Purge 1' in parameter_sheet.columns
                            else None
                        )
                    ]
                )

                fe2_pressure_time, fe2_pressure_val = row_timeseries(
                    parameter_sheet, 'BP FE2 time', 'BP FE2', index
                )
                fe2_pressure_time = (
                    fe2_pressure_time * ureg('minute').to('second').magnitude
                )

                fe2_temp_setval = pd.Series(
                    [
                        (
                            parameter_sheet['Set FE2 Temp'].loc[index]
                            if 'Set FE2 Temp' in parameter_sheet.columns
                            else None
                        )
                    ]
                )

                fe2_ar_push_setval = pd.Series(
                    [
                        (
                            parameter_sheet['Set Ar Push 2'].loc[index]
                            if 'Set Ar Push 2' in parameter_sheet.columns
                            else None
                        )
                    ]
                )

                fe2_ar_purge_setval = pd.Series(
                    [
                        (
                            parameter_sheet['Set Ar Purge 2'].loc[index]
                            if 'Set Ar Purge 2' in parameter_sheet.columns
                            else None
                        )
                    ]
                )

                gas_temp_time, gas_temp_val = row_timeseries(
                    parameter_sheet, 'Oxygen time', 'Read Oxygen T', index
                )
                gas_temp_time = gas_temp_time * ureg('minute').to('second').magnitude

                gas_mfc_setval = pd.Series(
                    [
                        (
                            parameter_sheet['Set of Oxygen uniform gas'].loc[index]
                            if 'Set of Oxygen uniform gas' in parameter_sheet.columns
                            else None
                        )
                    ]
                )
                growth_description = (
                    str(
                        parameter_sheet['Weekday'].loc[index]
                        if 'Weekday' in parameter_sheet.columns
                        else None
                    )
                    + '. Sequential number: '
                    + str(parameter_sheet['number'].loc[index])
                    + '. '
                    + str(parameter_sheet['Comment'].loc[index])
                )

                # creating GrowthMovpeIKZ archive
                growth_data = GrowthMovpeIKZ(
                    data_file=data_file_with_path,
                    name=f'{dep_control_run} Growth',
                    lab_id=dep_control_run,
                    description=growth_description,
                    datetime=(
                        parameter_sheet['Date'].loc[index]
                        if 'Date' in parameter_sheet.columns
                        else None
                    ),
                    steps=[
                        GrowthStepMovpeIKZ(
                            name='Deposition',
                            duration=(
                                float(parameter_sheet['Duration'].loc[index])
                                if 'Duration' in parameter_sheet.columns
                                else None
                            ),
                            environment=ChamberEnvironmentMovpe(
                                pressure=Pressure(
                                    set_time=pd.Series([0]),
                                    set_value=pressure_setval,
                                    value=pressure_val,
                                    time=pressure_time,
                                ),
                                throttle_valve=Pressure(
                                    value=throttle_val,
                                    time=throttle_time,
                                ),
                                rotation=Rotation(
                                    set_time=pd.Series([0]),
                                    set_value=rot_setval,
                                    value=rot_val,
                                    time=rot_time,
                                ),
                                uniform_gas_flow_rate=VolumetricFlowRate(
                                    set_time=pd.Series([0]),
                                    set_value=uniform_setval,
                                ),
                            ),
                            sample_parameters=[
                                SampleParametersMovpe(
                                    layer=ThinFilmReference(
                                        reference=f'{get_hash_ref(archive.m_context.upload_id, layer_filename)}',
                                    ),
                                    substrate=ThinFilmStackMovpeReference(
                                        reference=f'{get_hash_ref(archive.m_context.upload_id, grown_sample_filename)}',
                                    ),
                                    shaft_temperature=ShaftTemperature(
                                        set_time=pd.Series([0]),
                                        set_value=shaft_temp_setval,
                                        value=shaft_temp_val,
                                        time=shaft_temp_time,
                                    ),
                                    filament_temperature=FilamentTemperature(
                                        set_time=pd.Series([0]),
                                        set_value=fil_temp_setval,
                                        value=fil_temp_val,
                                        time=fil_temp_time,
                                    ),
                                )
                            ],
                            sources=[
                                FlashSource(
                                    name='Flash Evaporator 1',
                                    vapor_source=FlashEvaporator(
                                        pressure=Pressure(
                                            value=fe1_pressure_val,
                                            time=fe1_pressure_time,
                                        ),
                                        temperature=Temperature(
                                            set_time=pd.Series([0]),
                                            set_value=fe1_temp_setval,
                                        ),
                                        carrier_gas=PubChemPureSubstanceSection(
                                            name='Argon',
                                        ),
                                        carrier_push_flow_rate=VolumetricFlowRate(
                                            set_time=pd.Series([0]),
                                            set_value=fe1_ar_push_setval,
                                        ),
                                        carrier_purge_flow_rate=VolumetricFlowRate(
                                            set_time=pd.Series([0]),
                                            set_value=fe1_ar_purge_setval,
                                        ),
                                    ),
                                ),
                                FlashSource(
                                    name='Flash Evaporator 2',
                                    vapor_source=FlashEvaporator(
                                        pressure=Pressure(
                                            value=fe2_pressure_val,
                                            time=fe2_pressure_time,
                                        ),
                                        temperature=Temperature(
                                            set_time=pd.Series([0]),
                                            set_value=fe2_temp_setval,
                                        ),
                                        carrier_gas=PubChemPureSubstanceSection(
                                            name='Argon',
                                        ),
                                        carrier_push_flow_rate=VolumetricFlowRate(
                                            set_time=pd.Series([0]),
                                            set_value=fe2_ar_push_setval,
                                        ),
                                        carrier_purge_flow_rate=VolumetricFlowRate(
                                            set_time=pd.Series([0]),
                                            set_value=fe2_ar_purge_setval,
                                        ),
                                    ),
                                ),
                                GasLineSource(
                                    name='Oxygen uniform gas ',
                                    vapor_source=GasLineEvaporator(
                                        temperature=Temperature(
                                            value=gas_temp_val,
                                            time=gas_temp_time,
                                        ),
                                        total_flow_rate=VolumetricFlowRate(
                                            set_time=pd.Series([0]),
                                            set_value=gas_mfc_setval,
                                        ),
                                    ),
                                ),
                            ],
                        )
                    ],
                )
                growth_filename = f'{dep_control_run}.GrowthMovpeIKZ.archive.{filetype}'
                growth_archive = EntryArchive(
                    data=growth_data,
                    # m_context=archive.m_context,
                    metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
                )
                create_archive(
                    growth_archive.m_to_dict(),
                    archive.m_context,
                    growth_filename,
                    filetype,
                    logger,
                )

        # populate the raw file archive
        archive.data = RawFileMovpeDepositionControl(
            name=data_file, growth_run_deposition_control=deposition_control_list
        )
