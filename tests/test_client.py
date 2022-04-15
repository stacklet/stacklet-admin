from stacklet.client.platform.client import platform_client


def test_client_loaded_commands():
    client = platform_client()
    assert hasattr(client, 'list_bindings')
    assert hasattr(client, 'list_accounts')
    assert hasattr(client, 'list_repository')
    assert hasattr(client, 'list_policies')
