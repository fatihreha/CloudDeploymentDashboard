# 🚀 Azure App Service Simple Deployment (Python)
# Docker olmadan direkt Python deployment

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "rg-cloud-dashboard",
    
    [Parameter(Mandatory=$false)]
    [string]$AppName = "cloud-dashboard-$(Get-Random -Minimum 1000 -Maximum 9999)",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "East US"
)

Write-Host "🚀 Azure App Service Python Deployment Başlıyor..." -ForegroundColor Green

# 1. Resource Group oluştur
Write-Host "📦 Resource Group oluşturuluyor..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location

# 2. App Service Plan oluştur (Free tier)
Write-Host "📋 App Service Plan oluşturuluyor..." -ForegroundColor Yellow
az appservice plan create --name "$AppName-plan" --resource-group $ResourceGroup --sku F1 --is-linux

# 3. Web App oluştur (Python 3.9)
Write-Host "🌐 Web App oluşturuluyor..." -ForegroundColor Yellow
az webapp create --resource-group $ResourceGroup --plan "$AppName-plan" --name $AppName --runtime "PYTHON|3.9"

# 4. Environment variables ayarla
Write-Host "⚙️ Environment variables ayarlanıyor..." -ForegroundColor Yellow
az webapp config appsettings set --resource-group $ResourceGroup --name $AppName --settings @azure-app-settings.json

# 5. Startup command ayarla
Write-Host "🔧 Startup command ayarlanıyor..." -ForegroundColor Yellow
az webapp config set --resource-group $ResourceGroup --name $AppName --startup-file "startup.py"

Write-Host "✅ Deployment tamamlandı!" -ForegroundColor Green
Write-Host "🌐 URL: https://$AppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "📋 Resource Group: $ResourceGroup" -ForegroundColor White

# Git deployment için
Write-Host "📝 Git deployment için:" -ForegroundColor Yellow
Write-Host "   az webapp deployment source config --name $AppName --resource-group $ResourceGroup --repo-url https://github.com/YOUR_USERNAME/YOUR_REPO --branch main --manual-integration" -ForegroundColor White