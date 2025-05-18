# Usa la imagen oficial de Python 3.9 como base
FROM python:3.11.11-slim

# Copy local code to the container image.
ENV APP_HOME /app
ENV PYTHONUNBUFFERED TRUE

WORKDIR $APP_HOME
COPY . .

# Install production dependencies.
RUN pip install functions-framework
RUN pip install scikit-learn
RUN pip install -r requirements.txt

# Run the web service on container startup.
CMD exec functions-framework --target=hello_gcs
