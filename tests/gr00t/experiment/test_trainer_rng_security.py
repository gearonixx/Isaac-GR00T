# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import ast
from pathlib import Path


def _trainer_class() -> ast.ClassDef:
    source = next(
        parent / "gr00t" / "experiment" / "trainer.py"
        for parent in Path(__file__).resolve().parents
        if (parent / "gr00t" / "experiment" / "trainer.py").exists()
    )
    tree = ast.parse(source.read_text())
    return next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Gr00tTrainer")


def test_rng_loader_has_no_unrestricted_torch_load():
    method = next(
        node
        for node in _trainer_class().body
        if isinstance(node, ast.FunctionDef) and node.name == "_load_rng_state"
    )
    loads = [
        node
        for node in ast.walk(method)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "torch"
        and node.func.attr == "load"
    ]
    assert len(loads) == 1
    assert any(
        keyword.arg == "weights_only"
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value is True
        for keyword in loads[0].keywords
    )
