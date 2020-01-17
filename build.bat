pip install -r requirements.txt -t .dependencies
powershell Remove-Item output.zip -ErrorAction Ignore
powershell Compress-Archive -Path .dependencies, src/* -DestinationPath output.zip
