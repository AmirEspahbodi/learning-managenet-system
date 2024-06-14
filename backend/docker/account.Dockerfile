FROM  python_lms_base_image:latest

# Ensure proper permissions for the application directories
RUN chown -R $APP_USER:$APP_USER $APP_HOME
RUN chmod -R 755 $APP_HOME

# Switch to the application user
USER $APP_USER

# copy dependency
COPY ./account/pyproject.toml  ./account/README.md $APP_HOME

# [OPTIONAL] Validate the project is properly configured
RUN poetry check

# Install Dependencies
RUN poetry install --no-interaction --no-cache

# copy source code
COPY ./account/accounts/ $APP_HOME/account/accounts/
COPY ./account/django_core/ $APP_HOME/account/django_core/
COPY ./account/utils/ $APP_HOME/account/utils/
COPY ./account/rest_api/ $APP_HOME/account/rest_api/
COPY ./account/permissions/ $APP_HOME/account/permissions/
COPY ./account/main.py $APP_HOME/account/main.py
COPY ./account/manage.py $APP_HOME/account/manage.py
COPY ./account/.env $APP_HOME/account/.env

# copy .pg_service.conf in user homepage
COPY ./account/.pg_service.conf $APP_HOME

# copy entrypoint.sh
COPY ./account/entrypoint.sh $APP_HOME
RUN sed -i 's/\r$//g' $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh

# run entrypoint.sh
#ENTRYPOINT ["/home/python_user/entrypoint.sh"]

