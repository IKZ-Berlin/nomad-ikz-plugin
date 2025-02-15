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

from nomad.config.models.plugins import SchemaPackageEntryPoint


class DeprecatedCharacterizationEntryPoint(SchemaPackageEntryPoint):
    """
    Entry point for lazy loading of the schema package.
    """

    def load(self):
        from nomad_ikz_plugin.deprecated.characterization.schema import m_package

        return m_package


schema = DeprecatedCharacterizationEntryPoint(
    name='DeprecatedCharacterizationSchema',
    description="""
    Schema package containing deprecated schemas for characterization
    methods used at IKZ.
    """,
)
