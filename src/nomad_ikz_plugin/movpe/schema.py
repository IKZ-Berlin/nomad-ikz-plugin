import math

import numpy as np
import plotly.graph_objects as go

# from lakeshore_nomad_plugin.hall.schema import HallMeasurement
from laytec_epitt_plugin.schema import LayTecEpiTTMeasurement
from nomad.config import config
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
    SectionProperties,
)
from nomad.datamodel.metainfo.basesections import (
    Component,
    Experiment,
    Process,
    PureSubstance,
    PureSubstanceSection,
    SectionReference,
    System,
    SystemComponent,
)
from nomad.datamodel.metainfo.plot import (
    PlotlyFigure,
    PlotSection,
)
from nomad.datamodel.metainfo.workflow import (
    Link,
)

# from nomad.datamodel.context import ClientContext, ServerContext
# from nomad.app.v1.models.models import User
# from nomad.files import UploadFiles
# from nomad.app.v1.routers.uploads import get_upload_with_read_access

from nomad.metainfo import (
    Quantity,
    Reference,
    SchemaPackage,
    Section,
    SubSection,
)
from nomad.parsing.tabular import TableData
from nomad_material_processing.general import (
    CrystallineSubstrate,
    Geometry,
    SubstrateReference,
    ThinFilm,
    ThinFilmStack,
    ThinFilmStackReference,
)
from nomad_material_processing.vapor_deposition.cvd.general import (
    CVDSource,
    FlashEvaporator,
    Rotation,
)
from nomad_material_processing.vapor_deposition.general import (
    ChamberEnvironment,
    Pressure,
    SampleParameters,
    SubstrateHeater,
    Temperature,
    VaporDeposition,
    VaporDepositionStep,
    VolumetricFlowRate,
)
from nomad_measurements.general import (
    ActivityReference,
)
from nomad_measurements.xrd.schema import ELNXRayDiffraction
from plotly.subplots import make_subplots
from structlog.stdlib import (
    BoundLogger,
)

from nomad_ikz_plugin.characterization.schema import AFMmeasurement, LightMicroscope
from nomad_ikz_plugin.general.schema import (
    IKZMOVPECategory,
    SubstratePreparationStepReference,
)
from nomad_ikz_plugin.utils import handle_section

configuration = config.get_plugin_entry_point('nomad_ikz_plugin.movpe:schema')

m_package = SchemaPackage(
    aliases=[
        'ikz_plugin.movpe.schema',
    ],
)


class BubblerPrecursor(PureSubstance, EntryData):
    """
    A precursor already loaded in a bubbler.
    To calculate the vapor pressure the Antoine equation is used.
    log10(p) = A - [B / (T + C)]
    It is a mathematical expression (derived from the Clausius-Clapeyron equation)
    of the relation between the vapor pressure (p) and the temperature (T) of pure substances.
    """

    m_def = Section(categories=[IKZMOVPECategory])
    name = Quantity(
        type=str,
        description='FILL',
        a_eln=ELNAnnotation(component='StringEditQuantity', label='Substance Name'),
    )
    cas_number = Quantity(
        type=str,
        description='FILL',
        a_eln=ELNAnnotation(component='StringEditQuantity', label='CAS number'),
    )
    weight = Quantity(
        type=np.float64,
        description="""
        Weight of precursor and bubbler.
        Attention: Before weighing bubblers,
        all gaskets and corresponding caps must be attached!
        """,
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
        ),
        unit='kg',
    )
    weight_difference = Quantity(
        type=np.float64,
        description='Weight when the bubbler is exhausted.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
        ),
        unit='kg',
    )
    total_comsumption = Quantity(
        type=np.float64,
        description='FILL DESCRIPTION.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='gram',
        ),
        unit='kg',
    )
    a_parameter = Quantity(
        type=np.float64,
        description='The A parameter of Antoine equation. Dimensionless.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter',
        ),
        unit='millimeter',
    )
    b_parameter = Quantity(
        type=np.float64,
        description='The B parameter of Antoine equation. Temperature units.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
        unit='kelvin',
    )
    c_parameter = Quantity(
        type=np.float64,
        description='The C parameter of Antoine equation. Temperature units.',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
        unit='kelvin',
    )
    information_sheet = Quantity(
        type=str,
        description='pdf files containing certificate and other documentation',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln=ELNAnnotation(
            component='FileEditQuantity',
        ),
    )


