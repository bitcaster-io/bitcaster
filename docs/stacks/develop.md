
Docker compose file to be use in development environment

!!! note "Mounted local sources to enable local development:"
    
    - src/
    - docker/conf/
    - docker/bin/docker-entrypoint.sh



To run it:

    $ docker compose -f stack-samples/develop/compose.yml up

### Content

~~~yaml
--8<-- "stack-samples/develop/compose.yml"
~~~
