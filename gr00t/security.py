# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Small dependency security guards that do not require the ML runtime."""

from __future__ import annotations

import importlib
import re


_TRANSFORMERS_KERNEL_FIX = (5, 3, 0)
_VERSION_PREFIX = re.compile(r"^\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?")


def _parse_version_prefix(version: object) -> tuple[int, int, int] | None:
    match = _VERSION_PREFIX.match(str(version))
    if match is None:
        return None
    return tuple(int(part or 0) for part in match.groups())


def reject_vulnerable_transformers_kernel_loader() -> None:
    """Block the vulnerable Transformers kernel loading path.

    CVE-2026-4372 (GHSA-29pf-2h5f-8g72/PYSEC-2026-2289) is reachable when a
    model config can influence the internal attention implementation and the
    optional ``kernels`` package is installed.  The project does not require
    ``kernels``, so preserve compatibility when it is absent while refusing to
    load an unverified model with the vulnerable combination.
    """
    try:
        transformers = importlib.import_module("transformers")
    except ImportError:
        return

    version = _parse_version_prefix(getattr(transformers, "__version__", ""))
    if version is not None and version >= _TRANSFORMERS_KERNEL_FIX:
        return

    try:
        importlib.import_module("kernels")
    except ImportError:
        return

    if version is None:
        raise RuntimeError(
            "Cannot verify the installed Transformers version while optional "
            "'kernels' is present. Upgrade Transformers to >=5.3.0 before "
            "loading model configs (CVE-2026-4372)."
        )
    raise RuntimeError(
        "Transformers <5.3.0 with optional 'kernels' is unsafe for untrusted "
        "model configs (CVE-2026-4372). Upgrade Transformers to >=5.3.0."
    )
