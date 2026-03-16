FROM python:3.11-slim-bookworm AS admin_api_base

# --------------------------------------------------------------------------
ARG DOCKER_USER
ARG DOCKER_USER_ID

ARG PROJECT_BASE_DIR
ARG BACKEND_BASE_DIR

ARG ADMIN_API_BASE_DIR
ARG ADMIN_API_CACHE_DIR
ARG ADMIN_API_STATIC_ROOT
ARG ADMIN_API_MEDIA_ROOT

# --------------------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --------------------------------------------------------------------------
# create system user
RUN useradd -r -u ${DOCKER_USER_ID} -d /opt -s /bin/bash ${DOCKER_USER}
RUN usermod -aG sudo ${DOCKER_USER}


# --------------------------------------------------------------------------
# create folders for project
# with proper permissions
RUN mkdir -p ${PROJECT_BASE_DIR} && chown ${DOCKER_USER}:${DOCKER_USER} ${PROJECT_BASE_DIR} && chmod 770 ${PROJECT_BASE_DIR}
RUN mkdir -p ${BACKEND_BASE_DIR} && chown ${DOCKER_USER}:${DOCKER_USER} ${BACKEND_BASE_DIR} && chmod 770 ${BACKEND_BASE_DIR}

RUN mkdir -p ${ADMIN_API_BASE_DIR} && chown ${DOCKER_USER}:${DOCKER_USER} ${ADMIN_API_BASE_DIR} && chmod 770 ${ADMIN_API_BASE_DIR}

RUN mkdir -p ${ADMIN_API_CACHE_DIR} && chown ${DOCKER_USER}:${DOCKER_USER} ${ADMIN_API_CACHE_DIR} && chmod 770 ${ADMIN_API_CACHE_DIR}
RUN mkdir -p ${ADMIN_API_STATIC_ROOT} && chown ${DOCKER_USER}:${DOCKER_USER} ${ADMIN_API_STATIC_ROOT} && chmod 770 ${ADMIN_API_STATIC_ROOT}
RUN mkdir -p ${ADMIN_API_MEDIA_ROOT} && chown ${DOCKER_USER}:${DOCKER_USER} ${ADMIN_API_MEDIA_ROOT} && chmod 770 ${ADMIN_API_MEDIA_ROOT}

USER ${DOCKER_USER}


# --------------------------------------------------------------------------
# copy app files
COPY --chown=${DOCKER_USER}:${DOCKER_USER} ./src/src/backend ${BACKEND_BASE_DIR}
COPY --chown=${DOCKER_USER}:${DOCKER_USER} ./src/src/admin_api ${ADMIN_API_BASE_DIR}
COPY --chown=${DOCKER_USER}:${DOCKER_USER} ./django_admin_adapter ${PROJECT_BASE_DIR}/django_admin_adapter

COPY --chown=${DOCKER_USER}:${DOCKER_USER} ./src/docker/common/manage.py ${PROJECT_BASE_DIR}

COPY --chown=${DOCKER_USER}:${DOCKER_USER} ./src/docker/admin_api/wsgi.py ${PROJECT_BASE_DIR}
COPY --chown=${DOCKER_USER}:${DOCKER_USER} ./src/docker/admin_api/requirements.txt ${PROJECT_BASE_DIR}

COPY --chown=${DOCKER_USER}:${DOCKER_USER} ./src/docker/backend/settings.py ${BACKEND_BASE_DIR}
COPY --chown=${DOCKER_USER}:${DOCKER_USER} ./src/docker/admin_api/settings.py ${PROJECT_BASE_DIR}


# --------------------------------------------------------------------------
# install


WORKDIR ${PROJECT_BASE_DIR}
USER root

RUN apt-get update && apt-get install -y build-essential=12.9 libpq-dev python3-dev=3.11.2-1+b1


# ---------------- development

FROM admin_api_base AS dev

RUN python3 -m pip install -r requirements.txt
COPY --chown=${DOCKER_USER}:${DOCKER_USER} ./src/docker/admin_api/entrypoint.sh ${PROJECT_BASE_DIR}
RUN chmod 550 entrypoint.sh

USER ${DOCKER_USER}

RUN touch __init__.py

EXPOSE 8000
