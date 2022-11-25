FROM continuumio/miniconda3:4.12.0

WORKDIR /app

# Create the environment from prod dependencies
COPY environment.yml .
RUN conda env create -f environment.yml

# Adding development dependencies to env
COPY environment.dev.yml .
RUN conda env update -f environment.dev.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "proxy-env", "/bin/bash", "-c"]

# The code to run when container is started:
COPY test/ ./
CMD pytest . -v

