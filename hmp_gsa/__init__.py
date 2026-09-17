import importlib
import sys

# Keep the legacy top-level import paths and the package paths pointing at the
# same objects so identity checks in the existing tests remain valid.
package_aliases = {
    "modules": "hmp_gsa.modules",
    "experiments": "hmp_gsa.experiments",
    "configs": "hmp_gsa.configs",
}
for alias, fullname in package_aliases.items():
    sys.modules.setdefault(alias, importlib.import_module(fullname))

for module_name in [
    "modules.variants",
    "modules.models",
    "configs.settings",
]:
    real_name = module_name.replace("modules.", "hmp_gsa.modules.", 1)
    real_name = real_name.replace("experiments.", "hmp_gsa.experiments.", 1)
    real_name = real_name.replace("configs.", "hmp_gsa.configs.", 1)
    sys.modules.setdefault(module_name, importlib.import_module(real_name))


__all__ = ["VARIANTS", "run_search"]
