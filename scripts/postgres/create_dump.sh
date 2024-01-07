# SET ENVIRONMENT VARIABLES
export PG_CONTAINER_NAME=authenticator-pg_database-1
export POSTGRES_USER=AuthenticatorUser
export POSTGRES_DB=bot
docker exec -t ${PG_CONTAINER_NAME} pg_dump -U ${POSTGRES_USER} -Fp -f /tmp/db_dump.sql --dbname=${POSTGRES_DB}
mkdir -p ./postgres
docker cp ${PG_CONTAINER_NAME}:/tmp/db_dump.sql ./postgres/db_dump.sql
