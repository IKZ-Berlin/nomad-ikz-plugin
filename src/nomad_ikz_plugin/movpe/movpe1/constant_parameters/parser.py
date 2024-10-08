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
from nomad.metainfo import (
    Quantity,
    Section,
)
from nomad.parsing import MatchingParser
from nomad.parsing.tabular import create_archive
from nomad.utils import hash

from nomad_ikz_plugin.movpe.schema import (
    GrowthMovpe1IKZConstantParameters,
)


class RawFileConstantParameters(EntryData):
    m_def = Section(a_eln=None, label='Raw File Constant Parameters')
    constant_parameters_file = Quantity(
        type=GrowthMovpe1IKZConstantParameters,
        # a_eln=ELNAnnotation(
        #     component="ReferenceEditQuantity",
        # ),
        # shape=['*']
    )


class ParserMovpe1IKZ(MatchingParser):
    def __init__(self):
        super().__init__(
            name='MOVPE 1 IKZ',
            code_name='MOVPE 1 IKZ',
            code_homepage='https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas',
            supported_compressions=['gz', 'bz2', 'xz'],
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        xlsx = pd.ExcelFile(mainfile)
        data_file = mainfile.split('/')[-1]
        data_file_with_path = mainfile.split('raw/')[-1]
        sheet = pd.read_excel(
            xlsx, 'Overview', comment='#', converters={'Overview': str}
        )
        overview = sheet.rename(columns=lambda x: x.strip())
        if len(overview['Constant Parameters ID']) > 1:
            logger.warning(
                f'Only one line expected in the Overview sheet of {data_file_with_path}'
            )
        filetype = 'yaml'
        filename = f"{overview['Constant Parameters ID'][0]}_constant_parameters_growth.archive.{filetype}"
        growth_archive = EntryArchive(
            data=GrowthMovpe1IKZConstantParameters(
                lab_id=overview['Constant Parameters ID'][0],
                data_file=data_file_with_path,
            ),
            m_context=archive.m_context,
            metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
        )
        create_archive(
            growth_archive.m_to_dict(),
            archive.m_context,
            filename,
            filetype,
            logger,
        )
        archive.data = RawFileConstantParameters(
            constant_parameters_file=f'../uploads/{archive.m_context.upload_id}/archive/{hash(archive.metadata.upload_id, filename)}#data'
        )
        archive.metadata.entry_name = (
            overview['Constant Parameters ID'][0] + 'constant parameters file'
        )
