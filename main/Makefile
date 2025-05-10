run:
	uv run streamlit run main.py

one-time:
	uv run ohlc_save_data.py
	uv run ta_save_data.py

dev:
	uv run uvicorn app:app 

docker-build:
	@echo "Building Docker image..."
	docker build -t chart .

docker-run:
	@echo "Running Docker container..."
	docker run -d -p 8000:8000 chart