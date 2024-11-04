# MOVPE IKZ Plugin

See also:

[full ikz_plugin README](https://github.com/IKZ-Berlin/nomad-ikz-plugin)

[LayTec README](https://github.com/IKZ-Berlin/laytec_epitt_nomad_plugin)

## Overview

This directory contains the MOVPE IKZ plugin for the NOMAD project.

The MOVPE IKZ plugin is used to parse and process data related to the MOVPE growth process at IKZ.

It is derived from the former yaml schema:[AreaA-data_modeling_and_schemas/movpe_IKZ_Ga2O3](https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas/tree/main/movpe_IKZ_Ga2O3)

## Structure

The directory tree:

```bash
ikz_plugin/
├── nomad.yaml
├── src
│   └── ikz_plugin
│       └── movpe
│           ├── __init__.py
│           ├── schema.py
│           ├── movpe1
│           │   ├── constant_parameters
│           │   │   ├── __init__.py
│           │   │   └── parser.py
│           │   ├── growth_excel
│           │   │   ├── __init__.py
│           │   │   └── parser.py
│           │   └── utils.py
│           ├── movpe2
│           │   ├── growth_excel
│           │   │   ├── __init__.py
│           │   │   └── parser.py
│           │   └── utils.py
│           └── substrate
│               ├── __init__.py
│               ├── parser.py
│               └── utils.py
└── tests
    └── data
        ├── directional_solidification
        │   ├── G1_IKZ_NSI_23.ds.manualprotocol.xlsx <--- template file
        │   ├── G1_IKZ_NSI_23.ds.recipe.xlsx <--- template file
        │   └── G1_IKZ_NSI_23.ds.yaml <--- template file
        ├── movpe
        │   ├── movpe1
        │   │   ├── constant_parameters
        │   │   │   └── constant_parameters.xlsx <--- template file
        │   │   └── growth_excel
        │   │       └── Growth_Control_movpe1.xlsx <--- template file
        │   ├── movpe2
        │   │   └── GaO.growth.movpe.ikz.xlsx <--- template file
        │   └── substrate_parser
        │       └── GaO.substrates.movpe.ikz.xlsx <--- template file
        └── pld
            ├── 26042023_1630-STO-SAO-STO-Alev.dlog <--- template file
            ├── 26042023_1630-STO-SAO-STO-Alev.elog <--- template file
            ├── sao_1.archive.json <--- template file
            ├── sto_1.archive.json <--- template file
            ├── test_ikz_pld_substrate_batch.archive.yaml <--- template file
            └── test_ikz_pulsed_laser_deposition.archive.yaml <--- template file
```

- `src/`: contains the source code of the plugin.
- `tests/`: contains the tests and template file to use with the plugin.
- `movpe1_growth_parser/`: contains the source code for machine "1" at IKZ.
- `movpe2_growth_parser/`: contains the source code for machine "2" at IKZ.
- `substrate_parser/`: contains the source code for substrate parser.
- `schema.py` defines the structure of the data after it has been parsed. It specifies the fields that the structured data will contain and the types of those fields.
- `parser.py` contains the logic for parsing the raw data from the MOVPE growth process. This includes reading the data from its original format, extracting the relevant information, and transforming it into a structured format.
- `nomad_plugin.yaml` defines the raw file matching rules of the parser. Check [NOMAD plugin official docs](https://nomad-lab.eu/prod/v1/staging/docs/howto/customization/plugins_dev.html#parser-plugin-metadata) for more info.

## Usage

- You need to copy and fill the excel files in `tests/data` folder, then drag and drop them into a new NOMAD upload.

- Follow the raw file matching rules in `__init__.py` of each parser. In general, a file must:
  - have specific extension.
  - contain specific column headers.

> [!CAUTION]
> The parser is built to match specific template files. If files extension is changed or they are missing regex matching in the column headers, they might not be recognized by the parsers.

### `movpe1_growth_parser`

This folder contains two files with custom filename and `.xlsx` extension. Download these file if you use the "MOVPE 1" machine at IKZ.

- Upload in your NOMAD Oasis `constant_parameters.xlsx` BEFORE `deposition_control.xlsx` to reference automatically the generated samples in each activity.
Each row is used to record one experiment.

> [!NOTE]
> `deposition_control.xlsx` contains two sheets: "Deposition Control" and "Precursors". Some column header must be present for the file to be parsed: `Constant Parameters ID`, `Sample ID`, `Date`, `number` in "Deposition Control" and `Sample ID` in "Precursors".

- Fill the `Constant Parameters ID` with the same ID you write into the `constant_parameters.xlsx` file, in this way the parameters that remain constant across several experiments will be correctly referenced.
- Generate one row in "Deposition Control" sheet and in "Precursors" sheet for each growth experiment. They refer to the same sample and hence must contain the same unique `Sample ID`. An error will be thrown if the rows in the two sheets contain different `Sample ID` fields.

> [!NOTE]
> After uploading `constant_parameters.xlsx` and `deposition_control.xlsx`, please open `RawFileConstantParameters` and `RawFileDepositionControl` generated entries in NOMAD to check if there is some processing error. Carefully analize any warning or error and upload the file again if needed.

### `movpe2_growth_parser`

This folder contains one file with custom filename and `.growth.movpe.ikz.xlsx` extension. Download these file if you use the "MOVPE 2" machine at IKZ.

### `substrate_parser`

This folder contains one file with custom filename and `.substrates.movpe.ikz.xlsx` extension. Download these files to record info on Substrate used for both "MOVPE 1" and "MOVPE 2" machines at IKZ.

## Installation

to be updated
