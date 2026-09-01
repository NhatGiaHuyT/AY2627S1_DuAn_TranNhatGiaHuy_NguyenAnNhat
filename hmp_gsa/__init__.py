import importlib
import sys

# Keep the legacy top-level import paths and the package paths pointing at the
# same objects so identity checks in the existing tests remain valid.
package_aliases = {
    "modules": "hmp_gsa.modules",
    "experiments": "hmp_gsa.experiments",
    "configs": "hmp_gsa.configs",
    "scripts": "hmp_gsa.scripts",
}
for alias, fullname in package_aliases.items():
    sys.modules.setdefault(alias, importlib.import_module(fullname))

for module_name in [
    "modules.control_group",
    "modules.variants",
    "modules.subset",
    "modules.models",
    "experiments.landscapes",
    "experiments.models",
    "configs.settings",
    "scripts.demo",
]:
    real_name = module_name.replace("modules.", "hmp_gsa.modules.", 1)
    real_name = real_name.replace("experiments.", "hmp_gsa.experiments.", 1)
    real_name = real_name.replace("configs.", "hmp_gsa.configs.", 1)
    real_name = real_name.replace("scripts.", "hmp_gsa.scripts.", 1)
    sys.modules.setdefault(module_name, importlib.import_module(real_name))

try:
    from .experiments.gsa import VARIANTS, run_search
except ModuleNotFoundError:
    from experiments.gsa import VARIANTS, run_search

__all__ = ["VARIANTS", "run_search"]
