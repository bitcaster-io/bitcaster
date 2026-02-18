# Setup development environment





Prerequisites:

- This project uses [uv](https://docs.astral.sh/uv/) as package manager
- A Postgres DB v14+
- A Redis server

!!! note

     Uv will create a virtualenv in <project_root>/.venv, and install dependencies into it.


## Create virtualenvironment

2. Checkout code

    ```
    git clone {{ config.repo_url }}
    git config branch.autosetuprebase always

    ```

1. In the shell:

    ```
    uv venv
    source .venv/bin/activate

    ```

1. Install the package

    ```
     uv sync
     uv run pre-commit install
    ```


1. Add `export PYTHONPATH="$PYTHONPATH:./src"`


1. Check your environment:

    `./manage.py env --check` and configure the missing variables.

    !!! hint

        You can generate a list for your development environment with the command

            ./manage.py env --develop --config --pattern='export {key}={value}'

1. Run upgrade command to properly initialize the application:

    `./manage.py upgrade --admin-email ${ADMIN_EMAIL} --admin-password ${ADMIN_PASSWORD}`

    !!! note

          Django migrations and collectstatic commands are automatically included in this step


## Configure environment for .direnv

If you want to use [direnv](https://direnv.net/) and automatic loading of environment variables from a _.envrc_ file:

```
./manage.py env --develop --config --pattern='{key}={value}' > .envrc

echo 'export PYTHONPATH="$PYTHONPATH:./src"' >> .envrc
echo 'eval $(pdm venv activate)' >> .envrc
echo "unset PS1" >> .envrc
```

!!! warning

    The first time after you have created or modified the _.envrc_ file you will have to authorize it using:

        direnv allow
