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

from time import sleep, perf_counter
import pandas as pd
from typing import Dict, List
import yaml
import json
import math

from nomad.datamodel.context import ClientContext

from nomad.datamodel import EntryArchive
from nomad.metainfo import MSection, Quantity, Section
from nomad.parsing import MatchingParser
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.data import (
    EntryData,
)

from nomad.units import ureg

from nomad.datamodel.metainfo.basesections import (
    SystemComponent,
    CompositeSystemReference,
    ElementalComposition,
)
from nomad_material_processing import (
    Dopant,
)


def populate_element(line_number, substrates_file: pd.DataFrame):
    """
    Populate the GasSource object from the growth run file
    """
    elements = []
    elements_quantities = [
        "Elements",
    ]
    i = 0
    while True:
        if all(
            f"{key}{'' if i == 0 else '.' + str(i)}" in substrates_file.columns
            for key in elements_quantities
        ):
            elements.append(
                ElementalComposition(
                    element=substrates_file.get(
                        f"Elements{'' if i == 0 else '.' + str(i)}", ""
                    )[line_number],
                )
            )
            i += 1
        else:
            break
    return elements


def populate_dopant(line_number, substrates_file: pd.DataFrame):
    """
    Populate the GasSource object from the growth run file
    """
    dopants = []
    dopant_quantities = [
        "Elements",
    ]
    i = 0
    while True:
        if all(
            f"{key}{'' if i == 0 else '.' + str(i)}" in substrates_file.columns
            for key in dopant_quantities
        ):
            dopants.append(
                Dopant(
                    element=substrates_file.get(
                        f"Doping species{'' if i == 0 else '.' + str(i)}", ""
                    )[line_number],
                    doping_level=substrates_file.get(
                        f"Doping Level{'' if i == 0 else '.' + str(i)}", ""
                    )[line_number],
                )
            )
            i += 1
        else:
            break
    return dopants