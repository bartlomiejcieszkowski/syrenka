import ast
from syrenka.lang.python import PythonAstClass, PythonAstClassParams
from pathlib import Path


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
