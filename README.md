# IKZ Plugin

This directory contains a plugin called `nomad-ikz-plugin` designed for the IKZ institute.

This a python package that contains several subpackages for each technique.

Check the README within each subfolder for more deatils on each technique.

## Structure

The directory tree:

```bash
nomad-ikz-plugin/
├── src
│   └── nomad-ikz-plugin
│       ├── general
│       ├── characterization
│       ├── czochralski
│       ├── directional_solidification
│       ├── pld
│       ├── mbe
│       └── movpe
└── tests
    └── data
        ├── czochralski
        ├── directional_solidification
        ├── pld
        ├── mbe
        └── movpe
```

- `src/`: contains the source code for the plugins.
- `tests/`: contains tests for the plugins.

## Installation

To use this plugin you need to install several dependent packages.

There are at least two ways of installing them, depending on your aim:

- Deploy a custom NOMAD Oasis image.
  Refer to the [IKZ NOMAD Oasis custom image](https://github.com/IKZ-Berlin/nomad-oasis-ikz/tree/main) to discover how the `pyproject.toml` is composed.
  If you are using some plugins in your Oasis deployment that are also dependencies of this plugin, make sure to have compatible version tags. To do this, you will need the following lines in your Oasis deployment's `pyproject.toml`:

  ```bash
  [project.optional-dependencies]
  plugins = [
    "nomad-material-processing @ git+https://github.com/FAIRmat-NFDI/nomad-material-processing.git@<desired_commit_id>",
    "nomad-measurements @ git+https://github.com/FAIRmat-NFDI/nomad-measurements.git@<desired_commit_id>",
    "nomad-analysis @ git+https://github.com/FAIRmat-NFDI/nomad-analysis.git@<desired_commit_id>",
    "nomad-ikz-plugin",
    "uv_vis_nir_transmission @ git+https://github.com/FAIRmat-NFDI/AreaA-data_modeling_and_schemas.git@<desired_commit_id>#subdirectory=transmission/transmission_plugin/uv_vis_nir_transmission_plugin",
    "lakeshore-nomad-plugin @ git+https://github.com/IKZ-Berlin/lakeshore-nomad-plugin.git@<desired_commit_id>",
    "laytec_epitt_plugin @ git+https://github.com/IKZ-Berlin/laytec_epitt_nomad_plugin.git@<desired_commit_id>",
    "statsmodels" 
    ]
    [tool.uv.sources]
    nomad-ikz-plugin = { git = "https://github.com/IKZ-Berlin/nomad-ikz-plugin.git", rev = "v0.1.2" }
  ```
  
> [!NOTE]
> the toml above shows that the `nomad-ikz-plugin` is not bound to a commit, rather to a release

- Develop the plugin in your development environment.
  Refer to the [nomad-distro-dev repository](https://github.com/FAIRmat-NFDI/nomad-distro-dev) to setup your environment.
  You will then need to add all the dependencies as submodules and also to use the uv command `add` to have them in your python env.

  ```bash
  git submodule add https://github.com/FAIRmat-NFDI/nomad-measurements packages/nomad-measurements
  git submodule add https://github.com/FAIRmat-NFDI/nomad-material-processing packages/nomad-material-processing
  git submodule add https://github.com/IKZ-Berlin/nomad-ikz-plugin packages/nomad-ikz-plugin
  git submodule add https://github.com/IKZ-Berlin/laytec_epitt_nomad_plugin packages/laytec_epitt_nomad_plugin
  git submodule add https://github.com/IKZ-Berlin/lakeshore-nomad-plugin packages/lakeshore-nomad-plugin
  git submodule update --init --recursive
  uv add packages/nomad-ikz-plugin
  uv add packages/lakeshore-nomad-plugin
  uv add packages/laytec_epitt_nomad_plugin
  uv add packages/nomad-measurements
  uv add packages/nomad-material-processing 
  ```

For more details on what happens in this plugin under the hood, check the `.toml` file in the `nomad-ikz-plugin` folder:

- all the installed subpackages are listed under the section `[project.entry-points.'nomad.plugin']`.
- `dependencies` and `[project.optional-dependencies]` contain all the other packages installed along to this one.

## Usage

You need to copy and fill the tabular files in `tests/data` folder, then drag and drop them into a new NOMAD upload.

Please refer to the README.md file in each subdirectory for more information about each plugin.

## Development

### Clone your fork

Follow the github instructions. The URL and directory depends on your user name or organization and the
project name you choose. But, it should look somewhat like this:

```
git clone git@github.com:markus1978/my-nomad-schema.git
cd my-nomad-schema
```

### Install the dependencies

You should create a virtual environment. You will need the `nomad-lab` package (and `pytest`).

```sh
python3 -m venv .pyenv
source .pyenv/bin/activate
pip install -r requirements.txt --index-url https://gitlab.mpcdf.mpg.de/api/v4/projects/2187/packages/pypi/simple
```

to ensure installation of all the packages required, make sure in to install:

```sh
pip install nomad-lab[parsing, infrastructure]
```

### Run the tests

Make sure the current directory is in your path:

```sh
export PYTHONPATH=.
```

You can run automated tests with `pytest`:

```sh
pytest -svx tests
```

You can parse an example archive that uses the schema with `nomad` command
(installed via `nomad-lab` Python package):

```sh
nomad parse tests/data/test.archive.yaml --show-archive
```

### Developing your schema

Refer to official NOMAD docs to learn how to develop schemas and parsers and plugins, how to add them to an Oasis, how to publish them: <https://nomad-lab/prod/v1/staging/docs/plugins.html>