class Cylinder(Geometry):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section()
    height = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='nanometer',
        ),
        unit='nanometer',
    )
    radius = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter',
        ),
        unit='millimeter',
    )
    lower_cap_radius = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter',
        ),
        unit='millimeter',
    )
    upper_cap_radius = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter',
        ),
        unit='millimeter',
    )
    cap_surface_area = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter ** 2',
        ),
        unit='millimeter ** 2',
    )
    lateral_surface_area = Quantity(
        type=np.float64,
        description='docs',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='millimeter ** 2',
        ),
        unit='millimeter ** 2',
    )


class SubstrateMovpe(CrystallineSubstrate, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        label_quantity='lab_id', categories=[IKZMOVPECategory], label='Substrate'
    )
    as_received = Quantity(
        type=bool,
        description='Is the sample annealed?',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        # a_tabular={"name": "Substrate/As Received"},
    )
    etching = Quantity(
        type=bool,
        description='Usable Sample',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        # a_tabular={"name": "Substrate/Etching"},
    )
    annealing = Quantity(
        type=bool,
        description='Usable Sample',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        # a_tabular={"name": "Substrate/Annealing"},
    )
    # annealing_temperature = Quantity(
    #     type=np.float64,
    #     description='FILL THE DESCRIPTION',
    #     a_tabular={
    #         "name": "Substrate/Annealing Temperature"
    #     },
    #     a_eln={
    #         "component": "NumberEditQuantity",
    #         "defaultDisplayUnit": "celsius"
    #     },
    #     unit="celsius",
    # )
    tags = Quantity(
        type=str,
        description='FILL',
        shape=['*'],
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Box ID',
        ),
        a_tabular={'name': 'Substrate/Substrate Box'},
    )
    re_etching = Quantity(
        type=bool,
        description='Usable Sample',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        a_tabular={'name': 'Substrate/Re-Etching'},
    )
    re_annealing = Quantity(
        type=bool,
        description='Usable Sample',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        a_tabular={'name': 'Substrate/Re-Annealing'},
    )
    epi_ready = Quantity(
        type=bool,
        description='Sample ready for epitaxy',
        a_eln=ELNAnnotation(
            component='BoolEditQuantity',
        ),
        a_tabular={'name': 'Substrate/Epi Ready'},
    )
    quality = Quantity(
        type=str,
        description='Defective Sample',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
        a_tabular={'name': 'Substrate/Quality'},
    )
    information_sheet = Quantity(
        type=str,
        description='pdf files containing certificate and other documentation',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln=ELNAnnotation(
            component='FileEditQuantity',
        ),
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Notes',
        ),
    )


class ThinFilmMovpeIKZ(ThinFilm, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        label_quantity='lab_id',
        categories=[IKZMOVPECategory],
        label='ThinFilmMovpeIKZ',
    )
    lab_id = Quantity(
        type=str,
        description='the Sample created in the current growth',
        a_tabular={'name': 'GrowthRun/Sample Name'},
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Grown Sample ID',
        ),
    )
    test_quantities = Quantity(
        type=str,
        description='Test quantity',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )


class ThinFilmStackMovpe(ThinFilmStack, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        label_quantity='lab_id',
        categories=[IKZMOVPECategory],
        label='ThinFilmStackMovpe',
    )
    lab_id = Quantity(
        type=str,
        description='the Sample created in the current growth',
        a_tabular={'name': 'GrowthRun/Sample Name'},
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Grown Sample ID',
        ),
    )
    test_quantities = Quantity(
        type=str,
        description='Test quantity',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )


class ThinFilmStackMovpeReference(ThinFilmStackReference):
    """
    A section used for referencing a Grown Sample.
    """

    lab_id = Quantity(
        type=str,
        description='the Sample created in the current growth',
        a_tabular={'name': 'GrowthRun/Sample Name'},
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Grown Sample ID',
        ),
    )
    reference = Quantity(
        type=ThinFilmStackMovpe,
        description='A reference to a NOMAD `ThinFilmStackMovpe` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='ThinFilmStackMovpe Reference',
        ),
    )

    def normalize(self, archive, logger: BoundLogger) -> None:
        """
        The normalizer for the `ThinFilmStackMovpeReference` class.
        """
        super().normalize(archive, logger)


class SystemComponentIKZ(SystemComponent):
    """
    A section for describing a system component and its role in a composite system.
    """

    molar_concentration = Quantity(
        type=np.float64,
        description='The solvent for the current substance.',
        unit='mol/liter',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mol/liter'),
        a_tabular={
            'name': 'Precursors/Molar conc',
            # "unit": "gram"
        },
    )
    system = Quantity(
        type=Reference(System.m_def),
        description='A reference to the component system.',
        a_eln=dict(component='ReferenceEditQuantity'),
    )


