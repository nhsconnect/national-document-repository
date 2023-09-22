MOCK_S3_OBJECT_CREATED = {
	'Records': [
		{
			'eventVersion': '2.1',
			'eventSource': 'aws:s3',
			'awsRegion': 'eu-west-2',
			'eventTime': '2023-09-22T14:47:38.916Z',
			'eventName': 'ObjectCreated:Put',
			'userIdentity': {
				'principalId': 'AWS:AROAXYSUA44VTSOBR6O2X:alexandra.herbert1'
			},
			'requestParameters': {
				'sourceIPAddress': '88.98.242.53'
			},
			'responseElements': {
				'x-amz-request-id': 'G87VZVDY1AJ1ZKS6',
				'x-amz-id-2': 'WCEMLES+7IYahvchmXZVP+AC/xX9smt5SMKdVo9UlWOXYld2hodRApxUvfVHQ/vsKFs6pBUvcRHCfcbqlwuWQ1TCV6FPmnFT'
			},
			's3': {
				's3SchemaVersion': '1.0',
				'configurationId': 'a21ecf1d-f5c6-4f58-b4ae-658032c6ecff',
				'bucket': {
					'name': 'document-store-bucket',
					'ownerIdentity': {
						'principalId': 'A1U49MOL8I39U7'
					},
					'arn': 'arn:aws:s3:::document-store-terraform-state'
				},
				'object': {
					'key': '941450fa6380d82edf0b5515b14997f2_e4c19c48-9721-4a50-af82-af2a11083833_1200x1200-2751689439.jpg',
					'size': 55897,
					'eTag': '8774a1899a352114dde43e875b881df1',
					'versionId': 'nnLPppJuDyBmav5JjBpxzpddGiFaE0tf',
					'sequencer': '00650DA90AD294D658'
				}
			}
		}
	]
}
