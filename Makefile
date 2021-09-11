.PSEUDO: start-wsgi-app start-react-server

start-wsgi-app:
	cd server && ./venv/bin/flask run --reload

start-react-server:
	cd client && npm start
