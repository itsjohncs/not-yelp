.PSEUDO: init-db start-wsgi-app start-react-server

start-wsgi-app:
	cd server && ./venv/bin/flask run --reload --eager-loading

start-react-server:
	cd client && npm start

init-db:
	cd server && ./venv/bin/python3 -c 'import app; app.db.create_all()'

lint:
	./server/venv/bin/pylint --rcfile ./server/.pylintrc server
