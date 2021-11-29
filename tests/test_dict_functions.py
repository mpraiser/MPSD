from structed.dict_operations import dict_get, dict_struct_copy


class TestDictFunctions:
    def test_dict_get(self):
        x = {
            "a": {
                "a1": 1,
                "a2": 2
            },
            "b": 3
        }

        assert dict_get(x, "a2") == 2
        assert dict_get(x, "b") == 3
        assert dict_get(x, "a") == {
            "a1": 1,
            "a2": 2
        }

    def test_dict_struct_copy(self):
        x = {
            "a": {
                "a1": 1,
                "a2": 2
            },
            "b": 3
        }
        y = dict_struct_copy(x)
        # print(y)
        assert y == {
            "a": {
                "a1": {},
                "a2": {}
            },
            "b": {}
        }


if __name__ == "__main__":
    import pytest
    pytest.main(["test_dict_functions.py"])
