start:
	uv run main.py

test:
	uv run test/callTool.py

deploy:
	docker compose up --build

down:
	docker compose down
