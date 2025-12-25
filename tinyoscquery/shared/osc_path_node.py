import builtins
import json
from json import JSONEncoder
from typing import Any, TypeVar, Union

from tinyoscquery.shared.osc_access import OSCAccess
from tinyoscquery.shared.osc_spec import disallowed_path_chars, is_valid_path
from tinyoscquery.shared.oscquery_spec import OSCQueryAttribute


class OSCNodeEncoder(JSONEncoder):
    def __init__(self, attribute_filter: OSCQueryAttribute | None = None, **kwargs):
        super(OSCNodeEncoder, self).__init__()
        self.attribute_filter = attribute_filter

    def default(self, o):
        if isinstance(o, OSCPathNode):
            obj_dict = {}
            o: OSCPathNode
            for k, v in o.attributes.items():
                if v is None:
                    continue

                if self.attribute_filter is not None and self.attribute_filter != k:
                    continue

                match k:
                    case OSCQueryAttribute.CONTENTS:
                        if len(v) < 1:
                            continue
                        obj_dict["CONTENTS"] = {}
                        sub_node: OSCPathNode
                        for sub_node in v:
                            if (
                                sub_node.attributes[OSCQueryAttribute.FULL_PATH]
                                is not None
                            ):
                                obj_dict["CONTENTS"][
                                    sub_node.attributes[
                                        OSCQueryAttribute.FULL_PATH
                                    ].split("/")[-1]
                                ] = sub_node
                            else:
                                continue
                    case OSCQueryAttribute.TYPE:
                        obj_dict["TYPE"] = python_type_list_to_osc_type(v)
                    case _:
                        obj_dict[k.name.upper()] = v

            return obj_dict

        return json.JSONEncoder.default(self, o)


T = TypeVar("T", bound=int | float | bool | str)


