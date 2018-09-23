#!/bin/bash
mkdir src/lib
pip install -r requirements.txt -t src/lib/
cd src

echo "deploying $lambda >>>>>>>>>"
zip -qr ../prof-hubert.zip *

### Create the role for the lambda to assume
role="lambda_basic_execution"
function_name="$lambda"
handler_name="main.handler"
package_file=../prof-hubert.zip

### Update the function
runtime=python2.7
aws lambda update-function-code \
  --function-name $function_name \
  --zip-file fileb://$package_file \
  --region us-east-1


rm ../prof-hubert.zip
rm -rf lib

echo 'End of the deploy >>>>>>>>>'

