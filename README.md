# bitcaster

Setup development environment
=============================
This project uses PDM as package manager (see https://github.com/pdm-project/pdm).

To start developing:

1. install [pdm](https://github.com/pdm-project/pdm#installation)
2. $`pdm venv create`
3. activate you venv (eg. $`$(pdm venv activate)`)
4. Check your environment
   eg. $`python --version` -> see that it uses Python 3.12.*
   eg. $`which python` -> see that it matches you python executable in the venv you have created: $```echo `pwd`/.venv/bin/python```
5. Install the package: $`pdm install`
6. Check your environment: $`./manage.py env check` and configure the missing variables
7. Test using runserver $`./manage.py runserver`

NB: You may want to add the following environment variables to your local development environment:
DEBUG=1  # To start in debug mode
SECURE_SSL_REDIRECT=0  # To avoid having to use https


Configure environment for .direnv
=================================

If yoy want to use [direnv](https://direnv.net/)

    echo '$(pdm venv activate)' > .envrc
    echo "./manage.py env --develop --config --pattern='export {key}={value}'" >> .envrc
    echo "./manage.py env --check" >> .envrc
    echo "./manage.py upgrade" >> .envrc

The first time after you have created or modified the _.envrc_ file you will have to authorize it using $`direnv allow`

If you get a warning like "_direnv: PS1 cannot be exported. For more information see
https://github.com/direnv/direnv/wiki/PS1_" you can silence it by appending `unset PS1` at the end of the _.envrc_ 

If you want to use a _.env_ file for loading your environment variables automatically from direnv
you can add `dotenv` in your _.envrc_ just after the venv activation.

Example:
```shell
$(pdm venv activate)
dotenv
```
