# 
nell'oggetto subscription ci va aggiunto il **payload filter** as yaml for jmespath

#
nell'API di trigger va aggiunta il **recipient filter**
filter deve essere un dictionary che contiene filters django like per filtrare i queryset

#
aggiungere oggetto Team (con FK *Organisation* (mandatory), FK *Project* (opt), FK *Application* (opt))
e aggiungere **Team** in XOR con **User** in **Subscription**