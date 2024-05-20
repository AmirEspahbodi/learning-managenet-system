FROM  lms_base_image:latest

RUN chown $APP_USER:$APP_USER $APP_HOME

USER $APP_USER

# copy dependency
COPY ./services/auth/pyproject.toml  ./services/auth/README.md $APP_HOME

# [OPTIONAL] Validate the project is properly configured
RUN poetry check

# Install Dependencies
RUN poetry install --no-interaction --no-cache

# copy source code
COPY ./services/auth/accounts $APP_HOME/auth/accounts/
COPY ./services/auth/django_core $APP_HOME/auth/django_core/
COPY ./services/auth/utils $APP_HOME/auth/utils/
COPY ./services/auth/main.py $APP_HOME/auth/main.py
COPY ./services/auth/manage.py $APP_HOME/auth/manage.py
COPY ./services/auth/.env $APP_HOME/auth/.env

# copy .pg_service.conf in user homepage
COPY ./services/auth/.pg_service.conf $APP_HOME

# copy entrypoint.sh
COPY ./services/auth/entrypoint.sh $APP_HOME
RUN sed -i 's/\r$//g' $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh

# run entrypoint.sh
#ENTRYPOINT ["/home/python_user/entrypoint.sh"]

