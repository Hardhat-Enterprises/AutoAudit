"""The PowerShell service must stay importable on the interpreter it ships with.

The defect these exist to prevent was real and shipped. ``main.py`` carried

    _EXECUTION_POOL: ThreadPoolExecutor | None = None

at module level. Every other Python in this repository runs on 3.11, but
``engine/powershell/Dockerfile`` builds on ``mcr.microsoft.com/powershell:7.5-
mariner-2.0`` and installs Mariner's ``python3``, which is 3.9. A module-level
annotation is evaluated at import, so PEP 604 raised ``TypeError: unsupported
operand type(s) for |`` before uvicorn could bind, the container crash-looped,
and ``docker-compose.production.yml`` gives the worker
``depends_on: powershell-service: {condition: service_healthy}`` -- so the
worker never started either and the production topology could not run a scan.

Nothing caught it: no CI job builds or starts this image, the engine test suite
runs on 3.11 where the annotation is legal, and ``opa``/``ruff`` have no opinion
about it. This module is the cheap static half of that gap. The end-to-end half
is the six-service overlay smoke.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SERVICE_DIR = ROOT / "engine" / "powershell" / "service"
POWERSHELL_DOCKERFILE = ROOT / "engine" / "powershell" / "Dockerfile"
SERVICE_PYPROJECT = SERVICE_DIR / "pyproject.toml"

# The floor is set by the base image, not by preference: Mariner 2.0's python3.
PYTHON_FLOOR = (3, 9)


def _service_modules() -> list[Path]:
    modules = sorted(SERVICE_DIR.glob("*.py"))
    assert modules, f"no modules found under {SERVICE_DIR}"
    return modules


def _has_postponed_annotations(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            if any(alias.name == "annotations" for alias in node.names):
                return True
    return False


def _annotations(tree: ast.Module):
    """Yield (node, annotation) for every annotation evaluated at import time."""
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and node.annotation is not None:
            yield node, node.annotation
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is not None:
                yield node, node.returns
            args = node.args
            for arg in (
                args.posonlyargs
                + args.args
                + args.kwonlyargs
                + [args.vararg, args.kwarg]
            ):
                if arg is not None and arg.annotation is not None:
                    yield node, arg.annotation


def _pep604_lines(annotation: ast.expr) -> list[int]:
    return sorted(
        {
            child.lineno
            for child in ast.walk(annotation)
            if isinstance(child, ast.BinOp) and isinstance(child.op, ast.BitOr)
        }
    )


@pytest.mark.parametrize("module", _service_modules(), ids=lambda p: p.name)
def test_service_module_parses_on_the_image_interpreter(module: Path) -> None:
    """Reject syntax the image's interpreter cannot even parse."""
    source = module.read_text()
    try:
        ast.parse(source, filename=str(module), feature_version=PYTHON_FLOOR)
    except SyntaxError as error:  # pragma: no cover - only on a real regression
        pytest.fail(
            f"{module.relative_to(ROOT)} does not parse on Python "
            f"{'.'.join(map(str, PYTHON_FLOOR))}: {error}"
        )


@pytest.mark.parametrize("module", _service_modules(), ids=lambda p: p.name)
def test_service_module_has_no_runtime_evaluated_pep604(module: Path) -> None:
    """PEP 604 in an annotation that is evaluated at import breaks on 3.9.

    ``X | Y`` parses everywhere; it fails when the annotation is *evaluated*,
    which is at import unless the module postpones evaluation. A module that
    opts into ``from __future__ import annotations`` is exempt, because its
    annotations become strings that nothing here resolves at runtime.
    """
    source = module.read_text()
    tree = ast.parse(source, filename=str(module))
    if _has_postponed_annotations(tree):
        pytest.skip(f"{module.name} postpones annotation evaluation")

    offenders = []
    for node, annotation in _annotations(tree):
        for line in _pep604_lines(annotation):
            offenders.append(f"{module.relative_to(ROOT)}:{line}")
    assert not offenders, (
        "PEP 604 unions are evaluated at import and raise TypeError on Python "
        f"{'.'.join(map(str, PYTHON_FLOOR))}, which is what "
        "engine/powershell/Dockerfile installs. Use typing.Optional/Union, or "
        "add `from __future__ import annotations` if nothing resolves these at "
        f"runtime. Offending annotations: {offenders}"
    )


def test_declared_floor_matches_the_image() -> None:
    """The declared floor, the gate above and the Dockerfile must agree."""
    pyproject = SERVICE_PYPROJECT.read_text()
    floor = ".".join(map(str, PYTHON_FLOOR))
    assert f'requires-python = ">={floor}"' in pyproject, (
        f"{SERVICE_PYPROJECT.relative_to(ROOT)} must declare the floor this "
        "module enforces"
    )
    dockerfile = POWERSHELL_DOCKERFILE.read_text()
    assert "mariner-2.0" in dockerfile, (
        "The floor is Mariner 2.0's python3. If the base image changes, "
        "re-derive PYTHON_FLOOR from the new image rather than editing it to "
        "match whatever the code happens to need."
    )
    assert "tdnf install -y python3" in dockerfile, (
        "The service runs the distribution python3; if that changed to a pinned "
        "interpreter, this gate needs to follow it."
    )
