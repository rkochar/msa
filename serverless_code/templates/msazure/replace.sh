#!/bin/bash

URL=$(az storage account show-connection-string --name storageaccountfaasmonad --resource-group resourcegroup | jq '.connectionString')
echo "[URL]: $URL"
sed -i.bak "s|azurewebjobsstorage|$URL|g" local.settings.json
