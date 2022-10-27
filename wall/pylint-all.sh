for file in *.py; do 
  echo "File: $file"; pylint --extension-pkg-whitelist=pygame $file; 
done
