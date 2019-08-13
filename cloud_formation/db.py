from troposphere import (
    Ref,
    Parameter,
    dynamodb,
    rds,
)

# ============================================================================
# DB Params
# ============================================================================
db_user = Parameter(
    "DBUser",
    Description="The database admin account username",
    Type="String",
    MinLength="1",
    MaxLength="16",
    AllowedPattern="[a-zA-Z][a-zA-Z0-9]*",
    ConstraintDescription=("must begin with a letter and contain only"
                           " alphanumeric characters.")
)

db_password = Parameter(
    "DBPassword",
    NoEcho=True,
    Description="The database admin account password",
    Type="String",
    MinLength="1",
    MaxLength="41",
    AllowedPattern="[a-zA-Z0-9]*",
    ConstraintDescription="must contain only alphanumeric characters."
)

db_name = Parameter(
    "DBName",
    Description="The database name",
    Type="String",
    MinLength="1",
    MaxLength="41",
    AllowedPattern="[a-zA-Z0-9]*",
    ConstraintDescription="must contain only alphanumeric characters."
)

# ============================================================================
# Postgres
# ============================================================================
db = rds.DBInstance(
    'Postgres',
    DBInstanceClass='db.t2.micro',
    Engine='postgres',
    AllocatedStorage="5",
    DBName=Ref(db_name),
    MasterUsername=Ref(db_user),
    MasterUserPassword=Ref(db_password),
)

# ============================================================================
# Dynamodb
# ============================================================================
dynamo_db = dynamodb.Table(
    'DynamoDBLog',
    TableName='DynamoDBLog',
    AttributeDefinitions=[dynamodb.AttributeDefinition(
        AttributeName='request_id',
        AttributeType='S',
    )],
    KeySchema=[dynamodb.KeySchema(
        AttributeName='request_id',
        KeyType='HASH',
    )],
    ProvisionedThroughput=dynamodb.ProvisionedThroughput(
        ReadCapacityUnits=5,
        WriteCapacityUnits=5,
    )
)
