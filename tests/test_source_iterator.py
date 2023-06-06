import secrets
from julienne.sources.base import IteratorDataSource


def test_iterator_data_source():
    """tests that we can loop over a json array file"""

    comparison_datas = [{"key": secrets.token_hex()} for _ in range(10)]

    # make a copy of this data (using list comprehension to make a copy)
    data_source = IteratorDataSource([x for x in comparison_datas])

    for data in data_source:
        assert data in comparison_datas
        comparison_datas.remove(data)

    # there should be no remaining values in this list since we removed
    # them all as we found them above
    assert not comparison_datas
