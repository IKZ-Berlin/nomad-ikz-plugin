import numpy as np
from nomad.config import config
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.basesections import (
    Measurement,
    MeasurementResult,
)
from nomad.metainfo import Datetime, MEnum, Quantity, SchemaPackage, Section, SubSection

from nomad_ikz_plugin.general.schema import (
    IKZCategory,
    SubstratePreparationStep,
)

configuration = config.get_plugin_entry_point('nomad_ikz_plugin.characterization:schema')

m_package = SchemaPackage()


class AFMresults(MeasurementResult):
    """
    The results of an AFM measurement
    """

    roughness = Quantity(
        type=np.float64,
        description='RMS roughness value obtained by AFM',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'picometer'},
        unit='picometer',
    )
    surface_features = Quantity(
        type=MEnum(['Step Flow', 'Step Bunching', '2D Island']),
        a_eln={'component': 'EnumEditQuantity'},
    )
    scale = Quantity(
        type=np.float64,
        description='scale of the image, to be multiplied by 5 to know the image size',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'nanometer'},
        unit='nanometer',
    )
    image = Quantity(
        type=str,
        description='image showing the thickness measurement points',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    crop_image = Quantity(
        type=str,
        description='crop image ready to be used for AI-based analysis',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )


class AFMmeasurement(Measurement, SubstratePreparationStep, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln={'hide': ['steps']},
        categories=[IKZCategory],
        label='AFM',
    )

    method = Quantity(
        type=str,
        default='AFM (IKZ MOVPE)',
    )
    description = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    datetime = Quantity(
        type=Datetime,
        a_eln={'component': 'DateTimeEditQuantity'},
    )
    results = SubSection(
        section_def=AFMresults,
        repeats=True,
    )


class LiMiresults(MeasurementResult):
    """
    The results of a Light Microscope measurement
    """

    image = Quantity(
        type=str,
        description='image showing the thickness measurement points',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    crop_image = Quantity(
        type=str,
        description='crop image ready to be used for AI-based analysis',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    scale = Quantity(
        type=np.float64,
        description='scale of the image',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'micrometer'},
        unit='micrometer',
    )


class LightMicroscope(Measurement, SubstratePreparationStep, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln={'hide': ['steps']},
        categories=[IKZCategory],
        label='Light Microscope',
    )
    method = Quantity(
        type=str,
        default='Light Microscope (MOVPE IKZ)',
    )
    datetime = Quantity(
        type=Datetime,
        a_eln={'component': 'DateTimeEditQuantity'},
    )
    results = SubSection(
        section_def=LiMiresults,
        repeats=True,
    )
