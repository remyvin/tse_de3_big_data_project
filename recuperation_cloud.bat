aws s3 cp s3://rrt-data-storage-1/classification.csv classification.csv
aws s3 cp s3://rrt-data-storage-1/predictions.csv predictions.csv
aws s3 cp s3://rrt-data-storage-1/words.csv words.csv

mongoimport -d bdp -c classification_report.csv --type csv --file classification_report.csv --headerline
mongoimport -d bdp -c predictions.csv --type csv --file predictions.csv --headerline
mongoimport -d bdp -c words.csv --type csv --file words.csv --headerline