class PrecursorsPreparationIKZ(Process, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln={
            'hide': [
                'instruments',
                'steps',
                'samples',
            ]
        },
        label_quantity='name',
        categories=[IKZMOVPECategory],
        label='PrecursorsPreparation',
    )
    data_file = Quantity(
        type=str,
        description='Upload here the spreadsheet file containing the deposition control data',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    lab_id = Quantity(
        type=str,
        description='FILL',
        a_tabular={'name': 'Precursors/Sample ID'},
        a_eln={'component': 'StringEditQuantity', 'label': 'Sample ID'},
    )
    name = Quantity(
        type=str,
        description='FILL',
        a_tabular={'name': 'Precursors/number'},
        a_eln={
            'component': 'StringEditQuantity',
        },
    )
    description = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    flow_titanium = Quantity(  # TODO make this a single flow
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'Precursors/Set flow Ti'},
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'ml / minute'},
        unit='ml / minute',
    )
    flow_calcium = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_tabular={'name': 'Precursors/Set flow Ca'},
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'ml / minute'},
        unit='ml / minute',
    )
    # precursors = SubSection(
    #     section_def=SystemComponent,
    #     description="""
    #     A precursor used in MOVPE. It can be a solution, a gas, or a solid.
    #     """,
    #     repeats=True,
    # )
    components = SubSection(
        description="""
        A list of all the components of the composite system containing a name, reference
        to the system section and mass of that component.
        """,
        section_def=Component,
        repeats=True,
    )


class PrecursorsPreparationIKZReference(ActivityReference):
    """
    A section used for referencing a PrecursorsPreparationIKZ.
    """

    m_def = Section(
        label='PrecursorsPreparationReference',
    )
    reference = Quantity(
        type=PrecursorsPreparationIKZ,
        description='A reference to a NOMAD `PrecursorsPreparationIKZ` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='PrecursorsPreparationIKZ Reference',
        ),
    )


class InSituMonitoringReference(SectionReference):
    """
    A section used for referencing a InSituMonitoring.
    """

    reference = Quantity(
        type=LayTecEpiTTMeasurement,
        description='A reference to a NOMAD `InSituMonitoring` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='In situ Monitoring Reference',
        ),
    )


class HallMeasurementReference(SectionReference):
    """
    A section used for referencing a HallMeasurement.
    The class is taken from the dedicated Lakeshore plugin
    """

    reference = Quantity(
        type=ArchiveSection,  # HallMeasurement,
        description='A reference to a NOMAD `HallMeasurement` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='Hall Measurement Reference',
        ),
    )


class SubstrateMovpeReference(SubstrateReference):
    """
    A section for describing a system component and its role in a composite system.
    """

    lab_id = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.StringEditQuantity,
            label='Substrate ID',
        ),
    )
    reference = Quantity(
        type=SubstrateMovpe,
        a_eln=ELNAnnotation(
            component=ELNComponentEnum.ReferenceEditQuantity,
            label='Substrate',
        ),
    )


class SubstrateInventory(EntryData, TableData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=None,
        categories=[IKZMOVPECategory],
        label='SubstrateInventory',
    )
    data_file = Quantity(
        type=str,
        description='Upload here the spreadsheet file containing the substrates data',
        # a_tabular_parser={
        #     "parsing_options": {"comment": "#"},
        #     "mapping_options": [
        #         {
        #             "mapping_mode": "row",
        #             "file_mode": "multiple_new_entries",
        #             "sections": ["substrates"],
        #         }
        #     ],
        # },
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    substrates = SubSection(
        section_def=SubstrateMovpeReference,
        repeats=True,
    )
    steps = SubSection(
        section_def=SubstratePreparationStepReference,
        repeats=True,
    )


class AFMmeasurementReference(SectionReference):
    """
    A section used for referencing a AFMmeasurement.
    """

    reference = Quantity(
        type=AFMmeasurement,
        description='A reference to a NOMAD `AFMmeasurement` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='AFM Measurement Reference',
        ),
    )


class LiMimeasurementReference(SectionReference):
    """
    A section used for referencing a LightMicroscope.
    """

    reference = Quantity(
        type=LightMicroscope,
        description='A reference to a NOMAD `LightMicroscope` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='Light Microscope Measurement Reference',
        ),
    )


