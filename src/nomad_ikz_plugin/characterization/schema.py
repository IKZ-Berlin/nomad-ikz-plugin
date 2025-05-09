from typing import TYPE_CHECKING

import numpy as np
import plotly.express as px
from nomad.config import config
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    Filter,
    SectionProperties,
)
from nomad.datamodel.metainfo.basesections import (
    Measurement,
    MeasurementResult,
)
from nomad.datamodel.metainfo.plot import (
    PlotlyFigure,
)
from nomad.metainfo import Datetime, MEnum, Quantity, SchemaPackage, Section, SubSection
from nomad_measurements.transmission.schema import (
    ELNUVVisNirTransmission,
    UVVisNirTransmissionResult,
    UVVisNirTransmissionSettings,
)

from nomad_ikz_plugin.general.schema import (
    IKZCategory,
    SubstratePreparationStep,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger


configuration = config.get_plugin_entry_point(
    'nomad_ikz_plugin.characterization:schema'
)

m_package = SchemaPackage(
    aliases=[
        'ikz_plugin.characterization.schema',
    ],
)


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
        type=MEnum(['Step Flow', 'Step Bunching', '2D Island', 'Grains', 'Holes', 'Stripes', 'Other']),
        a_eln={'component': 'EnumEditQuantity'},
    )
    additional_surface_features = Quantity(
        type=str,
        description='specified surface features e.g. shape/size of holes or islands',
        a_eln={'component': 'StringEditQuantity'},
    )
    scale = Quantity(
        type=np.float64,
        description='scale bar of the image, to be multiplied by 5 to know the image size',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'nanometer'},
        unit='nanometer',
    )
    image = Quantity(
        type=str,
        description='image showing the height measurement points',
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
        description='image showing the measurement',
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


class IKZUVVisNirTransmissionSettings(UVVisNirTransmissionSettings):
    """
    A specialized section for IKZ based on the `UVVisNirTransmissionSettings` section.
    """

    ordinate_type = Quantity(
        type=MEnum(['%T', 'A']),
        description=(
            'Specifies whether the ordinate (y-axis) of the measurement data is '
            'percent transmittance (%T) or absorbance (A).'
        ),
        a_eln={'component': 'EnumEditQuantity'},
    )


class IKZUVVisNirTransmissionResult(UVVisNirTransmissionResult):
    """
    A specialized section for IKZ based on the `UVVisNirTransmissionResult` section.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'transmittance',
                    'absorbance',
                    'wavelength',
                    'extinction_coefficient',
                ],
                visible=Filter(
                    exclude=[
                        'array_index',
                    ],
                ),
            )
        )
    )
    extinction_coefficient = Quantity(
        type=np.float64,
        description=(
            'Extinction coefficient calculated from transmittance and sample thickness '
            'values: -log(T)/L. The coefficient includes the effects of '
            'absorption, reflection, and scattering.'
        ),
        shape=['*'],
        unit='1/m',
        a_plot={'x': 'array_index', 'y': 'extinction_coefficient'},
    )

    def generate_plots(self) -> list[PlotlyFigure]:
        """
        Extends UVVisNirTransmissionResult.generate_plots() method to include the plotly
        figures for the `IKZUVVisNirTransmissionResult` section.

        Returns:
            list[PlotlyFigure]: The plotly figures.
        """
        figures = super().generate_plots()
        if self.wavelength is None:
            return figures

        # generate plot for extinction coefficient
        if self.extinction_coefficient is None:
            return figures

        x = self.wavelength.to('nm').magnitude
        x_label = 'Wavelength'
        xaxis_title = x_label + ' (nm)'

        y = self.extinction_coefficient.to('1/cm').magnitude
        y_label = 'Extinction coefficient'
        yaxis_title = y_label + ' (1/cm)'

        line_linear = px.line(x=x, y=y)

        line_linear.update_layout(
            title=f'{y_label} over {x_label}',
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            xaxis=dict(
                fixedrange=False,
            ),
            yaxis=dict(
                fixedrange=False,
            ),
            template='plotly_white',
        )

        figures.append(
            PlotlyFigure(
                label=f'{y_label} linear plot',
                figure=line_linear.to_plotly_json(),
            ),
        )

        return figures

    def calculate_extinction_coefficient(self, archive, logger):
        """
        Calculate the extinction coefficient from the transmittance and geometric path
        length of the sample. The formula used is: -log( T[%] / 100 ) / L.

        Args:
            archive (EntryArchive): The archive containing the section.
            logger (BoundLogger): A structlog logger.
        """
        self.extinction_coefficient = None
        if not archive.data.samples:
            logger.warning(
                'Cannot calculate extinction coefficient as sample not found.'
            )
            return
        if not archive.data.samples[0].geometric_path_length:
            logger.warning(
                'Cannot calculate extinction coefficient as the geometric path length '
                'of the sample is not found or the value is 0.'
            )
            return

        path_length = archive.data.samples[0].geometric_path_length
        if self.transmittance is not None:
            extinction_coeff = -np.log(self.transmittance) / path_length
            self.extinction_coefficient = extinction_coeff

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `IKZUVVisNirTransmissionResult` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
        self.calculate_extinction_coefficient(archive, logger)


class IKZELNUVVisNirTransmission(ELNUVVisNirTransmission):
    """
    A specialized section for IKZ based on the `ELNUVVisNirTransmission` section.
    """

    m_def = Section(
        categories=[IKZCategory],
        label='IKZ UV-Vis-NIR Transmission',
        a_template={
            'measurement_identifiers': {},
        },
    )
    results = SubSection(
        section_def=IKZUVVisNirTransmissionResult,
        repeats=True,
    )
    transmission_settings = SubSection(
        section_def=IKZUVVisNirTransmissionSettings,
    )

    def write_transmission_data(self, transmission, data_dict, archive, logger):
        """
        Specialized method to write the transmission data for the IKZ plugin. The method
        overrides the `write_transmission_data` method of the parent
        `ELNUVVisNirTransmission` class.
        """
        super().write_transmission_data(transmission, data_dict, archive, logger)
        if data_dict['ordinate_type'] in ['%T', 'A']:
            transmission.transmission_settings.ordinate_type = data_dict.get(
                'ordinate_type'
            )


m_package.__init_metainfo__()
