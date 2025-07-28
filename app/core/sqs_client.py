"""
Cliente SQS centralizado para integração assíncrona com AWS SQS.
Utiliza aioboto3 para enviar, receber e deletar mensagens.
"""

import os
from typing import Any, Dict, List, Optional

import aioboto3

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


class SQSClient:
    def __init__(self):
        self.session = aioboto3.Session()
        self.region = AWS_REGION
        self.aws_access_key_id = AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = AWS_SECRET_ACCESS_KEY

    async def send_message(
        self,
        queue_url: str,
        message_body: str,
        message_attributes: Optional[Dict[str, Any]] = None,
    ):
        async with self.session.client(
            "sqs",
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        ) as sqs:
            await sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body,
                MessageAttributes=message_attributes or {},
            )

    async def receive_messages(
        self, queue_url: str, max_messages: int = 5, wait_time: int = 10
    ) -> List[Dict[str, Any]]:
        async with self.session.client(
            "sqs",
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        ) as sqs:
            response = await sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
                MessageAttributeNames=["All"],
            )
            return response.get("Messages", [])

    async def delete_message(self, queue_url: str, receipt_handle: str):
        async with self.session.client(
            "sqs",
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        ) as sqs:
            await sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)


def get_sqs_client() -> SQSClient:
    return SQSClient()