class XRDmeasurementReference(SectionReference):
    """
    A section used for referencing a LightMicroscope.
    """

    reference = Quantity(
        type=ELNXRayDiffraction,
        description='A reference to a NOMAD `ELNXRayDiffraction` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
            label='XRD Measurement Reference',
        ),
    )


class CharacterizationMovpe(ArchiveSection):
    """
    A wrapped class to gather all the characterization methods in MOVPE
    """

    xrd = SubSection(
        section_def=XRDmeasurementReference,
        repeats=True,
    )
    in_situ_reflectance = SubSection(
        section_def=InSituMonitoringReference,
        repeats=True,
    )
    hall = SubSection(
        section_def=HallMeasurementReference,
        repeats=True,
    )
    afm = SubSection(
        section_def=AFMmeasurementReference,
        repeats=True,
    )
    light_microscopy = SubSection(
        section_def=LiMimeasurementReference,
        repeats=True,
    )


class ShaftTemperature(Temperature):
    """
    Central shaft temperature (to hold the susceptor)
    """

    pass


class FilamentTemperature(Temperature):
    """
    heating filament temperature
    """

    pass


class LayTecTemperature(Temperature):
    """
    Central shaft temperature (to hold the susceptor)
    """

    pass


class ChamberEnvironmentMovpe(ChamberEnvironment):
    uniform_gas_flow_rate = SubSection(
        section_def=VolumetricFlowRate,
    )
    pressure = SubSection(
        section_def=Pressure,
    )
    throttle_valve = SubSection(
        section_def=Pressure,
    )
    rotation = SubSection(
        section_def=Rotation,
    )
    heater = SubSection(
        section_def=SubstrateHeater,
    )


class SampleParametersMovpe(SampleParameters):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'shaft_temperature',
                    'filament_temperature',
                    'laytec_temperature',
                    'substrate_temperature',
                    'in_situ_reflectance',
                    'growth_rate',
                    'layer',
                    'substrate',
                ],
            ),
        ),
        # a_plotly_graph_object=[
        #     {
        #         'label': 'shaft temperature',
        #         'index': 0,
        #         'dragmode': 'pan',
        #         'data': {
        #             'type': 'scattergl',
        #             'line': {'width': 2},
        #             'marker': {'size': 6},
        #             'mode': 'lines+markers',
        #             'name': 'Temperature',
        #             'x': '#shaft_temperature/time',
        #             'y': '#shaft_temperature/value',
        #         },
        #         'layout': {
        #             'title': {'text': 'Shaft Temperature'},
        #             'xaxis': {
        #                 'showticklabels': True,
        #                 'fixedrange': True,
        #                 'ticks': '',
        #                 'title': {'text': 'Process time [min]'},
        #                 'showline': True,
        #                 'linewidth': 1,
        #                 'linecolor': 'black',
        #                 'mirror': True,
        #             },
        #             'yaxis': {
        #                 'showticklabels': True,
        #                 'fixedrange': True,
        #                 'ticks': '',
        #                 'title': {'text': 'Temperature [°C]'},
        #                 'showline': True,
        #                 'linewidth': 1,
        #                 'linecolor': 'black',
        #                 'mirror': True,
        #             },
        #             'showlegend': False,
        #         },
        #         'config': {
        #             'displayModeBar': False,
        #             'scrollZoom': False,
        #             'responsive': False,
        #             'displaylogo': False,
        #             'dragmode': False,
        #         },
        #     },
        #     {
        #         'label': 'filament temperature',
        #         'index': 1,
        #         'dragmode': 'pan',
        #         'data': {
        #             'type': 'scattergl',
        #             'line': {'width': 2},
        #             'marker': {'size': 6},
        #             'mode': 'lines+markers',
        #             'name': 'Filament Temperature',
        #             'x': '#filament_temperature/time',
        #             'y': '#filament_temperature/value',
        #         },
        #         'layout': {
        #             'title': {'text': 'Filament Temperature'},
        #             'xaxis': {
        #                 'showticklabels': True,
        #                 'fixedrange': True,
        #                 'ticks': '',
        #                 'title': {'text': 'Process time [min]'},
        #                 # "showline": True,
        #                 'linewidth': 1,
        #                 'linecolor': 'black',
        #                 'mirror': True,
        #             },
        #             'yaxis': {
        #                 'showticklabels': True,
        #                 'fixedrange': True,
        #                 'ticks': '',
        #                 'title': {'text': 'Temperature [°C]'},
        #                 # "showline": True,
        #                 'linewidth': 1,
        #                 'linecolor': 'black',
        #                 'mirror': True,
        #             },
        #             'showlegend': False,
        #         },
        #         'config': {
        #             'displayModeBar': False,
        #             'scrollZoom': False,
        #             'responsive': False,
        #             'displaylogo': False,
        #             'dragmode': False,
        #         },
        #     },
        # ],
    )
    name = Quantity(
        type=str,
        description="""
        Sample name.
        """,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    distance_to_source = Quantity(
        type=float,
        unit='meter',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'millimeter'},
        description="""
        The distance between the substrate and the source.
        It is an array because multiple sources can be used.
        """,
        shape=[1],
    )
    shaft_temperature = SubSection(
        section_def=ShaftTemperature,
    )
    filament_temperature = SubSection(
        section_def=FilamentTemperature,
    )
    laytec_temperature = SubSection(
        section_def=LayTecTemperature,
    )
    in_situ_reflectance = SubSection(
        section_def=InSituMonitoringReference,
    )


