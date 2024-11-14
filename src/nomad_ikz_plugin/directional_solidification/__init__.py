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

from nomad.config.models.plugins import ParserEntryPoint, SchemaPackageEntryPoint
from pydantic import Field


class DirSolEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_ikz_plugin.directional_solidification.schema import m_package

        return m_package


schema = DirSolEntryPoint(
    name='DirectionalSolidificationSchema',
    description='Schema package for Directional Solidification definitions.',
)


class DirSolManualProtocolParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_ikz_plugin.directional_solidification.parser import (
            DSManualProtocolParserIKZ,
        )

        return DSManualProtocolParserIKZ(**self.dict())


manual_protocol_parser = DirSolManualProtocolParserEntryPoint(
    name='DirSolManualProtocolParser',
    description='Parse excel files containing parameters from the process.',
    mainfile_name_re=r'.+\.ds.manualprotocol.xlsx',
    mainfile_mime_re='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
)


class DirSolDigitalProtocolParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_ikz_plugin.directional_solidification.parser import (
            DSDigitalProtocolParserIKZ,
        )

        return DSDigitalProtocolParserIKZ(**self.dict())


digital_protocol_parser = DirSolDigitalProtocolParserEntryPoint(
    name='DirSolDigitalProtocolParser',
    description='Parse excel files containing parameters from the process.',
    mainfile_name_re=r'.+\.csv',
    mainfile_mime_re='text/plain',
    # mainfile_contents_dict={
    #     '__has_all_keys': ['T Ist H1 Time', 'T Ist H5 ValueY'],
    #     '__has_comment': '#',
    # },
)
