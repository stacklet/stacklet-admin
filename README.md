# Stacklet CLI


## Installation

```
$ just install
```

## User Creation and Login

To get started, simply use the `auto-configure` command to initialize the CLI configuration
by supplying the prefix that was used to deploy the Stacklet platform:

```
stacklet-admin auto-configure --prefix dev
```

This will create a configuration file in `~/.stacklet/config.json`.

### Logging in with SSO

If using SSO, simply login with:

```
stacklet-admin login
```

This will open a browser window and login via SSO. Once the login is successful in the browser,
the window may automatically close.

### Logging in without SSO

If SSO is not enabled, create a Cognito user (requires AWS credentials):

```
stacklet-admin user add --username test-user --password $PASSWORD
```

Finally, log in:

```
stacklet-admin login --username test-user
```

## Runnng Commands

Commands are grouped into command groups, for example, all the commands relating to accounts can be
found by running the following command:

```
stacklet-admin account --help
Usage: stacklet-admin account [OPTIONS] COMMAND [ARGS]...

  Query against and Run mutations against Account objects in Stacklet.

  Define a custom config file with the --config option

  Specify a different output format with the --output option

  Example:

      $ stacklet account --output json list

Options:
  -v                           Verbosity level, increase verbosity by
                               appending v, e.g. -vvv

  --api TEXT                   If set, --cognito-user-pool-id, --cognito-
                               client-id, --cognito-region, and --api must
                               also be set.

  --cognito-region TEXT        If set, --cognito-user-pool-id, --cognito-
                               client-id, --cognito-region, and --api must
                               also be set.

  --cognito-client-id TEXT     If set, --cognito-user-pool-id, --cognito-
                               client-id, --cognito-region, and --api must
                               also be set.

  --cognito-user-pool-id TEXT  If set, --cognito-user-pool-id, --cognito-
                               client-id, --cognito-region, and --api must
                               also be set.

  --output [|plain|json|yaml]  Ouput type
  --config TEXT
  --help                       Show this message and exit.

Commands:
  add     Add an account to Stacklet
  list    List cloud accounts in Stacklet
  remove  Remove an account from Stacklet
  show    Show an account in Stacklet
```

Then run the command:

```
stacklet-admin account list
data:
  accounts:
    edges:
    - node:
        description: null
        email: sonny@stacklet.io
        id: account:aws:123456789012
        key: '123456789012'
        name: Sandbox Sonny
        path: null
        provider: AWS
        securityContext: arn:aws:iam::123456789012:role/dev-stacklet-execution
        shortName: null
        tags: null
        variables: null
    pageInfo:
      endCursor: eJxTMlQCAADtAHY=
      hasNextPage: false
      hasPreviousPage: false
      startCursor: eJxTMlQCAADtAHY=
```

### Pagination

For commands that utilize pagination, select the next page by running the following command:

```
stacklet-admin account list --after "eJxTMlQCAADtAHY="
data:
  accounts:
    edges: []
    pageInfo:
      endCursor: ''
      hasNextPage: false
      hasPreviousPage: true
      startCursor: ''
```

The value of `--after` should be the value of the `endCursor` key under the `pageInfo` section in
the response. For results with multiple pages, continue to use the `endCursor` value to progress
through the pages. Additionally, use the `--before` option to move back one page.

`--first` and `--last` are numerical options used to select the first n or last n results of a
response. For example, to return the first account:

```
stacklet-admin account list --first 1
```

To return the last account:

```
stacklet-admin account list --last 1
```