class GrowthStepMovpeIKZ(VaporDepositionStep, PlotSection):
    """
    Growth step for MOVPE IKZ
    """

    m_def = Section(
        label_quantity='step_index',
    )
    # name
    # step_index
    # creates_new_thin_film
    # duration
    # sources
    # sample_parameters
    # environment
    # description

    step_index = Quantity(
        type=str,
        description='the step index',
        a_tabular={'name': 'Constant Parameters/Step'},
        a_eln={
            'component': 'StringEditQuantity',
        },
    )
    sample_parameters = SubSection(
        section_def=SampleParametersMovpe,
        repeats=True,
    )
    sources = SubSection(
        section_def=CVDSource,
        repeats=True,
    )
    environment = SubSection(
        section_def=ChamberEnvironmentMovpe,
    )
    in_situ_reflectance = SubSection(
        section_def=InSituMonitoringReference,
    )

    # def normalize(self, archive, logger):
    #     super().normalize(archive, logger)

    #     max_rows = 4
    #     max_cols = 2
    #     figure1 = make_subplots(
    #         rows=max_rows,
    #         cols=max_cols,
    #         subplot_titles=[
    #             'Chamber Pressure',
    #             'Filament T',
    #             'FE1 Back Pressure',
    #             'FE2 Back Pressure',
    #             'Oxygen T',
    #             'Rotation',
    #             'Shaft T',
    #             'Throttle Valve',
    #         ],
    #     )  # , shared_yaxes=True)
    #     arrays = {
    #         'chamber_pressure': self.environment.pressure,
    #         'filament_temp': self.sample_parameters[0].filament_temperature,
    #         'flash_evap1': self.sources[0].vapor_source.pressure,
    #         'flash_evap2': self.sources[1].vapor_source.pressure,
    #         'oxy_temp': self.sources[2].vapor_source.temperature,
    #         'rotation': self.environment.rotation,
    #         'shaft_temp': self.sample_parameters[0].shaft_temperature,
    #         'throttle_valve': self.environment.throttle_valve,
    #     }
    #     row = 1
    #     col = 0
    #     # for logged_par in sorted(arrays):
    #     #     # for logged_par_instance in arrays[logged_par]['obj']:
    #     #     if (
    #     #         arrays[logged_par]["obj"].value.m.any()
    #     #         and arrays[logged_par]["obj"].time.m.any()
    #     #     ):
    #     #         arrays[logged_par]["x"].append(arrays[logged_par]["obj"].time.m)
    #     #         arrays[logged_par]["y"].append(arrays[logged_par]["obj"].value.m)
    #     #     # else:
    #     #     #     logger.warning(f"{str(logged_par_instance)} was empty, check the cells or the column headers in your excel file.")
    #     #     if arrays[logged_par]["x"] and arrays[logged_par]["y"]:
    #     #         scatter = px.scatter(
    #     #             x=arrays[logged_par]["x"], y=arrays[logged_par]["y"]
    #     #         )
    #     #         if col == max_cols:
    #     #             row += 1
    #     #             col = 0
    #     #         if col < max_cols:
    #     #             col += 1
    #     #         figure1.add_trace(scatter.data[0], row=row, col=col)
    #     for logged_par in sorted(arrays):
    #         if (
    #             arrays[logged_par] is not None
    #             and arrays[logged_par].value is not None
    #             and arrays[logged_par].value.m is not None
    #             and arrays[logged_par].time is not None
    #             and arrays[logged_par].time.m is not None
    #         ):
    #             #     arrays[logged_par]["x"].append(arrays[logged_par]["obj"].time.m)
    #             #     arrays[logged_par]["y"].append(arrays[logged_par]["obj"].value.m)
    #             # else:
    #             #     print("empty")
    #             # if arrays[logged_par]["x"] and arrays[logged_par]["y"]:
    #             #     for x, y in zip(arrays[logged_par]["x"], arrays[logged_par]["y"]):
    #             #         figure1.add_trace(
    #             #             px.scatter(x=x, y=y).data[0], row=row, col=(col % max_cols) + 1
    #             #         )
    #             #     col += 1
    #             #     if col % max_cols == 0:
    #             #         row += 1
    #             x = arrays[logged_par].time.m
    #             y = arrays[logged_par].value.m
    #             col += 1
    #             if col > max_cols:
    #                 col = 1
    #                 row += 1
    #             if np.any(np.isfinite(x)) and np.any(np.isfinite(y)):
    #                 scatter = px.scatter(
    #                     x=x,
    #                     y=y,
    #                 )
    #                 figure1.add_trace(scatter.data[0], row=row, col=col)
    #             figure1.update_layout(
    #                 template='plotly_white',
    #                 height=800,
    #                 width=300,
    #                 # title_text='Creating Subplots in Plotly',
    #             )
    #         else:
    #             logger.warning(
    #                 f'{arrays[logged_par]} is an empty path, check your excel file and your parser.'
    #             )
    #     figure1.update_traces(line=dict(width=10), marker=dict(size=10))
    #     figure1.update_yaxes(
    #         ticks='outside',  # "",
    #         showticklabels=True,
    #         showline=True,
    #         linewidth=1,
    #         linecolor='black',
    #         mirror=True,
    #         row=[1, 2, 3, 4],
    #         col=[1, 2],
    #     )
    #     figure1.update_xaxes(
    #         ticks='outside',  # "",
    #         showticklabels=True,
    #         showline=True,
    #         linewidth=1,
    #         linecolor='black',
    #         mirror=True,
    #         row=[1, 2, 3, 4],
    #         col=[1, 2],
    #     )
    #     self.figures = [
    #         PlotlyFigure(label='figure 1', figure=figure1.to_plotly_json())
    #     ]  # .append(PlotlyFigure(label='figure 1', figure=figure1.to_plotly_json()))


