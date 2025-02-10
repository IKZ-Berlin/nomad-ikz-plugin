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

import pandas as pd
from nomad.datamodel.data import (
    EntryData,
)
from nomad.datamodel.datamodel import EntryArchive, EntryMetadata
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)
from nomad.datamodel.metainfo.basesections import (
    PubChemPureSubstanceSection,
    PureSubstanceComponent,
    PureSubstanceSection,
)
from nomad.metainfo import (
    Quantity,
    Section,
)
from nomad.parsing import MatchingParser
from nomad.units import ureg
from nomad.utils import hash
from nomad_material_processing.general import (
    SubstrateReference,
    ThinFilmReference,
)
from nomad_material_processing.vapor_deposition.cvd.general import (
    FlashEvaporator,
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

from nomad_ikz_plugin.general.schema import (
    LiquidComponent,
    Solution,
)
from nomad_ikz_plugin.movpe.schema import (
    ChamberEnvironmentMovpe,
    ExperimentMovpeIKZ,
    FilamentTemperature,
    GrowthMovpeIKZ,
    GrowthMovpeIKZReference,
    GrowthStepMovpe1IKZ,
    PrecursorsPreparationIKZ,
    PrecursorsPreparationIKZReference,
    SampleParametersMovpe,
    ShaftTemperature,
    SystemComponentIKZ,
    ThinFilmMovpeIKZ,
    ThinFilmStackMovpe,
    ThinFilmStackMovpeReference,
)
from nomad_ikz_plugin.utils import (
    clean_dataframe_headers,
    create_archive,
    get_hash_ref,
    row_timeseries,
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

        process_data = GrowthMovpeIKZ()

        with open(mainfile, 'r') as file:
            step_number = file.readline().split()[0]
            duration = file.readline().split()
            file.readline()
            for step in range(int(step_number)):
                process_step_data = GrowthStepMovpe1IKZ(
                    sources=[],
                    environment=ChamberEnvironmentMovpe(),
                    duration=int(duration[step])
                )
                process_step_data.m_add_sub_section(
                    GrowthStepMovpe1IKZ.sample_parameters, SampleParametersMovpe())
                process_data.m_add_sub_section(GrowthMovpeIKZ.steps, 
                                               process_step_data)
            while True:
                header = file.readline().split()
                value = file.readline().split()
                ramp = file.readline().split() # not used
                state = file.readline().split() # 0=ON, 1=OFF, 2=VENT
                if not header or not value or not ramp or not state:
                    break
                if header[0] == '3':
                    for step in range(int(step_number)):
                        process_data.steps[step].environment.uniform_gas_flow_rate = VolumetricFlowRate(
                            value=[ureg.Quantity(
                                    float(value[step]),
                                    ureg('centimeter ** 3 / minute'),
                    )]
                        )
        process_filename = f'{mainfile.split("/")[-1]}.archive.{filetype}'
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
