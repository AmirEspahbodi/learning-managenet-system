FROM  lms_base_image:latest

# copy dependency
COPY ./services/auth/poetry.lock  ./services/auth/pyproject.toml  ./services/auth/README.md $APP_HOME

# [OPTIONAL] Validate the project is properly configured
RUN poetry check

# Install Dependencies
RUN poetry install --no-interaction --no-cache

COPY ./services/auth/ $APP_HOME

USER $APP_USER
