# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from types import ModuleType, SimpleNamespace

import pytest

import gr00t.security as security


def _fake_importer(modules):
    def _import(name):
        if name in modules:
            return modules[name]
        raise ImportError(name)

    return _import


def test_blocks_vulnerable_transformers_when_kernels_is_installed(monkeypatch):
    monkeypatch.setattr(
        security.importlib,
        "import_module",
        _fake_importer(
            {
                "transformers": SimpleNamespace(__version__="4.57.3"),
                "kernels": ModuleType("kernels"),
            }
        ),
    )

    with pytest.raises(RuntimeError, match="CVE-2026-4372"):
        security.reject_vulnerable_transformers_kernel_loader()


def test_allows_fixed_transformers_with_kernels(monkeypatch):
    monkeypatch.setattr(
        security.importlib,
        "import_module",
        _fake_importer(
            {
                "transformers": SimpleNamespace(__version__="5.3.0"),
                "kernels": ModuleType("kernels"),
            }
        ),
    )

    security.reject_vulnerable_transformers_kernel_loader()


def test_preserves_compatibility_when_optional_kernels_is_absent(monkeypatch):
    monkeypatch.setattr(
        security.importlib,
        "import_module",
        _fake_importer({"transformers": SimpleNamespace(__version__="4.57.3")}),
    )

    security.reject_vulnerable_transformers_kernel_loader()
