up:
	docker-compose up -d

down:
	docker-compose down

logs: 
	docker-compose logs

ps:
	docker-compose ps

run-auth:
	poetry run uvicorn recotg.services.auth_service.app.main:app --host 0.0.0.0 --port 8001 --reload --env-file .env --reload-dir recotg


