# Stacklet CLI

Installation:

```
$ just install
```

Usage:

To inialize your stacklet cli, follow the prompts in the `save-config` command:

```
$ poetry shell
$ stacklet admin save-config
Stacklet API endpoint: https://ltudy56p2b.execute-api.us-east-1.amazonaws.com/api
Cognito Region: us-east-1
Cognito User Pool Client ID: ag9dia42qootqgmvvdk0fb5np
Cognito User Pool ID: us-east-1_tYCG1oFjn
Config File Location [~/.stacklet/config.json]:
Saved config to ~/.stacklet/config.json
```

Then, create a user and follow the prompts and ensure that you have AWS SSO credentials:

```
$ stacklet admin create-user
Username: test-user
Password:
Repeat for confirmation:
Email: sonny@stacklet.io
Phone Number: +15551234567
```

Now you can get started with stacklet cli! Add an account by following the prompts:

```
$ stacklet account add-account
Security context: arn:aws:iam::532725030595:role/dev-stacklet-execution-dev
Email: sonny@stacklet.io
Path: /
Name: stacklet-sonny
Key: 532725030595
data:
  addAccount:
    status: true
```

View the accounts easily:

```
$ stacklet account list
data:
  accounts:
    edges:
    - node:
        id: account:aws:532725030595
        key: '532725030595'
        name: stacklet-sonny
        path: /
        provider: AWS
        securityContext: arn:aws:iam::532725030595:role/dev-stacklet-execution-dev
```

Specify different output types and different config file locations:

```
$ stacklet admin --config /foo/bar/config.json --output json show
{
  "api": "https://ltudy56p2b.execute-api.us-east-1.amazonaws.com/api",
  "cognito_user_pool_id": "us-east-1_tYCG1oFjn",
  "cognito_client_id": "ag9dia42qootqgmvvdk0fb5np",
  "region": "us-east-1"
}
```
