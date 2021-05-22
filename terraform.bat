call config_cloud.cmd

terraform init
terraform plan
terraform apply -auto-approve
echo En attente du demarrage de la VM ...

call config_terraform_cloud.cmd
ssh -o StrictHostKeyChecking=no -i %key_path% ec2-user@%dns%
pause