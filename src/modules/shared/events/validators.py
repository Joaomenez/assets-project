"""
Validadores padrão para diferentes tipos de eventos.
"""
from typing import Dict, Any
from ddtrace import tracer
from .interfaces import EventValidator
from ..tracing.datadog_config import datadog_trace, add_trace_context

class KinesisEventValidator(EventValidator):
    """Validador para eventos Kinesis."""
    
    @datadog_trace(service="event_validator", name="validate_kinesis")
    def validate(self, event: Dict[str, Any]) -> bool:
        with tracer.current_span() as span:
            add_trace_context(span, {"validator": "kinesis"})
            
            if not isinstance(event, dict) or 'Records' not in event:
                span.set_tag("validation_error", "missing_records")
                return False
                
            records = event['Records']
            if not isinstance(records, list) or not records:
                span.set_tag("validation_error", "invalid_records")
                return False
                
            record = records[0]
            result = (
                isinstance(record, dict) and
                'kinesis' in record and
                isinstance(record['kinesis'], dict) and
                'data' in record['kinesis']
            )
            
            if not result:
                span.set_tag("validation_error", "invalid_kinesis_data")
            
            return result

class SQSEventValidator(EventValidator):
    """Validador para eventos SQS."""
    
    @datadog_trace(service="event_validator", name="validate_sqs")
    def validate(self, event: Dict[str, Any]) -> bool:
        with tracer.current_span() as span:
            add_trace_context(span, {"validator": "sqs"})
            
            if not isinstance(event, dict) or 'Records' not in event:
                span.set_tag("validation_error", "missing_records")
                return False
                
            records = event['Records']
            if not isinstance(records, list) or not records:
                span.set_tag("validation_error", "invalid_records")
                return False
                
            record = records[0]
            result = (
                isinstance(record, dict) and
                'eventSource' in record and
                record['eventSource'] == 'aws:sqs' and
                'body' in record
            )
            
            if not result:
                span.set_tag("validation_error", "invalid_sqs_data")
            
            return result

class DynamoDBEventValidator(EventValidator):
    """Validador para eventos DynamoDB."""
    
    @datadog_trace(service="event_validator", name="validate_dynamodb")
    def validate(self, event: Dict[str, Any]) -> bool:
        with tracer.current_span() as span:
            add_trace_context(span, {"validator": "dynamodb"})
            
            if not isinstance(event, dict) or 'Records' not in event:
                span.set_tag("validation_error", "missing_records")
                return False
                
            records = event['Records']
            if not isinstance(records, list) or not records:
                span.set_tag("validation_error", "invalid_records")
                return False
                
            record = records[0]
            result = (
                isinstance(record, dict) and
                'eventSource' in record and
                record['eventSource'] == 'aws:dynamodb' and
                'dynamodb' in record and
                isinstance(record['dynamodb'], dict)
            )
            
            if not result:
                span.set_tag("validation_error", "invalid_dynamodb_data")
            
            return result

class S3EventValidator(EventValidator):
    """Validador para eventos S3."""
    
    @datadog_trace(service="event_validator", name="validate_s3")
    def validate(self, event: Dict[str, Any]) -> bool:
        with tracer.current_span() as span:
            add_trace_context(span, {"validator": "s3"})
            
            if not isinstance(event, dict) or 'Records' not in event:
                span.set_tag("validation_error", "missing_records")
                return False
                
            records = event['Records']
            if not isinstance(records, list) or not records:
                span.set_tag("validation_error", "invalid_records")
                return False
                
            record = records[0]
            result = (
                isinstance(record, dict) and
                'eventSource' in record and
                record['eventSource'] == 'aws:s3' and
                's3' in record and
                isinstance(record['s3'], dict)
            )
            
            if not result:
                span.set_tag("validation_error", "invalid_s3_data")
            
            return result

class SNSEventValidator(EventValidator):
    """Validador para eventos SNS."""
    
    @datadog_trace(service="event_validator", name="validate_sns")
    def validate(self, event: Dict[str, Any]) -> bool:
        with tracer.current_span() as span:
            add_trace_context(span, {"validator": "sns"})
            
            if not isinstance(event, dict) or 'Records' not in event:
                span.set_tag("validation_error", "missing_records")
                return False
                
            records = event['Records']
            if not isinstance(records, list) or not records:
                span.set_tag("validation_error", "invalid_records")
                return False
                
            record = records[0]
            result = (
                isinstance(record, dict) and
                'eventSource' in record and
                record['eventSource'] == 'aws:sns' and
                'Sns' in record and
                isinstance(record['Sns'], dict)
            )
            
            if not result:
                span.set_tag("validation_error", "invalid_sns_data")
            
            return result

class CloudWatchEventValidator(EventValidator):
    """Validador para eventos CloudWatch."""
    
    @datadog_trace(service="event_validator", name="validate_cloudwatch")
    def validate(self, event: Dict[str, Any]) -> bool:
        with tracer.current_span() as span:
            add_trace_context(span, {"validator": "cloudwatch"})
            
            result = (
                isinstance(event, dict) and
                'detail-type' in event and
                'source' in event and
                'detail' in event and
                isinstance(event['detail'], dict)
            )
            
            if not result:
                span.set_tag("validation_error", "invalid_cloudwatch_data")
            
            return result

class APIGatewayEventValidator(EventValidator):
    """Validador para eventos API Gateway."""
    
    @datadog_trace(service="event_validator", name="validate_api_gateway")
    def validate(self, event: Dict[str, Any]) -> bool:
        with tracer.current_span() as span:
            add_trace_context(span, {"validator": "api_gateway"})
            
            result = (
                isinstance(event, dict) and
                'requestContext' in event and
                isinstance(event['requestContext'], dict) and
                'httpMethod' in event and
                'path' in event
            )
            
            if not result:
                span.set_tag("validation_error", "invalid_api_gateway_data")
            
            return result 