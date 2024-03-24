# bitcaster

Setup development environment
=============================
This project uses PDM as package manager (see https://github.com/pdm-project/pdm).

To start developing:

1. Install [pdm](https://github.com/pdm-project/pdm#installation)
2. $`pdm venv create`
3. Register the created venv for the project with `pdm use` 
4. Activate your venv (eg. $`$(pdm venv activate)`).
5. Check your environment
   eg. $`python --version` -> see that it uses Python 3.12.*
   eg. $`which python` -> see that it matches you python executable in the venv you have created: $```echo `pwd`/.venv/bin/python```
6. Install the package: $`pdm install`
7. Add `export PYTHONPATH="$PYTHONPATH:./src"`
8. Check your environment: $`./manage.py env --check` and configure the missing variables.
   You can generate a list for your development environment with the command `./manage.py env --develop --config --pattern='export {key}={value}'`
9. Once the environment has been set up run the initial migrations `./manage.py migrate`
10. Test using runserver $`./manage.py runserver`


Configure environment for .direnv
=================================

If yoy want to use [direnv](https://direnv.net/) and automatic loading of environment variables from a _.env_ file:
    
    ./manage.py env --develop --config --pattern='export {key}={value}' > .env
    echo "dotenv" > .envrc
    echo 'export PYTHONPATH="$PYTHONPATH:./src"' >> .envrc
    echo 'eval $(pdm venv activate)' >> .envrc
    echo "unset PS1" >> .envrc

The first time after you have created or modified the _.envrc_ file you will have to authorize it using $`direnv allow`

NB: remember to configure your variables in the _.env_ file