class FlashEvaporatorIKZ(FlashEvaporator):
    carrier_gas = SubSection(
        section_def=PureSubstanceSection,
    )


def fill_values(
    subsection: ArchiveSection,
    time_series_quantity: str,
    time_series_key: str,
    dictionary: dict,
):
    if (
        hasattr(subsection, time_series_quantity)
        and hasattr(getattr(subsection, time_series_quantity), 'set_value')
        and hasattr(
            getattr(getattr(subsection, time_series_quantity), 'set_value'), 'm'
        )
        and hasattr(getattr(subsection, time_series_quantity), 'set_time')
        and hasattr(getattr(getattr(subsection, time_series_quantity), 'set_time'), 'm')
    ):
        if time_series_key not in dictionary:
            dictionary[time_series_key] = {
                'set_value': np.array([]),
                'set_time': np.array([]),
                'value': np.array([]),
                'time': np.array([]),
            }
        dictionary[time_series_key]['set_value'] = np.append(
            dictionary[time_series_key]['set_value'],
            getattr(
                getattr(getattr(subsection, time_series_quantity), 'set_value'), 'm'
            ),
        )
        dictionary[time_series_key]['set_time'] = np.append(
            dictionary[time_series_key]['set_time'],
            getattr(
                getattr(getattr(subsection, time_series_quantity), 'set_time'), 'm'
            ),
        )
    if (
        hasattr(subsection, time_series_quantity)
        and hasattr(getattr(subsection, time_series_quantity), 'value')
        and hasattr(getattr(getattr(subsection, time_series_quantity), 'value'), 'm')
        and hasattr(getattr(subsection, time_series_quantity), 'time')
        and hasattr(getattr(getattr(subsection, time_series_quantity), 'time'), 'm')
    ):
        if time_series_key not in dictionary:
            dictionary[time_series_key] = {
                'set_value': np.array([]),
                'set_time': np.array([]),
                'value': np.array([]),
                'time': np.array([]),
            }
        dictionary[time_series_key]['value'] = np.append(
            dictionary[time_series_key]['value'],
            getattr(getattr(getattr(subsection, time_series_quantity), 'value'), 'm'),
        )
        dictionary[time_series_key]['time'] = np.append(
            dictionary[time_series_key]['time'],
            getattr(getattr(getattr(subsection, time_series_quantity), 'time'), 'm'),
        )


