FROM postgres:16-bullseye

USER root

RUN apt-get update && apt-get install -y postgresql-plpython3-16
RUN apt-get update && apt-get install -y pg-activity

CMD ["postgres"]
