FROM continuumio/miniconda3:4.12.0

WORKDIR /app

# Create the environment
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "proxy-env", "/bin/bash", "-c"]

# The code to run when container is started:
COPY proxy/ ./
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "proxy-env", "python", "main.py"]
#CMD python app/main.py

