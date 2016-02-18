import sys
import unittest

# sys.path.append("demos/helloworld")
# # from helloworld.api import PostIt
# import helloworld

sys.path.append(".")
from tornado_json.apidocjs.output import format_field_name
from tornado_json.apidocjs.output import format_type
from tornado_json.apidocjs.output import generate_py_def
# from tornado_json.apidocjs.output import get_output_example_doc
# from tornado_json.apidocjs.output import get_output_js
# from tornado_json.apidocjs.output import get_output_schema_doc
# from tornado_json.apidocjs.output import generate_apidoc_skeleton
# from tornado_json.routes import get_routes


class TestGeneratePySource(unittest.TestCase):

    def test_generate_py_def(self):
        self.assertEqual(
            generate_py_def("post", """
Description of My API method

@apiGroup People
"""),
            'def post():\n    """\n    \n    '
            'Description of My API method\n    \n    '
            '@apiGroup People\n    \n    """\n    '
            'pass\n')


class TestFormatFieldName(unittest.TestCase):

    def test_format_field_name(self):
        self.assertEqual(
            format_field_name(
                {
                    'type': 'boolean',
                },
                'published',
                ['published']),
            'published')

        self.assertEqual(
            format_field_name(
                {
                    'type': 'boolean',
                },
                'published',
                []),
            '[published]')

        self.assertEqual(
            format_field_name(
                {
                    'default': True,
                    'type': 'boolean',
                },
                'published',
                []),
            '[published=true]')


class TestFormatType(unittest.TestCase):

    def test_format_type_boolean(self):

        self.assertEqual(format_type({'type': 'boolean'}), 'Boolean')

        self.assertEqual(
            format_type({
                'type': 'array',
                'items': {
                    'type': 'boolean',
                },
            }),
            'Boolean[]')

    def test_format_type_string(self):

        self.assertEqual(format_type({'type': 'string'}), 'String')

        self.assertEqual(
            format_type({
                'type': 'string',
                'minLength': 10,
            }),
            'String{10..}')

        self.assertEqual(
            format_type({
                'type': 'string',
                'maxLength': 10,
            }),
            'String{..10}')

        self.assertEqual(
            format_type({
                'type': 'string',
                'minLength': 5,
                'maxLength': 10,
            }),
            'String{5..10}')

        self.assertEqual(
            format_type({
                'type': 'array',
                'items': {
                    'type': 'string',
                },
            }),
            'String[]')

        self.assertEqual(
            format_type({
                'type': 'array',
                'items': {
                    'type': 'string',
                    'minLength': 5,
                    'maxLength': 10,
                },
            }),
            'String[]{5..10}')

        self.assertEqual(
            format_type({
                'type': 'string',
                'enum': ['AA', 'BB', 'CC'],
                'minLength': 2,
            }),
            'String{2..}="AA","BB","CC"')

        self.assertEqual(
            format_type({
                'type': 'string',
                'enum': ['A', 'B', 'C'],
                'maxLength': 10,
            }),
            'String{..10}="A","B","C"')

        self.assertEqual(
            format_type({
                'type': 'string',
                'enum': ['Abcde', 'Bcdef', 'Cdefg'],
                'minLength': 5,
                'maxLength': 10,
            }),
            'String{5..10}="Abcde","Bcdef","Cdefg"')

        self.assertEqual(
            format_type({
                'type': 'array',
                'items': {
                    'type': 'string',
                    'enum': ['A', 'B', 'C'],
                },
            }),
            'String[]="A","B","C"')

        self.assertEqual(
            format_type({
                'type': 'array',
                'items': {
                    'type': 'string',
                    'enum': ['A', 'B', 'C'],
                    'minLength': 5,
                    'maxLength': 10,
                },
            }),
            'String[]{5..10}="A","B","C"')

    def test_format_type_number(self):

        self.assertEqual(format_type({'type': 'number'}), 'Number')

        self.assertEqual(
            format_type({
                'type': 'number',
                'minimum': 10,
            }),
            'Number{>=10}')

        self.assertEqual(
            format_type({
                'type': 'number',
                'maximum': 10,
            }),
            'Number{<=10}')

        self.assertEqual(
            format_type({
                'type': 'number',
                'minimum': 5,
                'maximum': 10,
            }),
            'Number{5~10}')

        self.assertEqual(
            format_type({
                'type': 'array',
                'items': {
                    'type': 'number',
                },
            }),
            'Number[]')

        self.assertEqual(
            format_type({
                'type': 'array',
                'items': {
                    'type': 'number',
                    'minimum': 5,
                    'maximum': 10,
                },
            }),
            'Number[]{5~10}')

    # def test_generate_apidoc_skeleton(self):
    #     routes = get_routes(helloworld)
    #     self.assertEqual(generate_apidoc_skeleton({
    #         "name": "example",
    #         "version": "1.2.3",
    #         "description": "apiDoc basic example",
    #         "title": "Custom apiDoc browser title",
    #         # "url": "https://api.github.com/v1"
    #     }, routes), True)

    # def test_js_output(self):
    #     self.assertEqual(
    #         get_output_js(
    #             {'version': '0.0.1'},
    #             '/postit/',
    #             PostIt),
    #         """""")

#     def test_get_get_output_schema_doc_string(self):
#         self.assertEqual(
#             str(get_output_schema_doc("Foobar")),
#             "")

#     def test_get_get_output_schema_doc_dict(self):
#         self.assertEqual(
#             str(get_output_schema_doc({
#                 'title': "Person details",
#                 'type': 'object',
#                 'properties': {
#                     'name': {
#                         'type': 'string',
#                     },
#                     'age': {
#                         'type': 'integer',
#                     },
#                     'address': {
#                         'title': 'Person address',
#                         'type': 'object',
#                         'properties': {
#                             'country': {
#                                 'type': 'string',
#                             },
#                         },
#                     },
#                 }})),
#             """@apiSuccess {Object} address Person address
# @apiSuccess {Integer} age None
# @apiSuccess {String} name None""")

#     def test_get_output_example_doc_string(self):
#         self.assertEqual(
#             str(get_output_example_doc("Foobar")),
#             """@apiSuccessExample {json} Success-Response:
#         HTTP/1.1 200 OK
#         \"Foobar\"""")

#     def test_get_output_example_doc_dict(self):
#         self.assertEqual(
#             str(get_output_example_doc({
#                 'name': "Paulo",
#                 'age': 29,
#                 'address': {
#                     'country': "Brazil",
#                 },
#             })),
#             """@apiSuccessExample {json} Success-Response:
#         HTTP/1.1 200 OK
#         {
#     "address": {
#         "country": "Brazil"
#     },
#     "age": 29,
#     "name": "Paulo"
# }""")


if __name__ == '__main__':
    unittest.main()
