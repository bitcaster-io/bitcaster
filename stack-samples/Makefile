help:
	@echo "develop:  run develop stack"
	@echo "simple :  run simple minimalistic stack"
	@echo "full   :  run full-featured stack (mainly as sample/reference)"
	@echo "clean  :  clean all created images/services"


develop:
	cd .. && docker compose -f ${PWD}/develop/compose.yml up

full:
	cd .. && docker compose -f ${PWD}/full/compose.yml up

simple:
	cd .. && docker compose -f ${PWD}/simple/compose.yml up


clean:
	cd .. && docker compose -f ${PWD}/develop/compose.yml  down -v --rmi all
	cd .. && docker compose -f ${PWD}/simple/compose.yml  down -v --rmi all
	cd .. && docker compose -f ${PWD}/full/compose.yml  down -v --rmi all


.PHONY: full clean simple develop
