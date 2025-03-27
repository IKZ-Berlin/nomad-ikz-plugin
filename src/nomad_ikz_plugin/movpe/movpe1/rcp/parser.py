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

from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.datamodel import EntryArchive
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    PureSubstanceSection,
)
from nomad.metainfo import (
    Quantity,
    Section,
)
from nomad.parsing import MatchingParser
from nomad.units import ureg
from nomad_material_processing.vapor_deposition.cvd.general import (
    FlashSource,
    GasLineEvaporator,
    GasLineSource,
    Rotation,
)
from nomad_material_processing.vapor_deposition.general import (
    Pressure,
    Temperature,
    VolumetricFlowRate,
)

from nomad_ikz_plugin.movpe.schema import (
    ChamberEnvironmentMovpe,
    FilamentTemperature,
    FlashEvaporatorIKZ,
    GrowthMovpeIKZ,
    GrowthStepMovpeIKZ,
    SampleParametersMovpe,
    ShaftTemperature,
)
from nomad_ikz_plugin.utils import (
    create_archive,
)


class RcpFileMovpe1(EntryData):
    m_def = Section(
        a_eln=None,
        label='Raw File Growth Run Deposition Control',
    )
    name = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            component='StringEditQuantity',
        ),
    )
    recipe_file = Quantity(
        type=str,
        a_browser={'adaptor': 'RawFileAdaptor'},
    )


