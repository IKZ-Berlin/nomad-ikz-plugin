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
import os
import time

import pandas as pd
import yaml
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.basesections.v1 import CompositeSystemReference
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
from nomad_material_processing.vapor_deposition.general import (
    Pressure,
    Temperature,
    VolumetricFlowRate,
)

from nomad_ikz_plugin.characterization.schema import (
    AFMmeasurement,
    AFMresults,
)
from nomad_ikz_plugin.movpe.schema import (
    ExperimentMovpeIKZ,
    GrowthMovpeIKZ,
    ThinFilmMovpeIKZ,
    ThinFilmStackMovpe,
)
from nomad_ikz_plugin.utils import (
    create_archive,
)

PARAMETER_SHEET_COLUMNS = {
    # A set of expected columns in the parameter sheet
    'Precursor',
    'Datum',
    'Sample ID',
    'number',
    'Software temp °C',
    'Fil. temp °C before dep.',
    'Fil. temp °C after 2min',
    'Fil. temp °C after 30min',
    'Fil. temp °C after 50min',
    'Fil. temp °C after 120min',
    'Shaft temp °C',
    'Ti conc (molar)',
    'Ti m in g',
    'Ca conc (molar)',
    'Ca/Ba m in g',
    'Sr m in mg',
    'wt.% Ca',
    'La m in mg',
    'wt.% La',
    'flow line 1 (Ti)',
    'flow line 2 (Ca)',
    'c(A-cation)/c(Ti)',
    'Volume Toluol in ml',
    'Ar uniform/sccm',
    'O2/sccm',
    'O2 temp °C before dep.',
    'O2 temp °C after 2min',
    'O2 temp °C after 60min',
    'O2 temp °C after 90min',
    'O2 temp °C after 140min',
    'Ar push/sccm ',
    'Ar purge/sccm',
    'dep time in min',
    'BP FE1 in mbar before dep.',
    'BP FE1 in mbar after 2min',
    'BP FE1 in mbar after 60min',
    'BP FE1 in mbar after 90min',
    'BP FE1 in mbar after 140min',
    'FE1 temp °C',
    'BP FE2 in mbar before dep.',
    'BP FE2 in mbar after 2min',
    'BP FE2 in mbar after 60min',
    'BP FE2 in mbar after 90min',
    'BP FE2 in mbar after 140min',
    'FE2 temp °C',
    'throttle valve in mbar before dep.',
    'throttle valve in mbar after 2min',
    'throttle valve in mbar after 60min',
    'throttle valve in mbar after 90min',
    'throttle valve in mbar after 140min',
    'reactor in mbar',
    'reactor in mbar before dep.',
    'reactor in mbar after 2min',
    'reactor in mbar after 60min',
    'reactor in mbar after 90min',
    'reactor in mbar after 140min',
    'rotation pro min',
    'rotation pro min before dep.',
    'rotation pro min after 2min',
    'rotation pro min after 60min',
    'rotation pro min after 90min',
    'rotation pro min after 140min',
    'substrates',
    'Charge-Nr.',
    'comments on deposition',
    'AFM',
    'XRD',
    'LiMi',
    'Deposition summary',
}


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
            xlsx,
            'Ti Sr Parameter',
            comment='#',  # , header=None
            nrows=10000,
        )
        missing_columns = set(PARAMETER_SHEET_COLUMNS) - set(parameter_sheet.columns)
        if missing_columns:
            logger.error(
                'Missing columns in the parameter sheet: '
                f'[{", ".join(missing_columns)}]. '
                f'Please check the file "{data_file_with_path}" for spelling mistakes.'
            )
            return

        deposition_control_list = []

        for index, sample_id in enumerate(parameter_sheet['Sample ID']):
            # find a growth run archive parsed by the rcp parser.
            # The recognition is based on the folder name where the rcp file was contained in
            time.sleep(
                0.6
            )  # allow the just created rcp entry to be indexing before searching for it
            if pd.isna(sample_id):
                continue
            search_growth = search(
                owner='all',
                query={
                    'results.eln.sections:any': ['GrowthMovpeIKZ'],
                    'upload_id:any': [archive.m_context.upload_id],
                    'results.eln.lab_ids:any': [sample_id],
                },
                pagination=MetadataPagination(page_size=10000),
                user_id=archive.metadata.main_author.user_id,
            )
            if search_growth.pagination.total > 1:
                logger.warn(
                    f'{search_growth.pagination.total} growth runs with lab_id {sample_id} found. Please check the upload with upload id {archive.m_context.upload_id}.'
                )
                continue
            if search_growth.pagination.total == 0:
                logger.warn(
                    f'{search_growth.pagination.total} growth runs with lab_id {sample_id} found. Please upload a recipe file for this sample.'
                )
                continue
            if search_growth.pagination.total == 1:
                with archive.m_context.raw_file(
                    search_growth.data[0]['mainfile'], 'r'
                ) as file:
                    dict_from_rcp = yaml.safe_load(file)
                    if 'data' in dict_from_rcp:
                        growth_from_rcp = GrowthMovpeIKZ.m_from_dict(
                            dict_from_rcp['data']
                        )
                    else:
                        logger.warn(
                            f'No data found in the growth run archive with lab_id {sample_id}. Please check the upload with upload id {archive.m_context.upload_id}.'
                        )
                        continue

            # check if experiment archive exists already
            search_experiments = search(
                owner='user',
                query={
                    'results.eln.sections:any': ['ExperimentMovpeIKZ'],
                    #'results.eln.methods:any': ['MOVPE 1 experiment'],
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
                    if f'{sample_id} experiment' in match['results']['eln']['lab_ids']:
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
                layer_filename = f'{sample_id}_{index}.ThinFilm.archive.{filetype}'
                layer_archive = EntryArchive(
                    data=ThinFilmMovpeIKZ(
                        name=sample_id + 'layer',
                        lab_id=sample_id + 'layer',
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
                    f'{sample_id}.ThinFilmStackMovpe.archive.{filetype}'
                )
                grown_sample_archive = EntryArchive(
                    data=ThinFilmStackMovpe(
                        name=sample_id + 'stack',
                        lab_id=sample_id,
                        substrate=SubstrateReference(
                            name=parameter_sheet['substrates'].loc[index],
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
                precursor = str(parameter_sheet['Ar uniform/sccm'].loc[index])
                date = str(parameter_sheet['Datum'].loc[index])
                deposition_step_no = int(parameter_sheet['number'].loc[index])
                # TODO check the setvals equals the one in growth run archive from the rcp file
                fil_temp_setval = pd.Series(
                    [parameter_sheet['Software temp °C'].loc[index]]
                )
                fil_temp_time = (
                    pd.Series([0, 2, 30, 50, 120])
                    * ureg('minute').to('second').magnitude
                )
                fil_temp_val = pd.Series(
                    [
                        parameter_sheet['Fil. temp °C before dep.'].loc[index],
                        parameter_sheet['Fil. temp °C after 2min'].loc[index],
                        parameter_sheet['Fil. temp °C after 30min'].loc[index],
                        parameter_sheet['Fil. temp °C after 50min'].loc[index],
                        parameter_sheet['Fil. temp °C after 120min'].loc[index],
                    ]
                )
                # TODO check the setvals equals the one in growth run archive from the rcp file
                shaft_temp_setval = pd.Series(
                    [parameter_sheet['Shaft temp °C'].loc[index]]
                )
                ti_molar_conc = parameter_sheet['Ti conc (molar)'].loc[index]
                ti_mass = parameter_sheet['Ti m in g'].loc[index]
                ca_molar_conc = parameter_sheet['Ca conc (molar)'].loc[index]
                ca_ba_mass_ratio = parameter_sheet['Ca/Ba m in g'].loc[index]
                sr_mass = parameter_sheet['Sr m in mg'].loc[index]
                ca_weigth_percent = parameter_sheet['wt.% Ca'].loc[index]
                la_mass = parameter_sheet['La m in mg'].loc[index]
                la_weigth_percent = parameter_sheet['wt.% La'].loc[index]
                conc_ratio_a_ti = parameter_sheet['c(A-cation)/c(Ti)'].loc[index]
                vol_toluol = parameter_sheet['Volume Toluol in ml'].loc[index]

                flow_line_1_ti = pd.Series(
                    [parameter_sheet['flow line 1 (Ti)'].loc[index]]
                )
                flow_line_2_ca = pd.Series(
                    [parameter_sheet['flow line 2 (Ca)'].loc[index]]
                )
                # TODO check the setvals equals the one in growth run archive from the rcp file
                uniform_setval = pd.Series(
                    [
                        parameter_sheet['Ar uniform/sccm'].loc[index]
                        * ureg('cm ** 3 / minute').to('meter ** 3 / second').magnitude
                    ]
                )
                # TODO check the setvals equals the one in growth run archive from the rcp file
                ox_flow_setval = pd.Series(
                    [
                        parameter_sheet['O2/sccm'].loc[index]
                        * ureg('cm ** 3 / minute').to('meter ** 3 / second').magnitude
                    ]
                )
                ox_temp_time = (
                    pd.Series([0, 2, 60, 90, 140])
                    * ureg('minute').to('second').magnitude
                )
                ox_temp_val = pd.Series(
                    [
                        parameter_sheet['O2 temp °C before dep.'].loc[index],
                        parameter_sheet['O2 temp °C after 2min'].loc[index],
                        parameter_sheet['O2 temp °C after 60min'].loc[index],
                        parameter_sheet['O2 temp °C after 90min'].loc[index],
                        parameter_sheet['O2 temp °C after 140min'].loc[index],
                    ]
                )
                # TODO WARNING! It is not clear whether this push and purge belong to the FE1 or FE2
                ar_push_flow = parameter_sheet['Ar push/sccm '].loc[index]
                ar_purge_flow = parameter_sheet['Ar purge/sccm'].loc[index]
                # TODO check if it matches the timing from rcp file
                deposition_time = parameter_sheet['dep time in min'].loc[index]

                fe1_back_press_time = (
                    pd.Series([0, 2, 60, 90, 140])
                    * ureg('minute').to('second').magnitude
                )
                fe1_back_press_val = pd.Series(
                    [
                        parameter_sheet['BP FE1 in mbar before dep.'].loc[index],
                        parameter_sheet['BP FE1 in mbar after 2min'].loc[index],
                        parameter_sheet['BP FE1 in mbar after 60min'].loc[index],
                        parameter_sheet['BP FE1 in mbar after 90min'].loc[index],
                        parameter_sheet['BP FE1 in mbar after 140min'].loc[index],
                    ]
                )
                # TODO check the setvals equals the one in growth run archive from the rcp file
                fe1_temp_setval = parameter_sheet['FE1 temp °C'].loc[index]

                fe2_back_press_time = (
                    pd.Series([0, 2, 60, 90, 140])
                    * ureg('minute').to('second').magnitude
                )
                fe2_back_press_val = pd.Series(
                    [
                        parameter_sheet['BP FE2 in mbar before dep.'].loc[index],
                        parameter_sheet['BP FE2 in mbar after 2min'].loc[index],
                        parameter_sheet['BP FE2 in mbar after 60min'].loc[index],
                        parameter_sheet['BP FE2 in mbar after 90min'].loc[index],
                        parameter_sheet['BP FE2 in mbar after 140min'].loc[index],
                    ]
                )
                # TODO check the setvals equals the one in growth run archive from the rcp file
                fe2_temp_setval = parameter_sheet['FE2 temp °C'].loc[index]

                throttle_time = (
                    pd.Series([0, 2, 60, 90, 140])
                    * ureg('minute').to('second').magnitude
                )
                throttle_val = pd.Series(
                    [
                        parameter_sheet['throttle valve in mbar before dep.'].loc[
                            index
                        ],
                        parameter_sheet['throttle valve in mbar after 2min'].loc[index],
                        parameter_sheet['throttle valve in mbar after 60min'].loc[
                            index
                        ],
                        parameter_sheet['throttle valve in mbar after 90min'].loc[
                            index
                        ],
                        parameter_sheet['throttle valve in mbar after 140min'].loc[
                            index
                        ],
                    ]
                )
                # TODO check the setvals equals the one in growth run archive from the rcp file
                reactor_pressure_setval = pd.Series(
                    [parameter_sheet['reactor in mbar'].loc[index]]
                )
                reactor_pressure_time = (
                    pd.Series([0, 2, 60, 90, 140])
                    * ureg('minute').to('second').magnitude
                )
                reactor_pressure_val = pd.Series(
                    [
                        parameter_sheet['reactor in mbar before dep.'].loc[index],
                        parameter_sheet['reactor in mbar after 2min'].loc[index],
                        parameter_sheet['reactor in mbar after 60min'].loc[index],
                        parameter_sheet['reactor in mbar after 90min'].loc[index],
                        parameter_sheet['reactor in mbar after 140min'].loc[index],
                    ]
                )
                # TODO check the setvals equals the one in growth run archive from the rcp file
                rotation_setval = pd.Series(
                    [parameter_sheet['rotation pro min'].loc[index]]
                )
                rotation_time = (
                    pd.Series([0, 2, 60, 90, 140])
                    * ureg('minute').to('second').magnitude
                )
                rotation_val = pd.Series(
                    [
                        parameter_sheet['rotation pro min before dep.'].loc[index],
                        parameter_sheet['rotation pro min after 2min'].loc[index],
                        parameter_sheet['rotation pro min after 60min'].loc[index],
                        parameter_sheet['rotation pro min after 90min'].loc[index],
                        parameter_sheet['rotation pro min after 140min'].loc[index],
                    ]
                )

                # WARNING!
                # deposition is taken as the "deposition_step_no" step read from the recipe file
                # if the recipe file is changed, the deposition step might be at a different index

                # calculation of the time of the deposition step
                # the time of the deposition step is the sum of the times of all the previous steps
                dep_time = 0
                for i in range(deposition_step_no - 1):
                    dep_time += growth_from_rcp.steps[i].duration.m

                # let's add samples to the growth run archive
                growth_from_rcp.m_add_sub_section(
                    GrowthMovpeIKZ.samples,
                    CompositeSystemReference(
                        reference=f'../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, grown_sample_filename)}#data'
                    ),
                )
                # let's update the growth run archive with the deposition control parameters
                growth_from_rcp.steps[deposition_step_no - 1].name = 'deposition'
                growth_from_rcp.steps[
                    deposition_step_no - 1
                ].step_index = '10 - deposition'
                growth_from_rcp.steps[deposition_step_no - 1].sample_parameters[
                    0
                ].filament_temperature.value = ureg.Quantity(
                    list(fil_temp_val),
                    ureg('celsius'),
                )
                growth_from_rcp.steps[deposition_step_no - 1].sample_parameters[
                    0
                ].filament_temperature.time = dep_time + fil_temp_time
                growth_from_rcp.steps[deposition_step_no - 1].sources[
                    1
                ].peristaltic_pump_flux = VolumetricFlowRate(
                    set_value=flow_line_1_ti
                    * ureg('cm ** 3 / minute').to('meter ** 3 / second').magnitude
                )
                growth_from_rcp.steps[deposition_step_no - 1].sources[
                    2
                ].peristaltic_pump_flux = VolumetricFlowRate(
                    set_value=flow_line_2_ca
                    * ureg('cm ** 3 / minute').to('meter ** 3 / second').magnitude
                )
                growth_from_rcp.steps[deposition_step_no - 1].sources[
                    0
                ].vapor_source.temperature = Temperature(
                    time=dep_time + ox_temp_time,
                    value=ox_temp_val * ureg('celsius'),
                )
                growth_from_rcp.steps[deposition_step_no - 1].sources[
                    1
                ].vapor_source.pressure = Pressure(
                    time=dep_time + fe1_back_press_time,
                    value=fe1_back_press_val * ureg('mbar'),
                )
                growth_from_rcp.steps[deposition_step_no - 1].sources[
                    2
                ].vapor_source.pressure = Pressure(
                    time=dep_time + fe2_back_press_time,
                    value=fe2_back_press_val * ureg('mbar'),
                )
                growth_from_rcp.steps[
                    deposition_step_no - 1
                ].environment.throttle_valve = Pressure(
                    time=dep_time + throttle_time,
                    value=throttle_val,
                )
                growth_from_rcp.steps[
                    deposition_step_no - 1
                ].environment.pressure.value = ureg.Quantity(
                    list(reactor_pressure_val),
                    ureg('mbar'),
                )
                growth_from_rcp.steps[
                    deposition_step_no - 1
                ].environment.pressure.time = dep_time + reactor_pressure_time
                growth_from_rcp.steps[
                    deposition_step_no - 1
                ].environment.rotation.value = rotation_val
                growth_from_rcp.steps[
                    deposition_step_no - 1
                ].environment.rotation.time = dep_time + rotation_time

                # in the case where dict_from_rcp = yaml.safe_load(file) is used:
                # growth_from_rcp["data"]["steps"][9]["sample_parameters"][0]["filament_temperature"]["time"] = fil_temp_time
                # growth_from_rcp["data"]["steps"][9]["sample_parameters"][0]["filament_temperature"]["value"] = fil_temp_val

                # dump the updated growth dictionary in the growth archive
                growth_archive = EntryArchive(
                    data=growth_from_rcp,
                    m_context=archive.m_context,
                    metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
                )
                create_archive(
                    growth_archive.m_to_dict(),
                    archive.m_context,
                    search_growth.data[0]['mainfile'],
                    filetype,
                    logger,
                    overwrite=True,
                )
            # AFM parsing !!!

            # check the correctness of the file location in the uploaded zip folder
            afm_folder = f'{os.path.dirname(mainfile)}/{sample_id}/AFM'
            if not os.path.isdir(afm_folder):
                logger.warn(f'AFM folder in {sample_id} not found.')
            else:
                for file in [f for f in os.listdir(afm_folder) if f.endswith('.png')]:
                    afm_filename = f'{sample_id}_AFM.archive.{filetype}'
                    afm_data = AFMmeasurement()
                    afm_data.m_add_sub_section(
                        AFMmeasurement.samples,
                        CompositeSystemReference(
                            reference=f'../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, grown_sample_filename)}#data'
                        ),
                    )
                    afm_data.m_add_sub_section(
                        AFMmeasurement.results,
                        AFMresults(
                            name=sample_id,
                            image=f'{mainfile.split("/")[-2]}/{sample_id}/AFM/{file}',
                        ),
                    )
                    afm_archive = EntryArchive(
                        data=afm_data,
                        m_context=archive.m_context,
                        metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
                    )
                    create_archive(
                        afm_archive.m_to_dict(),
                        archive.m_context,
                        afm_filename,
                        filetype,
                        logger,
                    )

        # populate the raw file archive
        archive.data = RawFileMovpeDepositionControl(
            name=data_file, growth_run_deposition_control=deposition_control_list
        )
