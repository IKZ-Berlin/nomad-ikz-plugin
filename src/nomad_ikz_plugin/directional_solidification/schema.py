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


import numpy as np
from nomad.config import config
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    SectionProperties,
)
from nomad.datamodel.hdf5 import HDF5Reference
from nomad.datamodel.metainfo.annotations import (
    H5WebAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    Entity,
    EntityReference,
    Experiment,
    Instrument,
    Measurement,
    Process,
    ProcessStep,
    PureSubstance,
    SectionReference,
)
from nomad.datamodel.metainfo.plot import PlotSection
from nomad.metainfo import (
    Datetime,
    Quantity,
    SchemaPackage,
    Section,
    SubSection,
)
from nomad_material_processing.general import (
    TimeSeries,
)

from nomad_ikz_plugin.general.schema import IKZDSCategory

configuration = config.get_plugin_entry_point(
    'nomad_ikz_plugin.directional_solidification:schema'
)

m_package = SchemaPackage(
    aliases=[
        'ikz_plugin.directional_solidification.schema',
    ],
)


def custom_separator(line):
    for sep in ['\t']:
        if sep in line:
            return sep
    return ';'


class Crucible(Entity, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        categories=[IKZDSCategory],
    )
    crucible_id = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    crucible_weight = Quantity(
        type=np.float64,
        description='Weight in grams',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'gram'},
        unit='gram',
    )
    crucible_model = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    crucible_coating = Quantity(
        type=str,
        description='see preprocess activity for details',
        a_eln={'component': 'StringEditQuantity'},
    )
    crucible_coating_pretreatment = Quantity(
        type=str,
        description='see preprocess activity for details',
        a_eln={'component': 'StringEditQuantity'},
    )
    support_side_and_bottom_shape = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    top_cover = Quantity(
        type=str,
        a_eln={
            'component': 'EnumEditQuantity',
            'suggestions': ['slot opening', 'plate'],
        },
    )
    top_cover_material = Quantity(
        type=str,
        a_eln={
            'component': 'EnumEditQuantity',
            'suggestions': ['SiC', 'TiC', 'graphite'],
        },
    )
    top_cover_age = Quantity(
        type=np.float64,
        description='crucible_top_cover_age in hours',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'hour'},
        unit='hour',
    )


class Furnace(Entity, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        categories=[IKZDSCategory],
    )
    furnace_id = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    furnace_description = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )


class Susceptor(Entity, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        categories=[IKZDSCategory],
    )
    susceptor_material = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    susceptor_mass = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )


class DiSoInstrument(Instrument, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZDSCategory],
    )
    vacuum_before_gas_inlet = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mbar'},
        unit='mbar',
    )
    crucible = Quantity(
        type=Crucible,
        a_eln={'component': 'ReferenceEditQuantity'},
    )
    furnace = Quantity(
        type=Furnace,
        a_eln={'component': 'ReferenceEditQuantity'},
    )
    susceptor = Quantity(
        type=Susceptor,
        a_eln={'component': 'ReferenceEditQuantity'},
    )


class DiSoInstruments(EntityReference):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    reference = Quantity(
        type=DiSoInstrument,
        description='A reference to a NOMAD `DiSoInstrument` entry.',
        a_eln={'component': 'ReferenceEditQuantity', 'label': 'Instrument Reference'},
    )


class CruciblePretreatment(Process, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        categories=[IKZDSCategory],
    )
    crucible = Quantity(
        type=Crucible,
        a_eln={'component': 'ReferenceEditQuantity'},
    )
    test = Quantity(
        type=str,
        description='FILL',
        a_eln={'component': 'StringEditQuantity'},
    )


class TemperatureRamp(ProcessStep):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    method = Quantity(
        type=str,
        default='Temperature Ramp (DS IKZ)',
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
    )
    rate = Quantity(
        type=np.float64,
        description='Temperature increase during the ramp',
        a_eln={
            'component': 'NumberEditQuantity',
            'defaultDisplayUnit': 'kelvin / hour',
        },
        shape=['*'],
        unit='kelvin / hour',
    )
    temperature = Quantity(
        type=np.float64,
        description='Temperature at the end of the ramp',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'kelvin'},
        shape=['*'],
        unit='kelvin',
    )
    dwell_time = Quantity(
        type=np.float64,
        description='dwell time',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'hour'},
        shape=['*'],
        unit='hour',
    )


