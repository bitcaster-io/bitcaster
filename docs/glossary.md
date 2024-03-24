# Bitcaster Glossary

 Term                                          | Definition                                                                                              
-----------------------------------------------|---------------------------------------------------------------------------------------------------------
 <a id="api-key">API Key</a>                   | Is the token used by an [Application](#application) when sending an [Event](#event)
 <a id="application">Application</a>           | Is a deployment artifact and a logical subdivision of the [Project](#project)                                                     
 <a id="channel">Channel</a>                   | Is the target system that will forward the [Message](#message) to the [Recipient](#recipient)           
 <a id="event">Event</a>                       | Is a single occurrence of an notification emitted by the client system                                  
 <a id="event-type">EvenType</a>               | Is the category of the [Event](#event)                                                                  
 <a id="message-template">Message Template</a> | Is the template that is used for the rendering of an [Event](#event) for a specific [Channel](#channel) 
 <a id="organization">Organization</a>         | The Organization is the primary configuration element and authorization domain in Bitcaster             
 <a id="project">Project</a>                   | Is a logical subdivision of the [Organization](#organization) and a collection of [Applications](#application)
 <a id="recipient">Recipient</a>               | Is the user receiving the [Message](#message) via the [Channel](#channel)                               
 <a id="recipient-group">Recipient Group</a>   | Is a collection of [Recipients](#recipient)                            
 <a id="sender">Sender</a>                     | Is the client system emitting the [Event](#event)                                                       
 <a id="user">User</a>                         | Is any user configuring the system or subscribed to                                                     
