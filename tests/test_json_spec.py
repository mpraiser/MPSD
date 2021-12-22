from pprint import pprint

from structed.json_codec import Decoder

spec_udp = """{
    "src_port": {
        "_length": 2,
        "_handler": "#bytes2int_b"
    },
    "dst_port": {
        "_length": 2,
        "_handler": "#bytes2int_b"
    },
    "length": {
        "_length": 2,
        "_handler": "#bytes2int_b"
    },
    "checksum": {
        "_length": 2,
        "_handler": "#bytes2int_b"
    },
    "data": {
        "_length": ["#", "length"],
        "_handler": "#bytes2hex"
    }
}"""

spec_q_gdw_12021_2019_mac_dcch = """{
    "header": {
        "type": {
            "_length": 1,
            "_handler": "#handler_type"
        },
        "payload_len": {
            "_length": 1,
            "_handler": "#bytes2int_b"
        }
    },
    "payload": {
        "_length": ["#", "payload_len"],
        "main_address": {
            "_length": 2,
            "_handler": "#bytes2hex"
        },
        "@schedules": {
            "_size": "greedy",
            "schedule_type": {
                "_length": 1,
                "_handler": "#handler_schedule_type"
            },
            "@schedule_content": {
                "_length": ["#handler_schedule_type_size", "schedule_type"],
                "_handler": ["#handler_schedule_type_content", "schedule_type"],
                "_size": ["#handler_schedule_type_len", "schedule_type"]
            }
        }
    },
    "footer": {
        "mic": {
            "_length": 2,
            "_handler": "#"
        }
    }
}"""


class TestJSONSpec:
    def test_simple_decode(self):
        decoded = Decoder().decode(spec_udp)
        pprint(decoded, sort_dicts=False)


if __name__ == "__main__":
    TestJSONSpec().test_simple_decode()