class Weighing(Process, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        categories=[IKZDSCategory],
    )
    method = Quantity(
        type=str,
        default='Weighing (DS IKZ)',
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
    )
    dose = Quantity(
        type=np.float64,
        description='dose',
        a_eln={'component': 'NumberEditQuantity'},
    )
    net_mass_before = Quantity(
        type=np.float64,
        description='net mass before the process step',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'gram'},
        unit='gram',
    )
    crucible_model = Quantity(
        type=str,
        description='The name of the chemical that is typically used in literature',
        a_eln={'component': 'StringEditQuantity'},
    )
    crucible_mass = Quantity(
        type=np.float64,
        description='crucible mass',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'gram'},
        unit='gram',
    )
    brutto_mass_before = Quantity(
        type=np.float64,
        description='brutto mass before the process step',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'gram'},
        unit='gram',
    )
    atmosphere = Quantity(
        type=str,
        description='which atmosphere is choosen for th experiment',
        a_eln={'component': 'StringEditQuantity'},
    )
    oven = Quantity(
        type=str,
        description='oven used in the experiment',
        a_eln={'component': 'StringEditQuantity'},
    )
    brutto_mass_after = Quantity(
        type=np.float64,
        description='brutto mass after the process step',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'gram'},
        unit='gram',
    )
    net_mass_after = Quantity(
        type=np.float64,
        description='net  mass after the process step',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'gram'},
        unit='gram',
    )
    mass_loss = Quantity(
        type=np.float64,
        description='mass loss in percentage',
        a_eln={'component': 'NumberEditQuantity'},
    )
    substances = SubSection(
        section_def=PureSubstance,
        repeats=True,
    )
    steps = SubSection(
        section_def=TemperatureRamp,
        repeats=True,
    )


class Weighings(SectionReference):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    reference = Quantity(
        type=Weighing,
        description='A reference to a NOMAD `Weighing` entry.',
        a_eln={'component': 'ReferenceEditQuantity', 'label': 'Weighing Reference'},
    )


class FeedstockFilling(Process, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        categories=[IKZDSCategory],
    )
    method = Quantity(
        type=str,
        default='Feedstock Filling (DS IKZ)',
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
    )
    notes = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    stacking_order = SubSection(
        section_def=PureSubstance,
        repeats=True,
    )


class FeedstockFillings(SectionReference):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    reference = Quantity(
        type=FeedstockFilling,
        description='A reference to a NOMAD `FeedstockFilling` entry.',
        a_eln={
            'component': 'ReferenceEditQuantity',
            'label': 'FeedstockFilling Reference',
        },
    )


class Recipe(PlotSection, Process, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZDSCategory],
        a_plotly_express={
            'method': 'line',
            'x': '#step_number',
            'y': '#h1_soll_p',
            'label': 'Example Express Plot',
            'index': 0,
            'layout': {
                'title': {'text': 'Example Express Plot'},
                'xaxis': {'title': {'text': 'x axis'}},
                'yaxis': {'title': {'text': 'y axis'}},
            },
        },
    )
    method = Quantity(
        type=str,
        default='Recipe (DS IKZ)',
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
    )
    timestamp = Quantity(
        type=Datetime,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'Datetime'},
        shape=['*'],
    )
    duration = Quantity(
        type=str,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'Duration'},
        shape=['*'],
    )
    step_number = Quantity(
        type=int,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'Step'},
        shape=['*'],
    )
    h1_soll_p = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'H1'},
        a_plot={'label': 'My label', 'x': 'step_number', 'y': 'h1_soll_p'},
        shape=['*'],
    )


class Recipes(SectionReference):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    reference = Quantity(
        type=Recipe,
        description='A reference to a NOMAD `Recipe` entry.',
        a_eln={'component': 'ReferenceEditQuantity', 'label': 'Recipe Reference'},
    )


class Feedstock(Entity, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        categories=[IKZDSCategory],
    )
    supplier = Quantity(
        type=str,
        description='Sample preparation including orientating, polishing, cutting done by this company',
        a_eln={'component': 'StringEditQuantity'},
    )


class BasicCharacterization(Measurement, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        categories=[IKZDSCategory],
    )
    method = Quantity(
        type=str,
        default='Basic Characterization (DS IKZ)',
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
    )
    kopfmasse_b = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity'},
    )
    kopfmasse_l = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity'},
    )
    bodenmasse_b = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity'},
    )
    bodenmasse_l = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity'},
    )
    weight = Quantity(
        type=np.float64,
        description='Weight in grams',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'gram'},
        unit='gram',
    )
    height_north_in_middle = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity'},
    )
    height_south = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity'},
    )
    height_east = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity'},
    )
    height_west = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity'},
    )
    surface_inspection = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )


