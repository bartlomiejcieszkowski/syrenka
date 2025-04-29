import ast
from syrenka.lang.python import PythonAstClass, PythonAstClassParams
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def test_python_ast_class_enum_with_members_assigned_names_should_be_enum():
    class_code = """
class ThisIsEnumClass(Enum):
    FIRST = ExampleClass1
    SECOND = ExampleClass2
    THIRD = ExampleClass3

    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    assert python_class.is_enum()

    assert len(python_class.info["enum"]) == 3


def test_python_ast_class_enum_with_members_assigned_names_should_be_enum2():
    class_code = """
class ThisIsEnumClass(IntEnum):
    FIRST = auto()
    SECOND = auto()
    THIRD = auto()

    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    assert python_class.is_enum()

    assert len(python_class.info["enum"]) == 3


def test_python_ast_class_enum_with_members_assigned_names_should_be_enum3():
    class_code = """
class ThisIsEnumClass(IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3

    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    assert python_class.is_enum()

    assert len(python_class.info["enum"]) == 3


def test_python_ast_class_with_members_assigned_names_should_not_be_enum():
    class_code = """
class ThisClassIsNotEnum:
    FIRST = ExampleClass1
    SECOND = ExampleClass2
    THIRD = ExampleClass3

    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    assert not python_class.is_enum()


def test_python_ast_class_with_members_assigned_names_should_not_be_enum2():
    class_code = """
class Whatever:
    _single_member = None

    @staticmethod
    def bunch_of_static_methods():
        return True
    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    assert not python_class.is_enum()


def test_python_ast_class_with_base():
    class_code = """
class Sample(ABC):
    sample = 0
    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()


def test_python_ast_class_with_base_dots():
    class_code = """
class Sample(abc.ABC):
    sample = 0

    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()


def test_python_ast_class_with_base_call():
    class_code = """
class Sample(function(Something)):
    sample = 0

    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_with_base_call2():
    class_code = """
class Sample(something.function(Something)):
    sample = 0

    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_with_decorator_in_module():
    class_code = """
@dataclasses.dataclass
class Sample:
    sample = 0

    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_base_with_params_const():
    class_code = """
class Sample(collections.namedtuple('Pair', 12)):
    sample = 0

    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_base_with_params_tuple():
    class_code = """
# from cpython/tkinter/__init__.py
class _VersionInfoType(collections.namedtuple('_VersionInfoType',
        ('major', 'minor', 'micro', 'releaselevel', 'serial'))):
    pass
    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_base_with_params_list():
    class_code = """
class Sample(collections.namedtuple('_Sample',
        [1, "2", 3.0, ])):
    pass
    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_base_with_params_dict():
    class_code = """
class Sample(collections.namedtuple('_Sample',
        {"1": 2, "2": None, 3: 1, })):
    pass
    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_base_with_class_subscript():
    class_code = """
# from cpython/Lib/test/test_typing.py
class SimpleMapping(Generic[XK, XV]):
    pass
    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_base_with_class_slice():
    class_code = """
class SimpleMapping(Generic[0:1]):
    pass
    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_base_with_class_slice2():
    class_code = """
class SimpleMapping(Generic[:1]):
    pass
    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_base_with_class_slice3():
    class_code = """
class SimpleMapping(Generic[1:]):
    pass
    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_base_with_class_slice4():
    class_code = """
class SimpleMapping(Generic[:]):
    pass
    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))


def test_python_ast_class_base_with_class_ifexp():
    class_code = """
# from cpython/Lib/xmlrpc/client.py
class GzipDecodedResponse(gzip.GzipFile if gzip else object):
    pass
    """

    parsed_module = ast.parse(class_code)
    print(f"{type(parsed_module)}, {parsed_module = }")
    parsed_class = parsed_module.body[0]
    params = PythonAstClassParams(
        ast_class=parsed_class, filepath=Path("unknown.py"), root=Path(".")
    )
    python_class = PythonAstClass(params=params)

    python_class._parse()
    logger.info(vars(python_class))
