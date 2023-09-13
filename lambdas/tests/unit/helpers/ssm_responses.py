from datetime import datetime

MOCK_SINGLE_STRING_PARAMETER_RESPONSE ={
    'Parameter': {
        'Name': 'ssm',
        'Type': 'String',
        'Value': 'some_value',
        'Version': 123,
        'Selector': 'string',
        'SourceResult': 'string',
        'LastModifiedDate': datetime(2015, 1, 1),
        'ARN': 'string',
        'DataType': 'string'
    }
}

MOCK_SINGLE_SECURE_STRING_PARAMETER_RESPONSE ={
    'Parameter': {
        'Name': 'ssm',
        'Type': 'SecureString',
        'Value': 'some_value',
        'Version': 123,
        'Selector': 'string',
        'SourceResult': 'string',
        'LastModifiedDate': datetime(2015, 1, 1),
        'ARN': 'string',
        'DataType': 'string'
    }
}

MOCK_MULTI_STRING_PARAMETERs_RESPONSE ={
        'Parameters': [
            {
                'Name': 'string_1',
                'Type': 'String',
                'Value': 'string_value_1',
                'Version': 123,
                'Selector': 'string',
                'SourceResult': 'string',
                'LastModifiedDate': datetime(2015, 1, 1),
                'ARN': 'string',
                'DataType': 'string'
            },
            {
                'Name': 'string_2',
                'Type': 'String',
                'Value': 'string_value_2',
                'Version': 123,
                'Selector': 'string',
                'SourceResult': 'string',
                'LastModifiedDate': datetime(2015, 1, 1),
                'ARN': 'string',
                'DataType': 'string'
            },
        ],
        'InvalidParameters': [
            'string',
        ]
    }

MOCK_MULTI_MIXED_PARAMETERs_RESPONSE ={
    'Parameters': [
        {
            'Name': 'string_1',
            'Type': 'String',
            'Value': 'string_value_1',
            'Version': 123,
            'Selector': 'string',
            'SourceResult': 'string',
            'LastModifiedDate': datetime(2015, 1, 1),
            'ARN': 'string',
            'DataType': 'string'
        },
        {
            'Name': 'string_2',
            'Type': 'String',
            'Value': 'string_value_2',
            'Version': 123,
            'Selector': 'string',
            'SourceResult': 'string',
            'LastModifiedDate': datetime(2015, 1, 1),
            'ARN': 'string',
            'DataType': 'string'
        },
    ],
    'InvalidParameters': [
        'string',
    ]
}