class Pressure(TimeSeries):
    """
    FILL
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(axes='time', signal='value', long_name='Pressure')
    )

    value = Quantity(
        type=HDF5Reference,
        # unit='',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class GasFlux(TimeSeries):
    """
    FILL
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(axes='time', signal='value', long_name='Gas Flux')
    )

    value = Quantity(
        type=HDF5Reference,
        # unit='',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class PP1(TimeSeries):
    """
    FILL
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(axes='time', signal='value', long_name='PP1')
    )

    value = Quantity(
        type=HDF5Reference,
        # unit='',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class CrucibleBottom(TimeSeries):
    """
    FILL
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(
            axes='time', signal='value', long_name='Crucible Bottom'
        )
    )

    value = Quantity(
        type=HDF5Reference,
        # unit='',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class Concentration(TimeSeries):
    """
    Messwert ppm
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(axes='time', signal='value', long_name='Concentrantion')
    )

    value = Quantity(
        type=HDF5Reference,
        # unit='',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class Resistance(TimeSeries):
    """
    FILL
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(axes='time', signal='value', long_name='Resistance')
    )

    value = Quantity(
        type=HDF5Reference,
        # unit='',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class HeaterPower(TimeSeries):
    """
    FILL
    """

    m_def = Section(
        a_plot=dict(
            # x=['time', 'set_time'],
            # y=['value', 'set_value'],
            x='time',
            y='value',
        ),
    )
    value = Quantity(
        type=float,
        unit='watt',
        shape=['*'],
    )
    time = Quantity(
        type=float,
        description='The process time when each of the values were recorded.',
        shape=['*'],
        unit='second',
    )


class HeaterPowerDP(HeaterPower):
    """
    FILL
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(axes='time', signal='value', long_name='Power')
    )

    value = Quantity(
        type=HDF5Reference,
        unit='watt',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class HeaterFrequency(TimeSeries):
    """
    FILL
    """

    m_def = Section(
        a_plot=dict(
            # x=['time', 'set_time'],
            # y=['value', 'set_value'],
            x='time',
            y='value',
        ),
    )
    value = Quantity(
        type=float,
        unit='Hz',
        shape=['*'],
    )
    time = Quantity(
        type=float,
        description='The process time when each of the values were recorded.',
        shape=['*'],
        unit='second',
    )


class HeaterFrequencyDP(HeaterFrequency):
    """
    FILL
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(axes='time', signal='value', long_name='Frequency')
    )

    value = Quantity(
        type=HDF5Reference,
        unit='Hz',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class HeaterPhase(TimeSeries):
    """
    FILL
    """

    m_def = Section(
        a_plot=dict(
            # x=['time', 'set_time'],
            # y=['value', 'set_value'],
            x='time',
            y='value',
        ),
    )
    value = Quantity(
        type=float,
        unit='degree',
        shape=['*'],
    )
    time = Quantity(
        type=float,
        description='The process time when each of the values were recorded.',
        shape=['*'],
        unit='second',
    )


class HeaterPhaseDP(HeaterPhase):
    """
    FILL
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(axes='time', signal='value', long_name='Phase')
    )

    value = Quantity(
        type=HDF5Reference,
        unit='degree',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class HeaterAcCurrent(TimeSeries):
    """
    FILL
    """

    m_def = Section(
        a_plot=dict(
            # x=['time', 'set_time'],
            # y=['value', 'set_value'],
            x='time',
            y='value',
        ),
    )
    value = Quantity(
        type=float,
        unit='ampere',
        shape=['*'],
    )
    time = Quantity(
        type=float,
        description='The process time when each of the values were recorded.',
        shape=['*'],
        unit='second',
    )


class HeaterAcCurrentDP(HeaterAcCurrent):
    """
    FILL
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(axes='time', signal='value', long_name='AC Current')
    )

    value = Quantity(
        type=HDF5Reference,
        unit='ampere',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class HeaterDcCurrent(TimeSeries):
    """
    FILL
    """

    m_def = Section(
        a_plot=dict(
            # x=['time', 'set_time'],
            # y=['value', 'set_value'],
            x='time',
            y='value',
        ),
    )
    value = Quantity(
        type=float,
        unit='ampere',
        shape=['*'],
    )
    time = Quantity(
        type=float,
        description='The process time when each of the values were recorded.',
        shape=['*'],
        unit='second',
    )


class HeaterDcCurrentDP(HeaterDcCurrent):
    """
    FILL
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(axes='time', signal='value', long_name='DC Current')
    )

    value = Quantity(
        type=HDF5Reference,
        unit='ampere',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class HeaterTemperature(TimeSeries):
    """
    FILL
    """

    m_def = Section(
        a_plot=dict(
            # x=['time', 'set_time'],
            # y=['value', 'set_value'],
            x='time',
            y='value',
        ),
    )
    value = Quantity(
        type=float,
        unit='K',
        shape=['*'],
    )
    time = Quantity(
        type=float,
        description='The process time when each of the values were recorded.',
        shape=['*'],
        unit='second',
    )


class HeaterTemperatureDP(HeaterTemperature):
    """
    FILL
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(axes='time', signal='value', long_name='Temperature')
    )

    value = Quantity(
        type=HDF5Reference,
        unit='K',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class Trafo(TimeSeries):
    """
    FILL
    """

    m_def = Section(a_h5web=H5WebAnnotation(axes='time', signal='value'))

    value = Quantity(
        type=HDF5Reference,
        # unit='K',
        shape=[],
    )
    time = Quantity(
        type=HDF5Reference,
        description='The process time when each of the values were recorded.',
        unit='second',
        shape=[],
    )


class HeaterCoil(ArchiveSection):
    """
    the coil in the instrument
    """

    frequency = SubSection(
        section_def=HeaterFrequency,
    )
    phase = SubSection(
        section_def=HeaterPhase,
    )
    ac_current = SubSection(
        section_def=HeaterAcCurrent,
    )


class HeaterParameters(ArchiveSection):
    """
    the heater in the instrument
    """

    m_def = Section(
        a_h5web=H5WebAnnotation(paths=['temperature', 'power']),
    )

    name = Quantity(
        type=str,
        description='The name of the heater',
    )
    temperature = SubSection(
        section_def=HeaterTemperature,
    )
    power = SubSection(
        section_def=HeaterPower,
    )
    dc_current = SubSection(
        section_def=HeaterDcCurrent,
    )
    sum_current = SubSection(
        section_def=HeaterDcCurrent,
    )
    f1_parameters = SubSection(
        section_def=HeaterCoil,
    )
    f2_parameters = SubSection(
        section_def=HeaterCoil,
    )


class DSProtocol(PlotSection, Process, EntryData):  # , TableData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        categories=[IKZDSCategory],
        # a_h5web=H5WebAnnotation(
        #     axes="elapsed_time",
        #     signal="temperature_1_2/value", # "/data/heaters/0/temperature/value",
        #     paths=['temperature_1_2', 'heaters/0/temperature']
        # ),
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'steps',
                    'instrument',
                    'figures',
                    'sample',
                ],
            ),
        ),
    )

    method = Quantity(
        type=str,
        default='Digital Protocol (DS IKZ)',
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
    )
    start_time = Quantity(
        type=Datetime,
        description='FILL THE DESCRIPTION',
    )
    timestamp = Quantity(
        type=Datetime,
        description='FILL THE DESCRIPTION',
        shape=['*'],
    )
    elapsed_time = Quantity(
        type=HDF5Reference,
        description='FILL THE DESCRIPTION',
        shape=[],
        unit='second',
    )
    trafo_1_m = SubSection(
        section_def=Trafo,
    )
    trafo_1_p = SubSection(
        section_def=Trafo,
    )
    trafo_2_m = SubSection(
        section_def=Trafo,
    )
    trafo_2_p = SubSection(
        section_def=Trafo,
    )
    druck_rezipient = SubSection(
        section_def=Pressure,
    )
    pp1 = SubSection(
        section_def=PP1,
    )
    gasfluss_df2 = SubSection(
        section_def=GasFlux,
    )
    gasfluss_df3 = SubSection(
        section_def=GasFlux,
    )
    gasfluss_df4 = SubSection(
        section_def=GasFlux,
    )
    co_messwert_ppm = SubSection(
        section_def=Concentration,
    )
    co_messwert_vol = SubSection(
        section_def=Concentration,
    )
    no_messwert_ppm = SubSection(
        section_def=Concentration,
    )
    tiegelboden = SubSection(
        section_def=CrucibleBottom,
    )
    temperature_pyrometer = SubSection(
        section_def=HeaterTemperature,
    )
    temperature_1_2 = SubSection(
        section_def=HeaterTemperature,
    )
    temperature_1_3 = SubSection(
        section_def=HeaterTemperature,
    )
    temperature_1_4 = SubSection(
        section_def=HeaterTemperature,
    )
    resistance_hz_4 = SubSection(
        section_def=Resistance,
    )
    resistance_hz_5 = SubSection(
        section_def=Resistance,
    )
    resistance_hz_6 = SubSection(
        section_def=Resistance,
    )
    heaters = SubSection(
        section_def=HeaterParameters,
        repeats=True,
    )


