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


class Movpe1RcpParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_ikz_plugin.movpe.movpe1.rcp.parser import ParserMovpe1RcpIKZ

        return ParserMovpe1RcpIKZ(**self.dict())


parser = Movpe1RcpParserEntryPoint(
    name='Movpe1Parser',
    description='Parse rcp plain text files containing logs from the MOVPE 1 machine in IKZ.',
    mainfile_name_re=r'.+\.rcp',
    mainfile_mime_re=r'text/plain',
)
