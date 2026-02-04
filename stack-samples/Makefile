help:
	@echo "develop:  run develop stack"
	@echo "stable :  run stable latest released stack"
	@echo "clean  :  clean all created images/services"


develop:
	cd .. && docker compose -f ${PWD}/develop/compose.yml up


stable:
	cd .. && docker compose -f ${PWD}/stable/compose.yml up


clean:
	cd .. && docker compose -f ${PWD}/develop/compose.yml  down -v --rmi all
	cd .. && docker compose -f ${PWD}/stable/compose.yml  down -v --rmi all


.PHONY: clean stable develop
