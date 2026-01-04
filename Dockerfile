FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 uninstall -y pyarrow && python3 -c "import streamlit; import pandas; import ortools"

COPY project_distributor ./project_distributor
COPY streamlit_app.py ./streamlit_app.py
COPY README.md ./README.md
COPY examples ./examples

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]