class GrowthMovpeIKZ(VaporDeposition, PlotSection, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'method',
                    'data_file',
                    'datetime',
                    'end_time',
                    'duration',
                ],
            ),
            # hide=[
            #     "instruments",
            #     "steps",
            #     "samples",
            #     "description",
            #     "location",
            #     "lab_id",
            # ],
        ),
        label_quantity='lab_id',
        categories=[IKZMOVPECategory],
        label='Growth Process',
    )

    # datetime
    # name
    # description
    # lab_id
    # method
    method = Quantity(
        type=str,
        default='MOVPE IKZ',
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln={'component': 'StringEditQuantity'},
    )
    recipe_id = Quantity(
        type=str,
        description='the ID from RTG',
        a_tabular={'name': 'GrowthRun/Recipe Name'},
        a_eln={'component': 'StringEditQuantity', 'label': 'Recipe ID'},
    )
    steps = SubSection(
        section_def=GrowthStepMovpeIKZ,
        repeats=True,
    )

    def normalize(self, archive, logger):
        # for sample in self.samples:
        #     sample.normalize(archive, logger)
        # for parent_sample in self.parent_sample:
        #     parent_sample.normalize(archive, logger)
        # for substrate in self.substrate:
        #     substrate.normalize(archive, logger)

        archive.workflow2 = None
        super().normalize(archive, logger)
        if self.steps is not None:
            inputs = []
            outputs = []
            for step in self.steps:
                if step.sample_parameters is not None:
                    for sample in step.sample_parameters:
                        if sample.layer is not None:
                            outputs.append(
                                Link(
                                    name=f'{sample.layer.name}',
                                    section=sample.layer.reference,
                                )
                            )
                        if sample.substrate is not None:
                            outputs.append(
                                Link(
                                    name=f'{sample.substrate.name}',
                                    section=sample.substrate.reference,
                                )
                            )

                        if (
                            sample.substrate is not None
                            and sample.substrate.reference.m_proxy_value is not None
                        ):
                            # sub_context = ServerContext(
                            #         get_upload_with_read_access(
                            #             matches["upload_id"][0],
                            #             User(
                            #                 is_admin=True,
                            #                 user_id=archive.metadata.main_author.user_id,
                            #             ),
                            #             include_others=True,
                            #         )
                            #    )  # Upload(upload_id=matches["upload_id"][0]))
                            if hasattr(
                                getattr(sample.substrate.reference, 'substrate'),
                                'name',
                            ):
                                inputs.append(
                                    Link(
                                        name=f'{sample.substrate.reference.substrate.name}',
                                        section=getattr(
                                            sample.substrate.reference.substrate,
                                            'reference',
                                            None,
                                        ),
                                    )
                                )
            archive.workflow2.outputs.extend(set(outputs))
            archive.workflow2.inputs.extend(set(inputs))

        # arrays for plotly figures
        parameters = {}
        if self.steps is not None:
            for step in self.steps:
                if step.sample_parameters is not None:
                    for sample_param in step.sample_parameters:
                        fill_values(
                            sample_param,
                            'filament_temperature',
                            'Filament T',
                            parameters,
                        )
                        fill_values(
                            sample_param, 'shaft_temperature', 'Shaft T', parameters
                        )
                if step.environment is not None:
                    fill_values(step.environment, 'pressure', 'Chamber P', parameters)
                    fill_values(step.environment, 'rotation', 'Rotation', parameters)
                    fill_values(
                        step.environment,
                        'throttle_valve',
                        'Throttle Valve',
                        parameters,
                    )
                if step.sources is not None:
                    for source in step.sources:
                        fill_values(
                            source.vapor_source,
                            'pressure',
                            f'{source.name} P',
                            parameters,
                        )
                        fill_values(
                            source.vapor_source,
                            'temperature',
                            f'{source.name} T',
                            parameters,
                        )

        # plotly figures
        max_cols = 2
        max_rows = math.ceil(len(parameters) / max_cols)
        figure1 = make_subplots(
            rows=max_rows,
            cols=max_cols,
            subplot_titles=list(sorted(parameters.keys())),
        )  # , shared_yaxes=True)
        row = 1
        col = 0
        for par in sorted(parameters.keys()):
            parameter = parameters[par]
            if parameter is not None:
                x_set = parameter['set_time'] / 60
                y_set = parameter['set_value']
                x = parameter['time'] / 60
                y = parameter['value']
                col += 1
                if col > max_cols:
                    col = 1
                    row += 1
                if np.any(np.isfinite(x)) and np.any(np.isfinite(y)):
                    figure1.add_trace(
                        go.Scatter(x=x, y=y, mode='markers', marker=dict(color='blue')),
                        row=row,
                        col=col,
                    )
                if np.any(np.isfinite(x_set)) and np.any(np.isfinite(y_set)):
                    figure1.add_trace(
                        go.Scatter(
                            x=x_set, y=y_set, mode='markers', marker=dict(color='red')
                        ),
                        row=row,
                        col=col,
                    )
                figure1.update_layout(
                    template='plotly_white',
                    height=1000,
                    # width=300,
                    title_text='Blue: measured, Red: set',
                )
            else:
                logger.warning(
                    f'{parameter} is an empty path, check your excel file and your parser.'
                )
        figure1.update_traces(line=dict(width=10), marker=dict(size=10))
        figure1.update_yaxes(
            ticks='outside',  # "",
            showticklabels=True,
            showline=True,
            linewidth=1,
            linecolor='black',
            mirror=True,
            row=[1, 2, 3, 4],
            col=[1, 2],
        )
        figure1.update_xaxes(
            ticks='outside',  # "",
            showticklabels=True,
            showline=True,
            linewidth=1,
            linecolor='black',
            mirror=True,
            row=[1, 2, 3, 4],
            col=[1, 2],
        )
        self.figures = [
            PlotlyFigure(label='figure 1', figure=figure1.to_plotly_json())
        ]  # .append(PlotlyFigure(label='figure 1', figure=figure1.to_plotly_json()))


