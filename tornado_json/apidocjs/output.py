from json import dump, dumps
from os import makedirs, system
from os.path import exists, join

from tornado_json.constants import HTTP_METHODS
from tornado_json.utils import is_method


def format_field_name(schema, field_name, required=[]):
    """Return string declaration for field name.

    :type  schema: dict
    :param schema: the schema
    :type  field_name: field_name
    :param field_name: the field name key
    :type  required: list
    :param required: required fields list
    :rtype: str
    :returns: the formated field name
    """
    has_default = 'default' in schema
    not_required = field_name not in required
    if has_default and not_required:
        default = dumps(schema['default'], separators=(',', ':'))
        return "[%s=%s]" % (field_name, default)
    elif not_required:
        return "[%s]" % field_name

    return field_name


def format_type(schema, template="%s"):
    """Return schema as formated type declarative type for api.

    :type  schema: dict
    :param schema: the schema
    :type  template: str
    :param template: template for output
    :rtype: str
    :returns: the formated string
    """
    stype = schema.get('type')
    if isinstance(stype, list):
        for i in stype:
            if i != 'null':
                stype = i
                break

    enum = schema.get('enum', '')
    if enum:
        enum = "=%s" % dumps(enum)[1:-1].replace('", ', '",')

    if stype == 'array' and 'items' in schema:
        return format_type(schema['items'], template='%s[]')

    elif stype == 'string':
        min_length = schema.get("minLength")
        max_length = schema.get("maxLength")
        if min_length and max_length:
            return "%s{%d..%d}%s" % (template % stype.capitalize(), min_length,
                                     max_length, enum)
        elif min_length:
            return "%s{%d..}%s" % (template % stype.capitalize(), min_length,
                                   enum)
        elif max_length:
            return "%s{..%d}%s" % (template % stype.capitalize(), max_length,
                                   enum)

    elif stype == 'number':
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if minimum and maximum:
            return "%s{%d~%d}%s" % (template % stype.capitalize(), minimum,
                                    maximum, enum)
        elif minimum:
            return "%s{>=%d}%s" % (template % stype.capitalize(), minimum,
                                   enum)
        elif maximum:
            return "%s{<=%d}%s" % (template % stype.capitalize(), maximum,
                                   enum)

    return "%s%s" % (template % stype.capitalize(), enum)


def get_rh_methods(rh):
    """Return all RequestHandler valid HTTP methods."""
    for k, v in vars(rh).items():
        if all([
            k in HTTP_METHODS,
            is_method(v),
        ]):
            yield (k, v)


class P(object):
    def __init__(self, name, *parts, **kw):
        self.name = name
        self.parts = parts
        self.lines = kw.get("lines", [])

    def __str__(self):
        lines = ""
        if self.lines:
            lines = "\n"
            lines += "\n".join(self.lines)
            lines = lines.replace("\n", "\n    ")

        s = "\n@%s %s %s\n" % (self.name, " ".join(self.parts), lines)

        return s


def get_method_api_description(method):
    return (getattr(method, "__doc__", "") or "").strip().split("\n")


def get_input_example_doc(input_example,
                          api_param="apiParamExample",
                          api_param_title="Request-Example"):
    src = dumps(input_example, indent=4, sort_keys=True)
    doc = P(api_param, "{json}", "%s:" % api_param_title, lines=[src])
    return doc


def get_output_example_doc(output_example,
                           api_param="apiSuccessExample",
                           api_param_title="Success-Response"):
    src = dumps(output_example, indent=4, sort_keys=True)
    doc = P(api_param, "{json}", "%s:" % api_param_title,
            lines=["HTTP/1.1 200 OK",
                   src])
    return doc


def get_input_schema_doc(input_schema):
    return get_output_schema_doc(input_schema, param_name="apiParam")


def get_output_schema_doc(output_schema, param_name="apiSuccess", preffix=[]):
    if not isinstance(output_schema, dict):
        return ""

    if output_schema.get("type") != 'object':
        return ""

    required = output_schema.get('required', [])
    parts = []
    for k, schema in sorted(output_schema.get('properties', {}).items()):
        vtype = schema.get('type')
        description = schema.get("description")
        if vtype == 'object' and description is None:
            description = schema.get("title", "")

        key = k
        if preffix:
            key = ".".join(preffix + [k])

        p = P(param_name,
              "{%s}" % format_type(schema),
              format_field_name(schema, key, required),
              description or '')

        parts.append(p)

        if vtype == 'object':
            parts += get_output_schema_doc(schema,
                                           param_name=param_name,
                                           preffix=preffix + [k])

        elif vtype == 'array' and 'items' in schema:
            parts += get_output_schema_doc(schema['items'],
                                           param_name=param_name,
                                           preffix=preffix + [k])

    return parts


