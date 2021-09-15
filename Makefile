.PSEUDO: init-db start-wsgi-app start-react-server

start-wsgi-app:
	cd server && ./venv/bin/flask run --reload --eager-loading

start-react-server:
	cd client && npm start

init-db:
	cd server && ./venv/bin/python3 -c 'import app; app.db.drop_all(); app.db.create_all()'

lint:
	find . \( -name 'venv' -o -name 'node_modules' \) -prune -o -name '*.sh' -print0 | xargs -0 -t shellcheck --shell=bash
	./server/venv/bin/pylint --rcfile ./server/.pylintrc server

smoke-test:
	./smoke_test.sh
