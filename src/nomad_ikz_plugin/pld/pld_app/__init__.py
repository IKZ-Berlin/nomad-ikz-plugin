import yaml
from nomad.config.models.plugins import AppEntryPoint

pld_layers_app = AppEntryPoint(
    name='PLD Layers App',
    description='Search for layers made by PLD.',
    app= yaml.safe_load(
    '''
        label: PLD Layers
        filters:
          include:
            - '*#nomad_ikz_plugin.pld.schema.*'
        # Path used in the URL, must be unique
        path: 'nomad_ikz_plugin/pld'
        # Used to categorize apps in the explore menu
        category: 'Experiment'
        # Brief description used in the app menu
        description: 'Search for layers made by PLD'
        # Longer description that can also use markdown
        readme: 'This app is for the analysis of PLD data.'
        # Controls which columns are shown in the results table
        columns:
          selected:
            - entry_name
            - results.material.elements
            - data.process_conditions.number_of_pulses#nomad_ikz_plugin.pld.schema.IKZPLDLayer
            - data.process_conditions.pressure#nomad_ikz_plugin.pld.schema.IKZPLDLayer
            - data.process_conditions.laser_energy#nomad_ikz_plugin.pld.schema.IKZPLDLayer
            - data.process_conditions.growth_temperature#nomad_ikz_plugin.pld.schema.IKZPLDLayer
            - data.process_conditions.laser_repetition_rate#nomad_ikz_plugin.pld.schema.IKZPLDLayer
            - data.process_conditions.sample_to_target_distance#nomad_ikz_plugin.pld.schema.IKZPLDLayer
            - data.geometry.height#nomad_ikz_plugin.pld.schema.IKZPLDLayer
          options:
            entry_name:
              label: 'Layer name'
              align: 'left'
            entry_type:
              label: 'Entry type'
              align: 'left'
            upload_create_time:
              label: 'Upload time'
              align: 'left'
            entry_create_time:
              label: 'Entry time'
              align: 'left'
            authors:
              label: 'Authors'
              align: 'left'
            results.material.elements:
              label: 'Elements'
              align: 'left'
            data.process_conditions.number_of_pulses#nomad_ikz_plugin.pld.schema.IKZPLDLayer:
              label: 'Number of pulses'
              align: 'left'
            data.process_conditions.pressure#nomad_ikz_plugin.pld.schema.IKZPLDLayer:
              label: 'Pressure'
              align: 'left'
              unit: 'mbar'
              format:
                decimals: 2
                mode: 'scientific'
            data.process_conditions.laser_energy#nomad_ikz_plugin.pld.schema.IKZPLDLayer:
              label: 'Laser energy'
              align: 'left'
              unit: 'mJ'
              format:
                decimals: 2
                mode: 'scientific'
            data.process_conditions.growth_temperature#nomad_ikz_plugin.pld.schema.IKZPLDLayer:
              label: 'Growth temperature'
              align: 'left'
              unit: 'celsius'
              format:
                decimals: 2
                mode: 'scientific'
            data.process_conditions.laser_repetition_rate#nomad_ikz_plugin.pld.schema.IKZPLDLayer:
              label: 'Laser repetition rate'
              align: 'left'
              unit: 'Hz'
              format:
                decimals: 2
                mode: 'scientific'
            data.process_conditions.sample_to_target_distance#nomad_ikz_plugin.pld.schema.IKZPLDLayer:
              label: 'Sample to target distance'
              align: 'left'
              unit: 'mm'
              format:
                decimals: 2
                mode: 'scientific'
            data.geometry.height#nomad_ikz_plugin.pld.schema.IKZPLDLayer:
              label: 'Layer thickness'
              align: 'left'
              unit: 'nm'
              format:
                decimals: 2
                mode: 'scientific'
        filters_locked:
          section_defs.definition_qualified_name: nomad_ikz_plugin.pld.schema.IKZPLDLayer
        filter_menus:
          options:
            material:
              label: 'Material'
              level: 0
            elements:
              label: 'Elements / Formula'
              level: 1
              size: 'xl'
            eln:
              label: 'Electronic Lab Notebook'
              level: 0
            custom_quantities:
              label: 'User Defined Quantities'
              level: 0
              size: 'l'
            author:
              label: 'Author / Origin / Dataset'
              level: 0
              size: 'm'
            metadata:
              label: 'Visibility / IDs / Schema'
              level: 0
        dashboard:
          widgets:
          - type: histogram
            showinput: true
            autorange: false
            nbins: 30
            scale: linear
            quantity: data.process_conditions.number_of_pulses#nomad_ikz_plugin.pld.schema.IKZPLDLayer
            layout:
              xxl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 0
                x: 0
              xl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 0
                x: 0
              lg:
                minH: 3
                minW: 3
                h: 4
                w: 12
                y: 4
                x: 12
              md:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 0
                x: 0
              sm:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 0
                x: 0
          - type: histogram
            showinput: true
            autorange: false
            nbins: 30
            scale: linear
            x:
              search_quantity: data.process_conditions.pressure#nomad_ikz_plugin.pld.schema.IKZPLDLayer
              unit: mbar
            layout:
              xxl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 0
                x: 8
              xl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 0
                x: 8
              lg:
                minH: 3
                minW: 3
                h: 4
                w: 12
                y: 8
                x: 12
              md:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 0
                x: 8
              sm:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 3
                x: 0
          - type: histogram
            showinput: true
            autorange: false
            nbins: 30
            scale: linear
            x:
              search_quantity: data.process_conditions.laser_energy#nomad_ikz_plugin.pld.schema.IKZPLDLayer
              unit: mJ
            layout:
              xxl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 0
                x: 16
              xl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 0
                x: 16
              lg:
                minH: 3
                minW: 3
                h: 4
                w: 12
                y: 16
                x: 12
              md:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 3
                x: 0
              sm:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 6
                x: 0
          - type: histogram
            showinput: true
            autorange: false
            nbins: 30
            scale: linear
            x:
              search_quantity: data.process_conditions.growth_temperature#nomad_ikz_plugin.pld.schema.IKZPLDLayer
              unit: celsius
            layout:
              xxl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 0
                x: 24
              xl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 3
                x: 0
              lg:
                minH: 3
                minW: 3
                h: 4
                w: 12
                y: 20
                x: 12
              md:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 6
                x: 0
              sm:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 9
                x: 0
          - type: histogram
            showinput: true
            autorange: false
            nbins: 30
            scale: linear
            x: 
              search_quantity: data.process_conditions.laser_repetition_rate#nomad_ikz_plugin.pld.schema.IKZPLDLayer
              unit: Hz
            layout:
              xxl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 3
                x: 0
              xl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 6
                x: 0
              lg:
                minH: 3
                minW: 3
                h: 4
                w: 12
                y: 12
                x: 12
              md:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 9
                x: 0
              sm:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 12
                x: 0
          - type: histogram
            showinput: true
            autorange: false
            nbins: 30
            scale: linear
            x:
              search_quantity: data.process_conditions.sample_to_target_distance#nomad_ikz_plugin.pld.schema.IKZPLDLayer
              unit: mm
            layout:
              xxl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 6
                x: 0
              xl:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 9
                x: 0
              lg:
                minH: 3
                minW: 3
                h: 4
                w: 12
                y: 0
                x: 12
              md:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 12
                x: 0
              sm:
                minH: 3
                minW: 3
                h: 3
                w: 8
                y: 15
                x: 0
          - type: scatterplot
            autorange: true
            size: 1000
            markers:
              color:
                search_quantity: data.process_conditions.sample_to_target_distance#nomad_ikz_plugin.pld.schema.IKZPLDLayer
                unit: mm
                scale: linear
            y: 
              search_quantity: data.geometry.height#nomad_ikz_plugin.pld.schema.IKZPLDLayer
              unit: nm
            x: data.process_conditions.number_of_pulses#nomad_ikz_plugin.pld.schema.IKZPLDLayer
            layout:
              xxl:
                minH: 3
                minW: 3
                h: 6
                w: 9
                y: 0
                x: 0
              xl:
                minH: 3
                minW: 3
                h: 6
                w: 9
                y: 0
                x: 0
              lg:
                minH: 3
                minW: 3
                h: 7
                w: 12
                y: 10
                x: 0
              md:
                minH: 3
                minW: 3
                h: 6
                w: 9
                y: 3
                x: 8
              sm:
                minH: 3
                minW: 3
                h: 6
                w: 9
                y: 18
                x: 0
          - type: scatterplot
            autorange: true
            size: 1000
            color: data.process_conditions.number_of_pulses#nomad_ikz_plugin.pld.schema.IKZPLDLayer
            y: 
              search_quantity: data.geometry.height#nomad_ikz_plugin.pld.schema.IKZPLDLayer
              unit: nm
            x: 
              search_quantity: data.process_conditions.sample_to_target_distance#nomad_ikz_plugin.pld.schema.IKZPLDLayer
              unit: mm
            layout:
              xxl:
                minH: 3
                minW: 3
                h: 6
                w: 9
                y: 0
                x: 0
              xl:
                minH: 3
                minW: 3
                h: 6
                w: 9
                y: 0
                x: 0
              lg:
                minH: 3
                minW: 3
                h: 7
                w: 12
                y: 17
                x: 0
              md:
                minH: 3
                minW: 3
                h: 6
                w: 9
                y: 9
                x: 8
              sm:
                minH: 3
                minW: 3
                h: 6
                w: 9
                y: 24
                x: 0
          - type: periodictable
            scale: linear
            quantity: results.material.elements
            layout:
              xxl:
                minH: 3
                minW: 3
                h: 9
                w: 12
                y: 0
                x: 0
              xl:
                minH: 3
                minW: 3
                h: 9
                w: 12
                y: 0
                x: 0
              lg:
                minH: 3
                minW: 3
                h: 10
                w: 12
                y: 0
                x: 0
              md:
                minH: 3
                minW: 3
                h: 9
                w: 12
                y: 0
                x: 0
              sm:
                minH: 3
                minW: 3
                h: 9
                w: 12
                y: 0
                x: 0
'''


))
