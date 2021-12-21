"""Unit tests only. The database is not requested."""

from typing import List

import pytest

from apps.commons.utils.mptree.models import MaterializedPathNodeModel


class NodeModel(MaterializedPathNodeModel):
    pass


def test_node_id():
    node = NodeModel(parent=None)
    encoder = node.encoder

    node.path = 'ff/0/1/ff/9'
    assert node.node_id == int(encoder.charset[9])
    node.path = '666'
    assert node.node_id == int(encoder.decode('666'))


def _create_nodes(ids: List[int]):
    nodes = []
    for i in ids:
        node = NodeModel()
        node.path = str(i)
        nodes.append(node)
    return nodes


@pytest.mark.parametrize('row, expected', [
    (_create_nodes([0, 2]), 1),
    (_create_nodes([0, 1]), 2),
    (_create_nodes([]), 0),
    (_create_nodes([666]), 0),
    (_create_nodes([0, 1, 2, 4]), 3),
    (_create_nodes([0, 1, 3, 5]), 2),
    (_create_nodes([0, 1]), 2),
])
def test_next_id(row, expected):
    node = NodeModel(parent=None)
    assert node.next_id(row) == expected
