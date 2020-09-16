import json
import os
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
import m

password = os.environ['DB_PASSWORD']
user = os.environ['DB_USER']
database = os.environ['DB_NAME']
host = os.environ['DB_HOST']
port = os.environ['DB_PORT']
school_sid = os.environ['SCHOOL_SID']

connection_string = (
    'postgresql+psycopg2://{}:{}@{}:{}/{}'
).format(user, password, host, port, database)

eng = sqlalchemy.create_engine(connection_string, pool_pre_ping=True, pool_recycle=3*3600, echo=False)
factory = sessionmaker(bind=eng)
session = factory()
session.connection(
    execution_options={
        "schema_translate_map": {"per_school": school_sid}
    }
)

m.init()

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    feature = session.query(m.Feature).first()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": feature.title,
        }),
    }
