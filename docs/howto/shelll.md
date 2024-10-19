# Send notifications from shell scripts

To send notification fro a shell script you have to

1. [Create an Application](/bitcaster/adm-guide/app/) that describes your originating system. 

     Es `Web Server` #1 or `Database Server`

1. [Create an ApiKey](/bitcaster/adm-guide/api_key/) and enable `Trigger Event` <glossary:Grant> 
1. Copy the value
1. Navigate to the Event page you want to trigger and check the <glossary:trigger url>

```shell

   curl -X POST \
      https://SERVER_ADDRESS/[trigger path] \
      -H "Authorization: Key <ApiKey>"
   
   
```
