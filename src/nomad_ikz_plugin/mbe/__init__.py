from nomad.config.models.plugins import SchemaPackageEntryPoint
from pydantic import Field


class MbeEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_ikz_plugin.mbe.schema import m_package

        return m_package


schema = MbeEntryPoint(
    name='MbeSchema',
    description='Schema package for Molecular Beam Epitaxy (MBE) definitions.',
)