class ParserMovpe1RcpIKZ(MatchingParser):
    def parse(self, mainfile: str, archive: EntryArchive, logger) -> None:
        filetype = 'yaml'

        # check the correctness of the file location in the uploaded zip folder
        assert mainfile.split('/')[-2] == 'Software file', (
            f"Expected 'Software file' folder in '{mainfile.split('/')[-3]}',"
            f"got '{mainfile.split('/')[-2]}'"
        )
        logger.info(
            f"Processing MOVPE 1 recipe file in folder '{mainfile.split('/')[-3]}'"
        )

        process_data = GrowthMovpeIKZ(
            name=mainfile.split('/')[-3],
            lab_id=mainfile.split('/')[-3],
            description=f"parsed from recipe file '{mainfile.split('/')[-1]}'",
        )

        with open(mainfile, encoding='utf-8') as file:
            total_steps = file.readline().split()[0]
            duration = file.readline().split()
            set_recipe_time = [0]
            file.readline()
            for step in range(int(total_steps)):
                set_recipe_time.append(set_recipe_time[step] + int(duration[step]))
                process_step_data = GrowthStepMovpeIKZ(
                    sources=[
                        GasLineSource(
                            name='Oxygen',
                            vapor_source=GasLineEvaporator(
                                total_flow_rate=VolumetricFlowRate(),
                            ),
                        ),
                        FlashSource(
                            name='Flash Evap. 1',
                            vapor_source=FlashEvaporatorIKZ(
                                carrier_gas=PureSubstanceSection(
                                    name='Argon',
                                ),
                                carrier_push_flow_rate=VolumetricFlowRate(),
                                carrier_purge_flow_rate=VolumetricFlowRate(),
                            ),
                        ),
                        FlashSource(
                            name='Flash Evap. 2',
                            vapor_source=FlashEvaporatorIKZ(
                                carrier_gas=PureSubstanceSection(
                                    name='Argon',
                                ),
                                carrier_push_flow_rate=VolumetricFlowRate(),
                                carrier_purge_flow_rate=VolumetricFlowRate(),
                            ),
                        ),
                    ],
                    environment=ChamberEnvironmentMovpe(),
                    sample_parameters=[SampleParametersMovpe()],
                    duration=int(duration[step]),
                    step_index=step + 1,
                )
                process_data.m_add_sub_section(GrowthMovpeIKZ.steps, process_step_data)

            line = file.readline()
            while line != '':
                header = (
                    line.split()
                )  # a new line it is read at the bottom of the loop!
                value = [float(element) / 10 for element in file.readline().split()]
                ramp = file.readline().split()  # not used
                state = file.readline().split()  # 0=ON, 1=OFF, 2=VENT
                if not header or not value or not ramp or not state:
                    break
                if header[0] == '3':
                    for step in range(int(total_steps)):
                        process_data.steps[
                            step
                        ].environment.uniform_gas_flow_rate = VolumetricFlowRate(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('centimeter ** 3 / minute'),
                                )
                            ],
                        )
                elif header[0] == '6':  # O2 GasLineSource
                    for step in range(int(total_steps)):
                        process_data.steps[step].sources[
                            0
                        ].vapor_source.total_flow_rate = VolumetricFlowRate(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('centimeter ** 3 / minute'),
                                )
                            ],
                        )
                elif header[0] == '9':  # flash evap no. 1
                    for step in range(int(total_steps)):
                        process_data.steps[step].sources[
                            1
                        ].vapor_source.carrier_push_flow_rate = VolumetricFlowRate(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('centimeter ** 3 / minute'),
                                )
                            ],
                        )
                elif header[0] == '12':  # flash evap no. 1
                    for step in range(int(total_steps)):
                        process_data.steps[step].sources[
                            1
                        ].vapor_source.carrier_purge_flow_rate = VolumetricFlowRate(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('centimeter ** 3 / minute'),
                                )
                            ],
                        )
                elif header[0] == '28':  # flash evap no. 2
                    for step in range(int(total_steps)):
                        process_data.steps[step].sources[
                            2
                        ].vapor_source.carrier_push_flow_rate = VolumetricFlowRate(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('centimeter ** 3 / minute'),
                                )
                            ],
                        )
                elif header[0] == '31':  # flash evap no. 2
                    for step in range(int(total_steps)):
                        process_data.steps[step].sources[
                            2
                        ].vapor_source.carrier_purge_flow_rate = VolumetricFlowRate(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('centimeter ** 3 / minute'),
                                )
                            ],
                        )
                elif header[0] == '36':  # peristaltic pump no. 2: Ca - Sr - Ba
                    for step in range(int(total_steps)):
                        process_data.steps[step].sources[
                            2
                        ].peristaltic_pump_flux = VolumetricFlowRate(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('centimeter ** 3 / minute'),
                                )
                            ],
                        )
                elif header[0] == '34':  # peristaltic pump no. 1: Ti
                    for step in range(int(total_steps)):
                        process_data.steps[step].sources[
                            1
                        ].peristaltic_pump_flux = VolumetricFlowRate(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('centimeter ** 3 / minute'),
                                )
                            ],
                        )
                elif header[0] == '17':  # filament temperature
                    for step in range(int(total_steps)):
                        process_data.steps[step].sample_parameters[
                            0
                        ].filament_temperature = FilamentTemperature(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('celsius'),
                                )
                            ],
                        )
                elif header[0] == '19':  # shaft temperature
                    for step in range(int(total_steps)):
                        process_data.steps[step].sample_parameters[
                            0
                        ].shaft_temperature = ShaftTemperature(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('celsius'),
                                )
                            ],
                        )
                elif header[0] == '21':  # rotation
                    for step in range(int(total_steps)):
                        process_data.steps[step].environment.rotation = Rotation(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('rpm'),
                                )
                            ],
                        )
                elif header[0] == '15':  # FE1 temperature
                    for step in range(int(total_steps)):
                        process_data.steps[step].sources[
                            1
                        ].vapor_source.temperature = Temperature(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('celsius'),
                                )
                            ],
                        )
                elif header[0] == '26':  # FE2 temperature
                    for step in range(int(total_steps)):
                        process_data.steps[step].sources[
                            2
                        ].vapor_source.temperature = Temperature(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('celsius'),
                                )
                            ],
                        )
                elif header[0] == '23':  # chamber pressure
                    for step in range(int(total_steps)):
                        process_data.steps[step].environment.pressure = Pressure(
                            set_time=[
                                ureg.Quantity(
                                    set_recipe_time[step],
                                    ureg.second,
                                )
                            ],
                            set_value=[
                                ureg.Quantity(
                                    float(value[step]),
                                    ureg('mbar'),
                                )
                            ],
                        )

                line = file.readline()

        process_filename = f'{mainfile.split("/")[-1][:-4]}.archive.{filetype}'
        process_archive = EntryArchive(
            data=process_data,
            m_context=archive.m_context,
        )
        create_archive(
            process_archive.m_to_dict(),
            archive.m_context,
            process_filename,
            filetype,
            logger,
        )

        # # create experiment archive
        # experiment_filename = (
        #     f'{dep_control_run}.ExperimentMovpeIKZ.archive.{filetype}'
        # )
        # experiment_archive = EntryArchive(
        #     data=ExperimentMovpeIKZ(
        #         name=f'{dep_control_run} experiment',
        #         method='MOVPE 1 experiment',
        #         lab_id=f'{dep_control_run} experiment',
        #         datetime=dep_control['Date'].loc[index],
        #         precursors_preparation=PrecursorsPreparationIKZReference(
        #             reference=get_hash_ref(
        #                 archive.m_context.upload_id, precursors_filename
        #             ),
        #         ),
        #         # growth_run_constant_parameters=GrowthMovpe1IKZConstantParametersReference(
        #         #     lab_id=dep_control["Constant Parameters ID"].loc[index],
        #         # ),
        #         growth_run=GrowthMovpeIKZReference(
        #             reference=get_hash_ref(
        #                 archive.m_context.upload_id, growth_filename
        #             ),
        #         ),
        #     ),
        #     m_context=archive.m_context,
        #     metadata=EntryMetadata(upload_id=archive.m_context.upload_id),
        # )
        # create_archive(
        #     experiment_archive.m_to_dict(),
        #     archive.m_context,
        #     experiment_filename,
        #     filetype,
        #     logger,
        # )

        # !!! the following code checks if the experiment archive already exists and overwrites it

        # if len(matches["lab_id"]) == 0:
        #     experiment_archive = EntryArchive(
        #         data=ExperimentMovpeIKZ(
        #             lab_id=f"{dep_control_run} experiment",
        #             datetime=dep_control["Date"].loc[index],
        #             precursors_preparation=PrecursorsPreparationIKZReference(
        #                 reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, precursors_filename)}#data",
        #             ),
        #             growth_run_constant_parameters=GrowthMovpe1IKZConstantParametersReference(
        #                 lab_id=dep_control["Constant Parameters ID"][index],
        #             ),
        #             growth_run_deposition_control=growth_data,
        #             grown_sample=ThinFilmStackMovpeReference(
        #                 reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, sample_filename)}#data",
        #             ),
        #         ),
        #         m_context=archive.m_context,
        #         metadata=EntryMetadata(
        #             upload_id=archive.m_context.upload_id
        #         ),
        #     )
        #     create_archive(
        #         experiment_archive.m_to_dict(),
        #         archive.m_context,
        #         experiment_filename,
        #         filetype,
        #         logger,
        #     )
        # elif (
        #     len(matches["lab_id"]) > 0
        #     and matches["entry_name"][0] == experiment_filename
        # ):  # the experiment will be retrieved, extended, and overwritten
        #     from nomad.app.v1.routers.uploads import get_upload_with_read_access

        #     logger.warning(
        #         f"Overwritten existing experiment archive {matches['entry_name'][0]}."
        #     )

        #     experiment_context = ServerContext(
        #         get_upload_with_read_access(
        #             matches["upload_id"][0],
        #             User(
        #                 is_admin=True,
        #                 user_id=archive.metadata.main_author.user_id,
        #             ),
        #             include_others=True,
        #         )
        #     )  # Upload(upload_id=matches["upload_id"][0]))

        #     #     filename =
        #     with experiment_context.raw_file(
        #         experiment_filename, "r"
        #     ) as experiment_file:
        #         updated_experiment = yaml.safe_load(experiment_file)
        #         updated_experiment["data"][
        #             "precursors_preparation"
        #         ] = PrecursorsPreparationIKZReference(
        #             reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, precursors_filename)}#data",
        #         ).m_to_dict()
        #         updated_experiment["data"][
        #             "growth_run_deposition_control"
        #         ] = growth_data.m_to_dict()
        #         updated_experiment["data"]["grown_sample"] = ThinFilmStackMovpeReference(
        #             reference=f"../uploads/{archive.m_context.upload_id}/archive/{hash(archive.m_context.upload_id, sample_filename)}#data",
        #         ).m_to_dict()

        #     create_archive(
        #         updated_experiment,
        #         experiment_context,
        #         experiment_filename,
        #         filetype,
        #         logger,
        #         bypass_check=True,
        #     )

        # populate the raw file archive
        archive.data = RcpFileMovpe1(
            name=mainfile.split('/')[-1], recipe_file=mainfile.split('/')[-1]
        )
