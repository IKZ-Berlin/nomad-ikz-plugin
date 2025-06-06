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

from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field


class OldExcelParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_ikz_plugin.movpe.movpe1.old_growth_excel.parser import (
            ParserMovpe1IKZ,
        )

        return ParserMovpe1IKZ(**self.dict())


parser = OldExcelParserEntryPoint(
    name='Movpe1ParserOld',
    description='Parse excel files containing growth process parameters logged manually.',
    mainfile_name_re=r'.+\.xlsx',
    mainfile_mime_re=r'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    mainfile_contents_dict={
        'Deposition Control': {
            '__has_all_keys': ['Constant Parameters ID', 'Sample ID', 'Date', 'number']
        },
        'Precursors': {'__has_all_keys': ['Sample ID']},
        '__has_comment': '#',
    },
)
