resource "aws_lambda_function" "this" {
    function_name = "${var.project_name}web-logic-core"
    handler       = "web_logic_core.handler"
    runtime       = "python3.9"
    role          = aws_iam_role.lambda_exec.arn
    filename      = "s3://${var.code_bucket}/lambda_functions/web_logic_core.zip"
}

resource "aws_iam_role" "lambda_exec" {
    name = "lambda_exec_role"
    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [{
            Action = "sts:AssumeRole"
            Effect = "Allow"
            Principal = {
                Service = "lambda.amazonaws.com"
            }
        }]
    })
}

resource "aws_iam_policy" "lambda_exec_policy" {
  name = "policy-618033"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
            "Sid": "AllowLambdaToAccessS3DataLake",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::tfm-educ-app-silver",
                "arn:aws:s3:::tfm-educ-app-silver/*",
                "arn:aws:s3:::tfm-educ-app-bronze",
                "arn:aws:s3:::tfm-educ-app-bronze/*",
                "arn:aws:s3:::tfm-educ-app-gold",
                "arn:aws:s3:::tfm-educ-app-gold/*",
            ]
        },
        {
            "Sid": "AllowLambdaToAccessCognitoUserPool",
            "Effect": "Allow",
            "Action": [
                "cognito-idp:AdminGetUser",
                "cognito-idp:GetUser",
                "cognito-idp:ListUsers",
                "cognito-idp:AdminUpdateUserAttributes",
                "cognito-idp:AdminAddUserToGroup",
                "cognito-idp:AdminRemoveUserFromGroup",
                "cognito-idp:AdminConfirmSignUp",
                "cognito-idp:AdminDeleteUser"
            ],
            "Resource": "*"
        },
        {
			"Sid": "AllowLambdaToData",
			"Effect": "Allow",
			"Action": [
				"lakeformation:GetDataAccess",
				"quicksight:DescribeUser",
                "quicksight:ListUsers",
                "quicksight:DescribeGroup",
                "quicksight:ListGroups",
                "quicksight:DescribeDashboard",
                "quicksight:ListDashboards",
                "quicksight:DescribeDataSet",
                "quicksight:ListDataSets",
                "quicksight:DescribeDataSource",
                "quicksight:ListDataSources",
                "quicksight:DescribeAnalysis",
                "quicksight:ListAnalyses",
                "quicksight:DescribeIngestion",
                "quicksight:ListIngestions",
                "quicksight:StartIngestion", // Para actualizar datasets
                "quicksight:GenerateEmbedUrlForAnonymousUser", // Para incrustar dashboards sin usuario QS
                "quicksight:GenerateEmbedUrlForRegisteredUser",  // Para incrustar dashboards con usuario QS
                "quicksight:CreateDashboard",
                "quicksight:UpdateDashboard",
                "quicksight:DeleteDashboard",
                "dynamodb:ListTables",
				"dynamodb:BatchGetItem",
				"dynamodb:DescribeTable",
				"dynamodb:GetItem",
				"dynamodb:GetRecords",
				"dynamodb:Query",
				"dynamodb:Scan",
				"dynamodb:BatchWriteItem",
				"dynamodb:DeleteItem"
			],
			"Resource": [
				"*"
			]
		}
    ]
  })
}


resource "aws_iam_role_policy_attachment" "lambda_exec-attach" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_exec_policy.arn
}

