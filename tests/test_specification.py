from pprint import pprint
from structed.specification import decode
from structed.section import load


json_str = """{
        "src_port": {
            "_properties": {
                "size": 2,
                "handler": "#bytes2int_b"
            }
        },
        "dst_port": {
            "_properties": {
                "size": 2,
                "handler": "#bytes2int_b"
            }
        },
        "length": {
            "_properties": {
                "size": 2,
                "handler": "#bytes2int_b"
            }
        },
        "checksum": {
            "_properties": {
                "size": 2,
                "handler": "#bytes2int_b"
            }
        },
        "data": {
            "_properties": {
                "size": [
                    "#identity",
                    "length"
                ],
                "handler": "#bytes2hex"
            }
        }
    }"""


class TestSpecification:
    def test_decode(self):
        decoded = decode(json_str)
        pprint(decoded, sort_dicts=False)
        # TODO: assertion of this case.


if __name__ == "__main__":
    import pytest
    pytest.main(["test_specification.py"])
