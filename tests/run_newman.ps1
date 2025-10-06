
param(
  [string]$Collection = ".\tests\Laburen.postman_collection.json",
  [string]$Env = ".\tests\Laburen.postman_environment.json"
)
docker run --rm -v "${PWD}\tests:/etc/newman" postman/newman \
  run "/etc/newman/$(Split-Path $Collection -Leaf)" -e "/etc/newman/$(Split-Path $Env -Leaf)" --reporters cli
