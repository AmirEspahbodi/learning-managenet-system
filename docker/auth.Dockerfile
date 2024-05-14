FROM  lms_base_image:latest

RUN chown $APP_USER:$APP_USER $APP_HOME

USER $APP_USER

# copy dependency
COPY ./services/auth/poetry.lock  ./services/auth/pyproject.toml  ./services/auth/README.md $APP_HOME

# [OPTIONAL] Validate the project is properly configured
RUN poetry check

# Install Dependencies
RUN poetry install --no-interaction --no-cache

COPY ./services/auth/ $APP_HOME
COPY ./services/auth/entrypoint.sh $APP_HOME

RUN sed -i 's/\r$//g' /$APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh

# run entrypoint.sh
#ENTRYPOINT ["./services/auth/entrypoint.sh"]