class DSProtocolReference(SectionReference):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    reference = Quantity(
        type=DSProtocol,
        description='A reference to a NOMAD `DSProtocol` entry.',
        a_eln={
            'component': 'ReferenceEditQuantity',
            'label': 'Manual Protocol Reference',
        },
    )


class MagneticFieldSettings(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    name = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    dc_current = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'ampere'},
        unit='ampere',
    )
    frequency = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'Hz'},
        unit='Hz',
    )
    ac_current = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'ampere'},
        unit='ampere',
    )
    phase_shift = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'deg'},
        unit='deg',
    )


class GasSettings(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    gas = Quantity(
        type=PureSubstance,
        a_eln={'component': 'ReferenceEditQuantity'},
    )
    flow = Quantity(
        type=np.float64,
        description='Velocity of gas flow',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'L/minute'},
        unit='L/minute',
    )
    pressure = Quantity(
        type=np.float64,
        description='Pressure of gas',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mbar'},
        unit='mbar',
    )


class PreparationSetupParts(Process, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(categories=[IKZDSCategory])
    method = Quantity(
        type=str,
        default='Preparation Setup Parts (DS IKZ)',
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
    )
    test = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )


class DirectionalSolidificationExperiment(Experiment, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZDSCategory],
    )
    method = Quantity(
        type=str,
        default='Directional Solidification (DS IKZ)',
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
    )
    # recipe_file = Quantity(
    #     type=str,
    #     description='protocol file',
    #     a_tabular_parser={
    #         "parsing_options": {
    #             "comment": "#"
    #         },
    #         "mapping_options": [
    #             {
    #                 "mapping_mode": "column",
    #                 "file_mode": "single_new_entry",
    #                 "sections": [
    #                     "recipe"
    #                 ]
    #             }
    #         ]
    #     },
    #     a_browser={
    #         "adaptor": "RawFileAdaptor"
    #     },
    #     a_eln={
    #         "component": "FileEditQuantity"
    #     },
    # )
    # manual_protocol_file = Quantity(
    #     type=str,
    #     description='''
    #     A reference to an uploaded .xlsx
    #     ''',
    #     a_tabular_parser={
    #         "parsing_options": {
    #             "comment": "#"
    #         },
    #         "mapping_options": [
    #             {
    #                 "mapping_mode": "column",
    #                 "file_mode": "single_new_entry",
    #                 "sections": [
    #                     "manual_protocol"
    #                 ]
    #             }
    #         ]
    #     },
    #     a_browser={
    #         "adaptor": "RawFileAdaptor"
    #     },
    #     a_eln={
    #         "component": "FileEditQuantity"
    #     },
    # )

    protocol_based_on = Quantity(
        type=str,
        description='FILL',
        a_eln={'component': 'StringEditQuantity'},
    )
    protocol_comment = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
    )
    experiment_aim = Quantity(
        type=str,
        description='FILL',
        a_eln={'component': 'StringEditQuantity'},
    )
    instrument = SubSection(
        section_def=Instrument,
    )
    magnetic_field_settings = SubSection(
        section_def=MagneticFieldSettings,
        repeats=True,
    )
    gas_settings = SubSection(
        section_def=GasSettings,
        repeats=True,
    )
    recipe = SubSection(
        section_def=Recipes,
    )
    preparation_setup_parts = SubSection(
        section_def=PreparationSetupParts,
    )
    weighing = SubSection(
        section_def=Weighings,
    )
    feedstock_filling = SubSection(
        section_def=FeedstockFillings,
    )
    manual_protocol = SubSection(
        section_def=DSProtocolReference,
    )
    digital_protocol = SubSection(
        section_def=DSProtocolReference,
    )
    basic_characterization = SubSection(
        section_def=BasicCharacterization,
    )

    # def normalize(self, archive, logger: BoundLogger) -> None:
    #     """
    #     The normalizer for the `MovpeExperimentIKZ` class.
    #     """
    #     super().normalize(archive, logger)

    #     if self.digital_protocol_file:
    #         filetype = 'yaml'
    #         filename = f'{self.digital_protocol_file}.archive.{filetype}'
    #         digital_protocol_archive = EntryArchive(
    #             data=DigitalProtocol(digital_protocol_file=self.digital_protocol_file),
    #             m_context=archive.m_context,
    #             metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
    #         )
    #         create_archive(
    #             digital_protocol_archive.m_to_dict(),
    #             archive.m_context,
    #             filename,
    #             filetype,
    #             logger,
    #         )
    #         setattr(
    #             digital_protocol_archive,
    #             'reference',
    #             f'../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, filename)}#data',
    #         )
    # self.digital_protocol.normalize(archive,logger)


m_package.__init_metainfo__()
