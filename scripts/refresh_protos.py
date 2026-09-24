#!/usr/bin/env python
"""Vendor galago-tools' .proto files and regenerate the Python stubs.

    python scripts/refresh_protos.py --ref <commit-or-tag>   # fetch + generate
    python scripts/refresh_protos.py                          # regenerate only

The upstream files are copied verbatim into ``proto/galago/`` and the pin is
recorded in ``proto/galago/UPSTREAM.json``. Stubs are generated into
``src/rhylthyme_galago/_gen/`` with their import paths moved under that
package, so they never collide with galago-tools' own top-level ``tools``
package. Proto package names are untouched, so the wire format (and the gRPC
service path ``/com.science.foundry.tools.grpc_interfaces.ToolDriver/...``) is
exactly galago's.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "proto" / "galago"
GEN_PKG = "rhylthyme_galago/_gen"
GEN_DIR = ROOT / "src" / GEN_PKG
UPSTREAM = "https://github.com/sciencecorp/galago-tools.git"
PROTO_SUBDIR = "interfaces/tools/grpc_interfaces"


def fetch(ref: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "clone", "-q", UPSTREAM, tmp], check=True)
        subprocess.run(["git", "-C", tmp, "checkout", "-q", ref], check=True)
        commit = subprocess.run(
            ["git", "-C", tmp, "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        version_file = Path(tmp) / "tools" / "version.py"
        match = re.search(r"__version__ = ['\"]([^'\"]+)", version_file.read_text())
        version = match.group(1) if match else None

        if VENDOR.exists():
            shutil.rmtree(VENDOR)
        dest = VENDOR / "tools" / "grpc_interfaces"
        dest.mkdir(parents=True)
        for proto in sorted((Path(tmp) / PROTO_SUBDIR).glob("*.proto")):
            shutil.copy2(proto, dest / proto.name)
        shutil.copy2(Path(tmp) / "LICENSE", VENDOR / "LICENSE")
        (VENDOR / "UPSTREAM.json").write_text(
            json.dumps(
                {"repository": UPSTREAM, "commit": commit, "version": version},
                indent=2,
            )
            + "\n"
        )
        print(f"Vendored galago-tools {version} ({commit[:7]})")


def generate() -> None:
    from grpc_tools import protoc

    sources = sorted((VENDOR / "tools" / "grpc_interfaces").glob("*.proto"))
    if not sources:
        sys.exit("No vendored protos; run with --ref first.")
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / GEN_PKG / "tools" / "grpc_interfaces"
        staged.mkdir(parents=True)
        for proto in sources:
            text = proto.read_text().replace(
                'import "tools/grpc_interfaces/',
                f'import "{GEN_PKG}/tools/grpc_interfaces/',
            )
            (staged / proto.name).write_text(text)

        if GEN_DIR.exists():
            shutil.rmtree(GEN_DIR)
        GEN_DIR.mkdir(parents=True)
        well_known = Path(protoc.__file__).parent / "_proto"
        args = [
            "protoc",
            f"-I{tmp}",
            f"-I{well_known}",
            f"--python_out={ROOT / 'src'}",
            f"--pyi_out={ROOT / 'src'}",
            f"--grpc_python_out={ROOT / 'src'}",
        ] + [str(p) for p in sorted(staged.glob("*.proto"))]
        if protoc.main(args) != 0:
            sys.exit("protoc failed")

    for d in [GEN_DIR, GEN_DIR / "tools", GEN_DIR / "tools" / "grpc_interfaces"]:
        (d / "__init__.py").touch()
    pin = json.loads((VENDOR / "UPSTREAM.json").read_text())
    (GEN_DIR / "__init__.py").write_text(
        '"""Stubs generated from galago-tools protos by scripts/refresh_protos.py."""\n\n'
        f"GALAGO_TOOLS_VERSION = {pin['version']!r}\n"
        f"GALAGO_TOOLS_COMMIT = {pin['commit']!r}\n"
    )
    print(f"Generated stubs for {len(sources)} protos into {GEN_DIR.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ref", help="galago-tools commit or tag to vendor")
    args = parser.parse_args()
    if args.ref:
        fetch(args.ref)
    generate()


if __name__ == "__main__":
    main()
