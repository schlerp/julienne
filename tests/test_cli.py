import json
import sys
from datetime import datetime
from pathlib import Path
from subprocess import run, CalledProcessError


def test_demo_filesystem_cli(tmp_path):
    input_file: Path = tmp_path / "people.json"
    output_dir: Path = tmp_path / "out"
    output_dir.mkdir()

    payload = [
        {"first_name": "First", "last_name": "Last", "dob": datetime.now().isoformat()},
        {"first_name": "Foo", "last_name": "Bar", "dob": datetime.now().isoformat()},
    ]

    input_file.write_text(json.dumps(payload))

    cmd = [
        sys.executable,
        "-m",
        "julienne",
        "demo-filesystem",
        "--input-json",
        str(input_file),
        "--output-dir",
        str(output_dir),
    ]

    try:
        run(cmd, capture_output=True, text=True, check=True)
    except CalledProcessError as exc:
        raise AssertionError(
            f"CLI failed with code {exc.returncode}: {exc.stderr}"
        ) from exc

    written_files = list(output_dir.glob("*.json"))
    assert len(written_files) == 2

    loaded = [json.loads(p.read_text()) for p in written_files]
    assert all("dob" not in item for item in loaded)