class OSCPathNode:
    def __init__(
        self,
        full_path: str,
        contents: list["OSCPathNode"] = None,
        access: OSCAccess = OSCAccess.NO_VALUE,
        description: str = None,
        value: Union[T, list[T]] = None,
    ):
        if not is_valid_path(full_path):
            raise ValueError(
                "Invalid path: Path must not contain any of the following characters: {} ".format(
                    disallowed_path_chars
                )
            )

        self._attributes: dict[OSCQueryAttribute, Any] = {}

        self._attributes[OSCQueryAttribute.FULL_PATH] = full_path

        self._attributes[OSCQueryAttribute.CONTENTS]: list["OSCPathNode"] = (
            contents or []
        )

        # Ensure that value is an iterable
        try:
            iter(value)
        except TypeError:
            value = [value] if value is not None else []
        self._attributes[OSCQueryAttribute.VALUE] = value

        if value is None and access is not OSCAccess.NO_VALUE:
            raise Exception(
                f"No value(s) given, access must be {OSCAccess.NO_VALUE.name} for container nodes."
            )

        types = []
        for v in self._attributes[OSCQueryAttribute.VALUE]:
            types.append(type(v))

        self._attributes[OSCQueryAttribute.TYPE] = types if value is not None else None

        self._attributes[OSCQueryAttribute.ACCESS] = access

        self._attributes[OSCQueryAttribute.DESCRIPTION] = description

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> "OSCPathNode":
        """Factory method to create an instance of OSCPathNode from JSON data."""
        contents = None
        if "CONTENTS" in json_data:
            sub_nodes = []
            for subNode in json_data["CONTENTS"]:
                sub_nodes.append(OSCPathNode.from_json(json_data["CONTENTS"][subNode]))
            contents = sub_nodes

        # This *should* be required but some implementations don't have it...
        full_path = None
        if "FULL_PATH" in json_data:
            full_path = json_data["FULL_PATH"]

        description = None
        if "DESCRIPTION" in json_data:
            description = json_data["DESCRIPTION"]

        access = None
        if "ACCESS" in json_data:
            access = OSCAccess(json_data["ACCESS"])

        value = None
        if "VALUE" in json_data:
            value = []
            if not isinstance(json_data["VALUE"], list):
                raise Exception("OSCQuery JSON Value is not List / Array? Out-of-spec?")

            for idx, v in enumerate(json_data["VALUE"]):
                # According to the spec, if there is not yet a value, the return will be an empty JSON object
                if isinstance(v, dict) and not v:
                    # FIXME does this apply to all values in the value array always...? I assume it does here
                    value = []
                    break
                else:
                    value.append(v)

        return cls(full_path, contents, access, description, value)

    @property
    def attributes(self) -> dict[OSCQueryAttribute, Any]:
        return self._attributes

    @property
    def full_path(self) -> str:
        return self._attributes[OSCQueryAttribute.FULL_PATH]

    @property
    def contents(self) -> list["OSCPathNode"]:
        return self._attributes[OSCQueryAttribute.CONTENTS]

    @property
    def description(self) -> str:
        return self._attributes[OSCQueryAttribute.DESCRIPTION]

    @property
    def access(self) -> OSCAccess:
        return self._attributes[OSCQueryAttribute.ACCESS]

    @property
    def value(self) -> Any:
        return self._attributes[OSCQueryAttribute.VALUE]

    @property
    def type(self) -> Any:
        return self._attributes[OSCQueryAttribute.TYPE]

    @property
    def is_method(self) -> bool:
        """Returns True if this node is an OSC method, False otherwise.
        An OSC method"""
        if self.contents:
            return False
        return True

    def find_subnode(self, full_path: str) -> Union["OSCPathNode", None]:
        """Recursively find a node with the given full path"""
        if self.full_path == full_path:
            return self

        if not self.contents:
            return None

        for sub_node in self.contents:
            found_node = sub_node.find_subnode(full_path)
            if found_node:
                return found_node

        return None

    def add_child_node(self, child: "OSCPathNode"):
        if child == self:
            return

        path_split = child.full_path.rsplit("/", 1)
        if len(path_split) < 2:
            raise Exception("Tried to add child node with invalid full path!")

        parent_path = path_split[0]

        if parent_path == "":
            parent_path = "/"

        parent = self.find_subnode(parent_path)

        if parent is None:
            parent = OSCPathNode(parent_path)
            self.add_child_node(parent)

        parent.contents.append(child)

    def to_json(self, attribute: OSCQueryAttribute | None = None) -> str:
        return json.dumps(self, cls=OSCNodeEncoder, attribute_filter=attribute)

    def __iter__(self):
        yield self
        if self.contents is not None:
            for subNode in self.contents:
                yield from subNode

    def __str__(self) -> str:
        return f'<OSCQueryNode @ {self.full_path} (D: "{self.description}" T:{self.type} V:{self.value})>'


def osc_type_string_to_python_type(type_str: str) -> list[type]:
    types: list[type] = []
    for type_value in type_str:
        match type_value:
            case "":
                pass
            case "i":
                types.append(int)
            case "f" | "h" | "d" | "t":
                types.append(float)
            case "T" | "F":
                types.append(bool)
            case "s":
                types.append(str)
            case _:
                raise Exception(
                    f"Unknown OSC type when converting! {type_value} -> ???"
                )

    return types


def python_type_list_to_osc_type(types_: list[type]) -> str:
    output = []
    for type_ in types_:
        match type_:
            case builtins.bool:
                output.append("T")
            case builtins.int:
                output.append("i")
            case builtins.float:
                output.append("f")
            case builtins.str:
                output.append("s")
            case _:
                raise Exception(f"Cannot convert {type_} to OSC type!")

    return "".join(output)


if __name__ == "__main__":
    root = OSCPathNode("/", description="root node")
    root.add_child_node(OSCPathNode("/test/node/one"))
    root.add_child_node(OSCPathNode("/test/node/two"))
    root.add_child_node(OSCPathNode("/test/othernode/one"))
    root.add_child_node(OSCPathNode("/test/othernode/three"))

    # print(root)

    for _child in root:
        print(_child)
