from .output import get_output_example_doc
from .output import get_output_schema_doc


def apply_apidocjs(func, output_schema=None, output_example=None):
    print(output_schema)
    print(output_example)
    if func.__doc__ is None:
        func.__doc__ = ''

    func.__doc__ = """@api {get} /user/:id Request User information
@apiName GetUser
@apiGroup User"""

    help(func)

    if output_schema is not None:
        func.__doc__ += "\n%s" % get_output_schema_doc(output_schema)

    if output_example is not None:
        func.__doc__ += "\n%s" % get_output_example_doc(output_example)

    help(func)
