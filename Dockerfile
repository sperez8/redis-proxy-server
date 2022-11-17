FROM continuumio/miniconda3:4.12.0

WORKDIR /app

# Create the environment
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "proxy-env", "/bin/bash", "-c"]

# Demonstrate the environment is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

# The code to run when container is started:
COPY main.py .
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "proxy-env", "python", "main.py"]
CMD python main.py

# WORKDIR /app

# RUN apt-get update -y; apt-get upgrade -y; apt-get install -y vim-tiny vim-athena ssh


# # Create the environment:
# COPY environment.yml .
# RUN conda env create -f environment.yml

# # Add some aliases convenient for debugging
# RUN echo "alias l='ls -lah'" >> ~/.bashrc
# RUN echo "source activate connect" >> ~/.bashrc

# # Setting these environmental variables is the functional equivalent of running 'source activate my-conda-env'
# ENV CONDA_EXE /opt/conda/bin/conda
# ENV CONDA_PREFIX /opt/conda/envs/connect
# ENV CONDA_PYTHON_EXE /opt/conda/bin/python
# ENV CONDA_PROMPT_MODIFIER (connect)
# ENV CONDA_DEFAULT_ENV connect
# ENV PATH /opt/conda/envs/connect/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# # The code to run when container is started:
# COPY main.py .
# ENTRYPOINT ["python", "main.py"]