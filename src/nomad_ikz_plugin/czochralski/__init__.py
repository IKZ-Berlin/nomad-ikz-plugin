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


class CzochralskiEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_ikz_plugin.czochralski.schema import m_package

        return m_package


schema = CzochralskiEntryPoint(
    name='CzochralskiSchema',
    description='Schema package for Czochralski Method definitions.',
)


class CzochralskiParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_ikz_plugin.czochralski.parser import CzParser

        return CzParser(**self.dict())


parser = CzochralskiParserEntryPoint(
    name='CzochralskiParser',
    description='Parse a csv file generated by multilog tool https://github.com/nemocrys/multilog.',
    mainfile_name_re=r'.+\.multilog.csv',
    mainfile_mime_re='text/csv',
)
