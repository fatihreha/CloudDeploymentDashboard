# 🐳 Azure App Service Container Deployment Script
# Cloud Deployment Dashboard - Production Ready Container Deployment

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "rg-cloud-deployment-dashboard",
    
    [Parameter(Mandatory=$false)]
    [string]$AppName = "cloud-deployment-dashboard",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory=$false)]
    [string]$ContainerRegistry = "clouddeploymentdashboard",
    
    [Parameter(Mandatory=$false)]
    [string]$ImageName = "dashboard-app",
    
    [Parameter(Mandatory=$false)]
    [string]$ImageTag = "latest"
)

Write-Host "🚀 Starting Azure App Service Container Deployment..." -ForegroundColor Green
Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host "   App Name: $AppName" -ForegroundColor White
Write-Host "   Location: $Location" -ForegroundColor White
Write-Host "   Registry: $ContainerRegistry.azurecr.io" -ForegroundColor White
Write-Host "   Image: $ImageName`:$ImageTag" -ForegroundColor White

# 1. Login to Azure
Write-Host "`n🔐 Step 1: Azure Login" -ForegroundColor Cyan
az login

# 2. Create Resource Group
Write-Host "`n📦 Step 2: Creating Resource Group" -ForegroundColor Cyan
az group create --name $ResourceGroup --location $Location

# 3. Create Azure Container Registry
Write-Host "`n🏗️ Step 3: Creating Azure Container Registry" -ForegroundColor Cyan
az acr create --resource-group $ResourceGroup --name $ContainerRegistry --sku Basic --admin-enabled true

# 4. Build and Push Docker Image
Write-Host "`n🐳 Step 4: Building and Pushing Docker Image" -ForegroundColor Cyan
az acr build --registry $ContainerRegistry --image "$ImageName`:$ImageTag" --file Dockerfile.azure .

# 5. Create App Service Plan
Write-Host "`n📋 Step 5: Creating App Service Plan" -ForegroundColor Cyan
az appservice plan create --name "$AppName-plan" --resource-group $ResourceGroup --sku B1 --is-linux

# 6. Get ACR credentials
Write-Host "`n🔍 Step 6: Getting ACR credentials" -ForegroundColor Cyan
$acrLoginServer = az acr show --name $ContainerRegistry --query loginServer --output tsv
$acrUsername = az acr credential show --name $ContainerRegistry --query username --output tsv
$acrPassword = az acr credential show --name $ContainerRegistry --query passwords[0].value --output tsv

# 7. Create Web App with Container
Write-Host "`n🌐 Step 7: Creating Web App with Container" -ForegroundColor Cyan
az webapp create --resource-group $ResourceGroup --plan "$AppName-plan" --name $AppName --deployment-container-image-name "$acrLoginServer/$ImageName`:$ImageTag"

# 8. Configure Container Registry
Write-Host "`n🔑 Step 8: Configuring Container Registry" -ForegroundColor Cyan
az webapp config container set --name $AppName --resource-group $ResourceGroup --docker-custom-image-name "$acrLoginServer/$ImageName`:$ImageTag" --docker-registry-server-url "https://$acrLoginServer" --docker-registry-server-user $acrUsername --docker-registry-server-password $acrPassword

# 9. Configure App Settings
Write-Host "`n⚙️ Step 9: Configuring App Settings" -ForegroundColor Cyan
az webapp config appsettings set --resource-group $ResourceGroup --name $AppName --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=false WEBSITES_PORT=8000 FLASK_ENV=production DOCKER_ENABLE_CI=true

# 10. Get App URL
Write-Host "`n🌍 Step 10: Getting Application URL" -ForegroundColor Cyan
$appUrl = az webapp show --name $AppName --resource-group $ResourceGroup --query defaultHostName --output tsv
Write-Host "   Application URL: https://$appUrl" -ForegroundColor Green

Write-Host "`n🎉 Deployment Completed Successfully!" -ForegroundColor Green
Write-Host "📱 Application URL: https://$appUrl" -ForegroundColor Yellow
