# Terms and Definitions

 Term                                                                  | Definition                                                                                                     
-----------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------
 <a id="api-key" href="api-key">API Key</a>                            | Is the token used by an [Application](#application) when sending an [Event](#event)                            
 <a id="application" href="application">Application</a>                | Is a deployment artifact and a logical subdivision of the [Project](#project)                                  
 <a id="assignment" href="assignment">Assignment</a>                | defines for which [Channel](channel) an [Address](address) can be used.                                  
 <a id="channel" href="channel">Channel</a>                            | Is the target system that will forward the [Message](#message) to the [Recipient](#recipient)                  
 <a id="dispatcher" href="dispatcher">Dispatcher</a>                   | Is the [Channel's](channel) technical component responsible for sending the [Notification](notification).
 <a id="distribution-list" href="distribution-list">Distribution List</a>                   | a list of [Recipients](recipient) meant to receive one or more [Notifications](notification).
 <a id="event" href="event">Event</a>                                  | Is the category of the [Occurrence](#occurrence)
 <a id="message" href="message">Message</a>                            | Is the template that is used for the rendering of an [Occurrence](#occurrence) for a specific [Channel](#channel)
 <a id="notification" href="notification">Notification</a>             | The configuration of the rules for matching an [Event](event) based on the event name or its payload and the [Distribution list](distribution-list) of the intended [Recipients](recipient).                                             
 <a id="occurrence" href="occurrence">Occurrence</a>                   | Is a single instance of an [Event](#event) emitted by the client system                                         
 <a id="organization" href="organization">Organization</a>             | Is the primary configuration element and authorization domain in Bitcaster                                     
 <a id="project" href="project">Project</a>                            | Is a logical subdivision of the [Organization](#organization) and a collection of [Applications](#application) 
 <a id="recipient" href="recipient">Recipient</a>                      | Is the user receiving the [Message](#message) via the [Channel](#channel)                                      
 <a id="recipient-group" href="recipient-group">Recipient Group</a>    | Is a collection of [Recipients](#recipient)                                                                    
 <a id="sender" href="sender">Sender</a>                               | Is the client system emitting the [Event](#event)                                                              
 <a id="user" href="user">User</a>                                     | Is any user configuring the system or subscribed to                                                            