class GrowthMovpeIKZReference(ActivityReference):
    """
    A section used for referencing a GrowthMovpeIKZ.
    """

    m_def = Section(
        label='GrowthProcessReference',
    )
    reference = Quantity(
        type=GrowthMovpeIKZ,
        description='A reference to a NOMAD `GrowthMovpeIKZ` entry.',
        a_eln=ELNAnnotation(
            component='ReferenceEditQuantity',
        ),
    )


class ExperimentMovpeIKZ(Experiment, EntryData):
    """
    Class autogenerated from yaml schema.
    """

    m_def = Section(
        # a_eln={"hide": ["steps"]},
        categories=[IKZMOVPECategory],
        label='MOVPE Experiment',
    )

    method = Quantity(
        type=str,
    )
    data_file = Quantity(
        type=str,
        description='Upload here the spreadsheet file containing the growth data',
        a_browser={'adaptor': 'RawFileAdaptor'},
        a_eln={'component': 'FileEditQuantity'},
    )
    description = Quantity(
        type=str,
        description='description',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
            label='Notes',
        ),
    )
    substrate_temperature = Quantity(
        type=np.float64,
        description='FILL THE DESCRIPTION',
        a_eln=ELNAnnotation(
            component='NumberEditQuantity',
            defaultDisplayUnit='celsius',
        ),
        unit='kelvin',
    )
    oxygen_argon_ratio = Quantity(
        type=str,
        description='FILL THE DESCRIPTION',
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    composition = Quantity(
        type=str,
        description='FILL THE DESCRIPTION',
        a_eln={
            'component': 'StringEditQuantity',
        },
    )
    precursors_preparation = SubSection(
        section_def=PrecursorsPreparationIKZReference,
    )
    growth_run = SubSection(
        section_def=GrowthMovpeIKZReference,
    )
    characterization = SubSection(section_def=CharacterizationMovpe)

    steps = SubSection(
        section_def=ActivityReference,
        repeats=True,
    )

    def normalize(self, archive, logger):
        from nomad.datamodel import EntryArchive

        archive_sections = (
            attr
            for attr in vars(self).values()
            if isinstance(attr, ArchiveSection) and not isinstance(attr, EntryArchive)
        )
        step_list = []
        for section in archive_sections:
            try:
                step_list.extend(handle_section(section))
            except (AttributeError, TypeError, NameError) as e:
                print(f'An error occurred in section {section}: {e}')
        self.steps = [step for step in step_list if step is not None]

        activity_lists = (
            attr[1]
            for attr in vars(self).items()
            if isinstance(attr[1], list) and attr[0] != 'steps'
        )
        for activity_list in activity_lists:
            for activity in activity_list:
                if isinstance(activity, ArchiveSection):
                    try:
                        step_list.extend(handle_section(activity))
                    except (AttributeError, TypeError, NameError) as e:
                        print(f'An error occurred in section {activity}. {e}')
        self.steps = [step for step in step_list if step is not None]

        archive.workflow2 = None
        super().normalize(archive, logger)


m_package.__init_metainfo__()
