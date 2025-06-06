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
import pandas as pd
from nomad.config import config
from nomad.datamodel.data import ArchiveSection, EntryData, User
from nomad.datamodel.metainfo.basesections import Activity, Experiment, Instrument
from nomad.metainfo import (
    Datetime,
    MEnum,
    Quantity,
    QuantityReference,
    SchemaPackage,
    Section,
    SubSection,
)
from nomad.parsing.tabular import TableData

configuration = config.get_plugin_entry_point('nomad_ikz_plugin.czochralski:schema')

m_package = SchemaPackage(
    aliases=[
        'ikz_plugin.czochralski.schema',
    ],
)


class Operators(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    user = Quantity(
        type=User,
        a_eln={'component': 'AuthorEditQuantity'},
        shape=['*'],
    )


class Furnace(Instrument, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        # a_eln={
        #     "lane_width": "600px"
        # },
    )
    furnace_type = Quantity(
        type=str,
        description='Furnace description',
        a_eln={'component': 'StringEditQuantity'},
    )


class FurnacesReference(ArchiveSection):
    """
    A wrapper for the heaters
    """

    furnace = Quantity(
        type=Furnace,
        a_eln={'component': 'ReferenceEditQuantity'},
    )


class Heater(Instrument, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        # a_eln={
        #     "lane_width": "600px"
        # },
    )
    heater_type = Quantity(
        type=MEnum(['Resistance', 'Inductor']),
        a_eln={'component': 'EnumEditQuantity'},
    )
    heater_id = Quantity(
        type=str,
        description='Inductor or resistance heater name or ID',
        a_eln={'component': 'StringEditQuantity'},
    )


class HeatersReference(ArchiveSection):
    """
    A wrapper for the heaters
    """

    heater = Quantity(
        type=Heater,
        a_eln={'component': 'ReferenceEditQuantity'},
    )


class TimeAxis(ArchiveSection):
    """
    The axis time for the sensors
    """

    elapsed_time = Quantity(
        type=np.float64,
        description='Relative time',
        a_tabular={'name': 'time_rel'},
        shape=['*'],
    )
    timestamp = Quantity(
        type=Datetime,
        description='Timestamp for when the values provided in the value field were registered. Individual readings can be stored with their timestamps under value_log. This is to timestamp the nominal setpoint or average reading values listed above in the value field.',
        a_tabular={'name': 'time_abs'},
        shape=['*'],
    )


class Sensor(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    name = Quantity(
        type=str,
        description='Sensor name',
        a_eln={'component': 'StringEditQuantity'},
    )
    elapsed_time = Quantity(
        type=QuantityReference(TimeAxis.elapsed_time),
        default='#data/time_axis/elapsed_time',
    )
    timestamp = Quantity(
        type=QuantityReference(TimeAxis.timestamp), default='#data/time_axis/timestamp'
    )
    value_log = Quantity(
        type=np.float64,
        description='Time history of sensor readings. May differ from nominal setpoint',
        a_tabular={'name': 'TE_1_K_bottom_axis'},
        shape=['*'],
    )
    emissivity = Quantity(
        type=np.float64,
        description='Emission percentage value set in pyrometer',
        a_eln={'component': 'NumberEditQuantity'},
    )
    transmissivity = Quantity(
        type=np.float64,
        description='Transmission percentage value set in pyrometer',
        a_eln={'component': 'NumberEditQuantity'},
    )
    t90 = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'second'},
        unit='second',
    )
    comment = Quantity(
        type=str,
        description='Comment, e.g. sensor position',
        a_eln={'component': 'StringEditQuantity'},
    )


class Sensors(TableData, Instrument, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        # a_eln={
        #     "lane_width": "600px"
        # },
        a_plot=[
            dict(
                x='time_axis/elapsed_time',
                y='sensors/value_log',
            )
        ],
        # a_template=dict(
        #     instruments=[dict(name='RTG SIMS', lab_id='RTG Mikroanalyse Cameca IMS')],
        # ),
    )
    data_file = Quantity(
        type=str,
        description='A reference to an uploaded .csv',
        a_tabular_parser={
            'parsing_options': {'comment': '#', 'sep': ','},
            'mapping_options': [
                {
                    'mapping_mode': 'column',
                    'file_mode': 'current_entry',
                    'sections': ['time_axis', 'sensors_list'],
                }
            ],
        },
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    time_axis = SubSection(section_def=TimeAxis)
    sensors_list = SubSection(section_def=Sensor)  # , repeats=True)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        if archive.data.data_file:
            with archive.m_context.raw_file(self.data_file, 'r') as file:
                data_df = pd.read_csv(file, header=0, skipinitialspace=True, sep=',')
                logger.info('started nomralization')
                print(data_df.keys())


class SensorsReference(ArchiveSection):
    """
    A wrapper for the heaters
    """

    sensor = Quantity(
        type=Sensors,
        a_eln={'component': 'ReferenceEditQuantity'},
    )


class IRImage(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    image = Quantity(
        type=str,
        description='png visualization of heat map matrix',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    heat_map = Quantity(
        type=str,
        description='heat map matrix',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    elapsed_time = Quantity(
        type=np.float64,
        description='Relative time',
    )
    datetime = Quantity(
        type=Datetime,
        description='Absolute time',
    )


class IRCamera(Instrument, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        # a_eln={
        #     "lane_width": "600px"
        # },
    )
    emissivity = Quantity(
        type=np.float64,
        description='Emissivity of the measurement series',
    )
    transmissivity = Quantity(
        type=np.float64,
        description='Transmissivity of the measurement series',
    )
    ambient_temperature = Quantity(
        type=np.float64,
        description='Ambient temperature of the measurement series',
    )
    measurement_range = Quantity(
        type=str,
        description='Measurement range of the measurement series',
    )
    extended_temperature_range = Quantity(
        type=int,
        description='0: off, 1: on',
    )
    comment = Quantity(
        type=str,
        description='Comment, e.g. sensor position',
        a_eln={'component': 'StringEditQuantity'},
    )
    ir_images = SubSection(section_def=IRImage, repeat=True)


class IRCamerasReference(ArchiveSection):
    """
    A wrapper for the heaters
    """

    ir_camera = Quantity(
        type=IRCamera,
        a_eln={'component': 'ReferenceEditQuantity'},
    )


class Instrumentation(ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln={'lane_width': '200px'},
    )
    furnaces = SubSection(section_def=FurnacesReference, repeat=True)
    heaters = SubSection(section_def=HeatersReference, repeat=True)
    sensors = SubSection(section_def=SensorsReference, repeat=True)
    ir_cameras = SubSection(section_def=IRCamerasReference, repeat=True)


class MeltCzochralskiExperiment(Experiment, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        # a_eln={
        #     "lane_width": "600px"
        # },
    )

    method = Quantity(default='MeltCzochralski')

    operators = SubSection(
        section_def=Operators,
    )
    instrumentation = SubSection(
        section_def=Instrumentation,
    )


class DataProcessing(Activity, ArchiveSection):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    software = Quantity(
        type=str,
        description='Software used for logging',
        a_eln={'component': 'StringEditQuantity'},
    )
    sampling_time = Quantity(
        type=np.float64,
        description='Time between sampled points',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'ms'},
        unit='ms',
    )
    image_time = Quantity(
        type=np.float64,
        description='Time between recorded images',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'ms'},
        unit='ms',
    )


m_package.__init_metainfo__()
