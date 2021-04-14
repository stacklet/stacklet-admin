import click

from cli.commands import CustodianCommand, commands


@click.group()
def cli():
    """
    Stacklet CLI

    Run graphql queries against Stacklet API. To get started run the following command
    and follow prompts to configure your Stacklet CLI:

        $ stacklet admin configure

    If this is your first time using Stacklet, create a user:

        $ stacklet admin create-user

    Now login:

        $ stacklet user login

    Your configuration file is saved to the directory: ~/.stacklet/config.json and your credentials
    are stored at ~/.stacklet/credentials. You may need to periodically login to refresh your
    authorization token.

    Run your first query:

        $ stacklet account list

    To specify a different configuration file or different API endpoint/Cognito Configuration:

    \b
        $ stacklet user \\
            --api $stacklet_api \\
            --cognito-client-id $cognito_client_id \\
            --cognito-user-pool-id $cognito_user_pool_id \\
            --region $region \\
            login

    or:

    \b
        $ stacklet user \\
            --config $config_file_location \\
            login

    Specify different output types:

        $ stacklet account --output json list

    Stacklet queries default to 20 entries per page. To use pagiantion:

    \b
        $ stacklet account \\
            --first 20 \\
            --last 20 \\
            --before $before_token \\
            --after $after_token \\
            list

    You can also use Stacklet CLI to run Cloud Custodian commands:

    \b
        $ stacklet custodian schema aws
    """
    pass


@cli.command(cls=CustodianCommand)
def custodian(*args, **kwargs):
    """
    Cloud Custodian CLI
    """


for c in commands:
    cli.add_command(c)


if __name__ == "__main__":
    cli()
