# Message parsing based on structure description

[TOC]

## Introduction

- Requirement: Python (>= 3.10)
- Functionality: Parse messages of any protocols by a given structure description.

`Specification` and `Field` are the main objects. `Specification` is the recursively defined structure of message. `Field` contains the parsed result, also recursively. 

The message may contain field with variability, of *structural* or *length*. The basic structure is defined in `Specification`, while the final structure and length of each field will be deduced during parsing.

`parse()` takes the specification and the *sequence* to be parsed. The procedure follows:

**Spec, raw** --parse-> **Field**

JSON is used to store the serialized specification. Use `decode()` to decode it as an intermediate `dict`, then use `load()` to generate the specification.

**JSON** --decode-> **dict** --load-> **Spec** 


## Example

E.g. structure of a UDP segment is:

src_port | dst_port | length | checksum | data
:-: | :-: | :-: | :-: | :-:
2 bytes | 2 bytes | 2 bytes | 2 bytes | variable

The structure description in `udp.json` will be

```json
{
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
}
```

We've got a raw message of bytes, and parse it.

```py
from structed import decode, parse, load

with open("udp.json", "r") as fp:
    spec = load(decode(fp.read()))

raw = b"09\x1f@\x00N\xd2\x0f X\x86o\xff\xce\xd0k\xe2\x12\xbe\xfdQ\xb9L5\xd4\xd5\x16V\x8f\xc6\xb2\xdeS\xd9\xa4\xbff]tz\xa7\xf6=\xa1\xa9)\x82\xf2y\x96\xb0\xf8L\xa9\xc4\xa8z\xf7\xd3 \x88d\xb3\\\x17\xe2\x07\xd5'\x88\xaf\xc2p\xa3Y\xfcI\x8e"
message = parse(spec, raw)
print(dict(message))
```

`message` can be converted into a dict to view all the parsed values, simply by `dict()`. The result is

```profile
{
    "src_port": 12345,
    "dst_port": 8000,
    "length": 78,
    "checksum": 53775,
    "data": "2058866fffced06be212befd51b94c35d4d516568fc6b2de53d9a4bf665d747aa7f63da1a92982f27996b0f84ca9c4a87af7d3208864b35c17e207d52788afc270a359fc498e"
}
```
