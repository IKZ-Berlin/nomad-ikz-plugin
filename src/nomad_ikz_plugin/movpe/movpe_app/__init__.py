from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    App,
    Column,
    Columns,
    FilterMenu,
    FilterMenus,
    Filters,
)

movpesubstrateapp = AppEntryPoint(
    name='MOVPESubstratesApp',
    description='Explore MOVPE substrates.',
    app=App(
        label='MOVPE Substrates',
        path='movpesubstrateapp',
        category='MOVPE',
        columns=Columns(
            selected=[
                'data.name#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.supplier#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.datetime#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.lab_id#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.crystal_properties.orientation#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.crystal_properties.miscut.angle#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.crystal_properties.miscut.orientation#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.geometry.length#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.geometry.width#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.electronic_properties.conductivity_type#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.tags#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
                'data.description#nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
            ],
            options={
                'data.name#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.supplier#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Supplier ID'
                ),
                'data.datetime#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Delivery Date'
                ),
                'data.lab_id#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Substrate ID'
                ),
                'data.tags#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Substrate Box'
                ),
                'data.description#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Comment'
                ),
                'data.etching#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.annealing#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.re_etching#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.re_annealing#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.epi_ready#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.geometry.length#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Length', unit='mm'
                ),
                'data.geometry.width#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Width', unit='mm'
                ),
                'data.dopants.elements#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.dopants.doping_level#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.crystal_properties.orientation#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
                'data.crystal_properties.miscut.angle#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Miscut Angle'
                ),
                'data.crystal_properties.miscut.orientation#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(
                    label='Miscut Orientation'
                ),
                'data.electronic_properties.conductivity_type#nomad_ikz_plugin.movpe.schema.SubstrateMovpe': Column(),
            },
        ),
        filter_menus=FilterMenus(
            options={
                'material': FilterMenu(label='Material'),
                'eln': FilterMenu(label='Electronic Lab Notebook'),
                'custom_quantities': FilterMenu(label='User Defined Quantities'),
                'author': FilterMenu(label='Author / Origin / Dataset'),
                'metadata': FilterMenu(label='Visibility / IDs / Schema'),
            }
        ),
        filters=Filters(
            include=['*#nomad_ikz_plugin.movpe.schema.SubstrateMovpe'],
        ),
        filters_locked={
            'section_defs.definition_qualified_name': [
                'nomad_ikz_plugin.movpe.schema.SubstrateMovpe',
            ],
        },
    ),
)


movpegrowthrunapp = AppEntryPoint(
    name='MOVPEGrowthRunApp',
    description='Explore MOVPE growth runs.',
    app=App(
        label='MOVPE Growth Runs',
        path='movpegrowthrunapp',
        category='MOVPE',
        columns=Columns(
            selected=[
                'data.name#nomad_ikz_plugin.movpe.schema.GrowthMovpeIKZ',
                'data.name#nomad_ikz_plugin.movpe.schema.GrowthMovpeIKZ',
                'data.datetime#nomad_ikz_plugin.movpe.schema.GrowthMovpeIKZ',
                'data.lab_id#nomad_ikz_plugin.movpe.schema.GrowthMovpeIKZ',
                'data.recipe_id#nomad_ikz_plugin.movpe.schema.GrowthMovpeIKZ',
            ],
            options={
                'data.name#nomad_ikz_plugin.movpe.schema.GrowthMovpeIKZ': Column(),
                'data.datetime#nomad_ikz_plugin.movpe.schema.GrowthMovpeIKZ': Column(
                    label='Start Time'
                ),
                'data.lab_id#nomad_ikz_plugin.movpe.schema.GrowthMovpeIKZ': Column(
                    label='Growth Run ID'
                ),
                'data.recipe_id#nomad_ikz_plugin.movpe.schema.GrowthMovpeIKZ': Column(),
            },
        ),
        filter_menus=FilterMenus(
            options={
                'material': FilterMenu(label='Material'),
                'eln': FilterMenu(label='Electronic Lab Notebook'),
                'custom_quantities': FilterMenu(label='User Defined Quantities'),
                'author': FilterMenu(label='Author / Origin / Dataset'),
                'metadata': FilterMenu(label='Visibility / IDs / Schema'),
            }
        ),
        filters=Filters(
            include=['*#nomad_ikz_plugin.movpe.schema.GrowthMovpeIKZ'],
        ),
        filters_locked={
            'section_defs.definition_qualified_name': [
                'nomad_ikz_plugin.movpe.schema.GrowthMovpeIKZ',
            ],
        },
    ),
)


movpelayersapp = AppEntryPoint(
    name='MOVPELayersApp',
    description='Explore MOVPE Layers.',
    app=App(
        label='MOVPE Layers',
        path='movpelayersapp',
        category='MOVPE',
        columns=Columns(
            selected=[
                'data.name#nomad_ikz_plugin.movpe.schema.ThinFilmMovpeIKZ',
                'data.lab_id#nomad_ikz_plugin.movpe.schema.ThinFilmMovpeIKZ',
                'data.datetime#nomad_ikz_plugin.movpe.schema.ThinFilmMovpeIKZ',
            ],
            options={
                'data.name#nomad_ikz_plugin.movpe.schema.ThinFilmMovpeIKZ': Column(),
                'data.lab_id#nomad_ikz_plugin.movpe.schema.ThinFilmMovpeIKZ': Column(),
                'data.datetime#nomad_ikz_plugin.movpe.schema.ThinFilmMovpeIKZ': Column(),
                'data.description#nomad_ikz_plugin.movpe.schema.ThinFilmMovpeIKZ': Column(),
            },
        ),
        filter_menus=FilterMenus(
            options={
                'material': FilterMenu(label='Material'),
                'eln': FilterMenu(label='Electronic Lab Notebook'),
                'custom_quantities': FilterMenu(label='User Defined Quantities'),
                'author': FilterMenu(label='Author / Origin / Dataset'),
                'metadata': FilterMenu(label='Visibility / IDs / Schema'),
            }
        ),
        filters=Filters(
            include=['*#nomad_ikz_plugin.movpe.schema.ThinFilmMovpeIKZ'],
        ),
        filters_locked={
            'section_defs.definition_qualified_name': [
                'nomad_ikz_plugin.movpe.schema.ThinFilmMovpeIKZ',
            ],
        },
    ),
)
