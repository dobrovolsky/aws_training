
from troposphere import (
    Ref,
    sns,
)

# ============================================================================
# SNS
# ============================================================================
sns_topic = sns.Topic("SNSTopic", )
subscription = sns.SubscriptionResource(
    'SNSTopicSubscription',
    Protocol='email',
    Endpoint='bogdan.gm24@gmail.com',
    TopicArn=Ref(sns_topic)
)