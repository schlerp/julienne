import json
import os
import secrets
import tempfile
from julienne.sources.filesystem import JsonArrayFileDataSource


def test_json_array_file_data_source():
    """tests that we can loop over a json array file"""
    temp_dir = tempfile.mkdtemp()

    file_content = (
        f'[{{"key": "{secrets.token_hex()}"}}, {{"key": "{secrets.token_hex()}"}}]'
    )
    file_name = os.path.join(temp_dir, "test_file.json")

    with open(file_name, "w+") as f:
        f.write(file_content)

    data_source = JsonArrayFileDataSource(file_name)

    comparison_datas = json.loads(file_content)
    for data in data_source:
        assert data in comparison_datas
        comparison_datas.remove(data)

    # there should be no remaining values in this list since we removed
    # them all as we found them above
    assert not comparison_datas
