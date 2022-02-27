class StackletGraphqlSnippet:
    """
    A resusable Graphql Snippet

    Define required variables with the required class attribute and optional
    variables with the optional class attribute. The value can either be a string
    or a dict. If the type is string, the value is passed in as the help text for
    the option. See example:

    .. code-block:: python

        class MySnippet(StackletGraphqlSnippet):

            name = 'my-snippet'
            snippet = '''
                query {
                    foo(
                        id: $id
                        bar: $bar
                        baz: $baz
                    ) {
                        id
                        description
                    }
                }
            '''

            required = {
                'id': {
                    'help': 'the id',
                    'type': click.Choice(['foo', 'bar'])
                },
                "bar": 'Another variable'
            }

            optional = {
                'baz': {
                    'help': 'An optional variable',
                    'default': 'blah'
                }
            }
    """

    def __init__(self):
        raise RuntimeError("instances don't do anything")

    name = None
    snippet = None
    required = {}
    optional = {}
    pagination = False
    input_variables = None
    parameter_types = {}

    @classmethod
    def build(cls, variables):
        if cls.snippet:
            split_snippet = list(filter(None, cls.snippet.split("\n")))
        else:
            split_snippet = []

        # remove empty options so we can remove any optional values in the mutation/queries
        for k in set(cls.optional).intersection(variables):
            if variables[k] is None or variables[k] == ():
                split_snippet = [
                    line
                    for line in split_snippet
                    if f"${k.replace('-', '_')}" not in line
                ]
        d = {}
        if variables:
            d["variables"] = {
                k: v for k, v in variables.items() if v is not None and v != ()
            }
        var_names = d.get("variables", ())

        if var_names:
            qtype, bracked = split_snippet[0].strip().split(" ", 1)
            split_snippet[0] = "%s (%s) {" % (
                qtype,
                (
                    " ".join(
                        [
                            "$%s: %s,"
                            % (s, gql_type(variables[s], cls.parameter_types.get(s)))
                            for s in var_names
                        ]
                    )
                )[:-1],
            )
        d["query"] = ("\n".join(split_snippet)).replace('"', "")
        return d


def gql_type(v, snippet_type=None):
    if snippet_type is not None:
        return snippet_type
    if isinstance(v, str):
        return "String!"
    elif isinstance(v, bool):
        return "Boolean!"
    elif isinstance(v, int):
        return "Int!"
    elif isinstance(v, list) or isinstance(v, tuple):
        return "[%s]" % (gql_type(v[0]))
    else:
        raise ValueError("unsupported %s" % (type(v)))