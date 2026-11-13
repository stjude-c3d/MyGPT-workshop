# MyGPT workshop environment: JupyterLab + the Python packages used by every module.
# MyGPT and Ollama are NOT in this image — they run on the host (see SETUP.md).
#
# Prebuilt image:  docker pull ghcr.io/stjude-c3d/mygpt-workshop:latest
# Local build:     docker compose build

FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b

LABEL org.opencontainers.image.source="https://github.com/stjude-c3d/MyGPT-workshop" \
      org.opencontainers.image.description="JupyterLab environment for the MyGPT KIDS26 workshop"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Pinned versions (requirements.lock) so every attendee gets the same environment
COPY requirements.lock /tmp/requirements.lock
RUN pip install -r /tmp/requirements.lock && rm /tmp/requirements.lock

# Run as an unprivileged user
RUN useradd --create-home --uid 1000 workshop
WORKDIR /workspace

# Bake the workshop material in, so the image also works without a clone.
# docker compose mounts your clone over /workspace, so your edits and outputs persist.
COPY --chown=workshop:workshop . /workspace

USER workshop
EXPOSE 8888

# The token is read from JUPYTER_TOKEN (set in compose.yaml).
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--ServerApp.root_dir=/workspace"]
