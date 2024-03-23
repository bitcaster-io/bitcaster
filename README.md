# bitcaster


Configure environment for .direnv
================================
    
    export PYTHONPATH="$PYTHONPATH:./src"

    ./manage.py env --develop --config --pattern='export {key}={value}' > .envrc
    ./manage.py env --check
    ./manage.py upgrade