def get_output_js(apidoc, url, rh_class):
    src = []
    for method_type, method in get_rh_methods(rh_class):
        doc = {}
        docparts = get_method_api_description(method) or ['']
        doc['api'] = ("{%s}" % method_type,
                      url,
                      docparts[0], )
        doc['apiVersion'] = apidoc['version']
        doc['apiName'] = "%s%s" % (method_type.upper(), rh_class.__name__)
        doc['apiGroup'] = rh_class.__name__

        if getattr(method, 'input_schema', None):
            doc['input_schema'] = get_input_schema_doc(method.input_schema)
            doc['input_schema_apiuse'] = P("apiUse", "SchemaValidationError")

        if getattr(method, 'input_example', None):
            doc['input_example'] = get_input_example_doc(method.input_example)

        if getattr(method, 'output_schema', None):
            output_schema = {
                'type': 'object',
                'properties': {
                    'data': method.output_schema,
                    'status': {
                        'description': "Returns 'success', 'fail' or 'error'.",
                        'type': 'string',
                        # 'enum': ['fail', 'success']
                    }
                }
            }
            doc['output_schema'] = get_output_schema_doc(output_schema)

        if getattr(method, 'output_example', None):
            output_example = {
                "data": method.output_example,
                "status": "success"
            }
            doc['output_example'] = get_output_example_doc(output_example)

        doc['apiUse'] = "InternalServerError"

        parts = []
        for k, v in doc.items():
            if isinstance(v, P):
                p = v
            elif isinstance(v, str):
                p = P(k, v)
            else:
                if any([isinstance(i, P) for i in v]):
                    p = "".join([str(i) for i in v])
                else:
                    p = P(k, *v)

            parts.append(str(p))

        extra = []
        for line in docparts[1:]:
            line = line.strip()
            if line.startswith("@api"):
                extra.append(line)

        parts += extra

        doc = "\n".join(parts).replace("\n", "\n    ")

        doc = """    \"\"\"%s
    \"\"\"""" % doc
        js = """def %s():
%s
    pass
""" % (method_type, doc)
        src.append(js)

    src = "\n".join(src)
    return src


def generate_py_def(func_name, docstring):
    """Return dummy python source containing one function with docstring.

    :type  func_name: str
    :param func_name: function name
    :type  docstring: str
    :param docstring: docstring text (not indented)
    :rtype: str
    :returns: the python source code
    """
    docstring = docstring.replace("\n", "\n    ")
    # doc = """    \"\"\"%s
    # \"\"\"""" % doc
    src = '''def %s():
    """
    %s
    """
    pass
''' % (func_name, docstring)
    return src


def generate_errors_file(output_path):
    """Write file declaring @apiError notations.

    :type  output_path: str
    :param output_path: Destination path
    """
    src = []

    src.append(generate_py_def("schema_validation_error", """
@apiDefine SchemaValidationError
@apiError SchemaValidationError One schema field did not validate
@apiErrorExample {json} SchemaValidationError-Response:
    HTTP/1.1 400 Bad Request
    {
      "data": "TRACEBACK FROM SERVER",
      "status": "fail"
    }
"""))

    src.append(generate_py_def("internal_server_error", """
@apiDefine InternalServerError
@apiError (Error 5xx) InternalServerError Return data for any internal
    server error
@apiErrorExample {json} InternalServerError-Response:
    HTTP/1.1 500 Internal Server Error
    {
      "status": "error",
      "code": 500,
      "message": "Internal Server Error"
    }
"""))

    src = "\n".join(src)
    return src


def generate_apidoc_skeleton(routes,
                             content_output_path="apidocjs_input",
                             doc_output_path="doc", **kw):
    apidoc = {
        'name': "My project",
        'title': "My Tornado-JSON based project",
        'version': '0.0.1',
    }
    apidoc.update(kw)
    output_path = join(content_output_path, apidoc['version'])

    if not exists(output_path):
        makedirs(output_path)

    open(join(output_path, 'errors.py'), 'w').write(generate_errors_file())

    dump(apidoc,
         open(join(output_path, 'apidoc.json'), 'w'), indent=4)

    for url, rh in routes:
        part = url[1:].replace("/", "_").replace("_?", "")
        fname = "%s_%s.py" % (part, rh.__name__)
        fname = fname.lower()
        fpath = join(output_path, fname)
        src = get_output_js(apidoc, url, rh)
        open(fpath, 'w').write(src)

    system("apidoc -i %s -o %s --verbose" % (content_output_path,
                                             doc_output_path))
