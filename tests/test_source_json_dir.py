import json
import os
import tempfile
from julienne.sources.filesystem import JsonFilesDirDataSource


def test_json_files_dir_data_source():
    """tests that we can loop over a directory of json files correctly"""
    temp_dir = tempfile.mkdtemp()

    file_content_template = '{{"key": {}}}'

    # create our files, and the array of file contents to compare to
    comparison_datas = []
    for i in range(10):
        file_name = os.path.join(temp_dir, f"{i}.json")
        with open(file_name, "w+") as f:
            data = file_content_template.format(i)
            f.write(data)
            comparison_datas.append(json.loads(data))

    data_source = JsonFilesDirDataSource(temp_dir)

    # check that the data from each file is in the comparinson datas array
    for data in data_source:
        assert data in comparison_datas
        comparison_datas.remove(data)

    # there should be no remaining values in this list since we removed
    # them all as we found them above
    assert not comparison_datas
