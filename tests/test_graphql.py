import requests_mock

from unittest import TestCase
from unittest.mock import MagicMock

from cli.context import StackletContext
from cli.executor import StackletGraphqlExecutor


def get_mock_context():
    mock_ctx = MagicMock()
    mock_ctx.config = {
        'config': None,
        'output': 'yaml',
        'page_variables': {
            'first': 20,
            'last': 20,
            'before': '',
            'after': ''
        },
        'raw_config': {
            'cognito_user_pool_id': 'foo',
            'cognito_client_id': 'bar',
            'region': 'us-east-1',
            'api': 'https://stacklet.acme.org/api',
        }
    }
    return mock_ctx


def get_executor_adapter():
    context = StackletContext(
        raw_config={
            'cognito_user_pool_id': 'foo',
            'cognito_client_id': 'bar',
            'region': 'us-east-1',
            'api': 'mock://stacklet.acme.org/api',
        }
    )
    executor = StackletGraphqlExecutor(context=context, token='foo')
    adapter = requests_mock.Adapter()
    executor.session.mount('mock://', adapter)
    return executor, adapter


class TestGraphql(TestCase):
    def test_executor_run(self):
        executor, adapter = get_executor_adapter()
        self.assertEqual(executor.token, 'foo')
        self.assertEqual(executor.api, 'mock://stacklet.acme.org/api')
        self.assertEqual(
            executor.session.headers['authorization'],
            'foo'
        )

        adapter.register_uri(
            'POST',
            'mock://stacklet.acme.org/api',
            json={
                'data': {
                    'accounts': {
                        'edges': [
                            {
                                'node': {
                                    'email': 'foo@bar.com',
                                    'id': 'account:aws:123123123123',
                                    'key': '123123123123',
                                    'name': 'test-account',
                                    'path': '/',
                                    'provider': 'AWS'
                                }
                            }
                        ]
                    }
                }
            }
        )

        snippet = executor.registry.get('list-accounts')

        results = executor.run(
            snippet,
            variables={
                'provider': 'AWS',
                'first': 1,
                'last': 1,
                'before': '',
                'after': ''
            }
        )

        self.assertEqual(
            results,
            {
                'data': {
                    'accounts': {
                        'edges': [
                            {
                                'node': {
                                    'email': 'foo@bar.com',
                                    'id': 'account:aws:123123123123',
                                    'key': '123123123123',
                                    'name': 'test-account',
                                    'path': '/',
                                    'provider': 'AWS'
                                }
                            }
                        ]
                    }
                }
            }
        )

    def test_executor_no_snippet(self):
        from cli.graphql import StackletGraphqlSnippet
        snippet = StackletGraphqlSnippet(
            name='foo',
            snippet='''
{
    accounts (
    ){
        edges {
            node {
                id
            }
        }
    }
}
''',
        )
        self.assertEqual(
            snippet.snippet,
            '''
{
    accounts (
    ){
        edges {
            node {
                id
            }
        }
    }
}
'''
        )
