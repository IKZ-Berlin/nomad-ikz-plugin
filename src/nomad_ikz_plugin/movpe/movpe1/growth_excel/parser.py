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
import yaml
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
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

from nomad_ikz_plugin.movpe.schema import (
    ExperimentMovpeIKZ,
    GrowthMovpeIKZ,
    ThinFilmMovpeIKZ,
    ThinFilmStackMovpe,
)
from nomad_ikz_plugin.utils import (
    create_archive,
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
            xlsx,
            'Ti Sr Parameter',
            comment='#',  # , header=None
        )

        deposition_control_list = []

        for index, sample_id in enumerate(parameter_sheet['Sample ID']):
            # find a growth run archive parsed by the rcp parser.
            # The recognition is based on the folder name where the rcp file was contained

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

                # TODO check the setvals equals the one in growth run archive from the rcp file
                uniform_setval = pd.Series(
                    [
                        parameter_sheet['Ar uniform/sccm'].loc[index]
                        * ureg('cm ** 3 / minute').to('meter ** 3 / second').magnitude
                    ]
                )
                # TODO check the setvals equals the one in growth run archive from the rcp file
                fil_temp_setval = pd.Series(
                    [parameter_sheet['Software Temp °C'].loc[index]]
                )
                fil_temp_time = (
                    pd.Series([0, 2, 30, 50, 120])
                    * ureg('minute').to('second').magnitude
                )
                fil_temp_val = pd.Series(
                    [
                        parameter_sheet['Fil. temp °C before dep.'].loc[index],
                        parameter_sheet['Fil. Temp °C after 2min'].loc[index],
                        parameter_sheet['Fil. Temp °C after 30min'].loc[index],
                        parameter_sheet['Fil. Temp °C after 50min'].loc[index],
                        parameter_sheet['Fil. Temp °C after 120min'].loc[index],
                    ]
                )
                # TODO check the setvals equals the one in growth run archive from the rcp file
                shaft_temp_setval = pd.Series(
                    [parameter_sheet['Shaft temp °C'].loc[index]]
                )

                # WARNING! deposition is taken as the 10th step in the growth run recipe file containing 16 steps in total
                # if the recipe file is changed, the deposition step might be at a different index
                growth_from_rcp.steps[9].sample_parameters[
                    0
                ].filament_temperature.value = fil_temp_val
                growth_from_rcp.steps[9].sample_parameters[
                    0
                ].filament_temperature.time = fil_temp_time

                # if dict_from_rcp = yaml.safe_load(file) is used:
                # growth_from_rcp["data"]["steps"][9]["sample_parameters"][0]["filament_temperature"]["time"] = fil_temp_time
                # growth_from_rcp["data"]["steps"][9]["sample_parameters"][0]["filament_temperature"]["value"] = fil_temp_val

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

        # populate the raw file archive
        archive.data = RawFileMovpeDepositionControl(
            name=data_file, growth_run_deposition_control=deposition_control_list
        )
