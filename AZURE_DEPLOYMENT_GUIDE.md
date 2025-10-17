# 🚀 Azure Student Pack ile Cloud Deployment Dashboard Kurulumu

## 📋 **ÖN KOŞULLAR**

### 1. Azure Student Pack Aktivasyonu
- [Azure for Students](https://azure.microsoft.com/tr-tr/free/students/) sayfasına git
- Öğrenci e-posta adresinle kayıt ol
- **$100 kredi** ve **12 ay ücretsiz** hizmet al
- **Kredi kartı gerektirmez!** ✅

### 2. Gerekli Araçlar
```bash
# Azure CLI kurulumu
winget install Microsoft.AzureCLI

# Git kurulumu (eğer yoksa)
winget install Git.Git

# Node.js kurulumu (GitHub Actions için)
winget install OpenJS.NodeJS
```

---

## 🏗️ **AZURE KAYNAKLARI OLUŞTURMA**

### 1. Azure CLI ile Giriş
```bash
# Azure'a giriş yap
az login

# Subscription'ı kontrol et
az account show

# Resource group oluştur
az group create --name rg-cloud-dashboard --location "East US"
```

### 2. Azure App Service Oluşturma
```bash
# App Service Plan oluştur (F1 - Ücretsiz tier)
az appservice plan create \
  --name plan-cloud-dashboard \
  --resource-group rg-cloud-dashboard \
  --sku F1 \
  --is-linux

# Web App oluştur
az webapp create \
  --name cloud-deployment-dashboard-[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard \
  --plan plan-cloud-dashboard \
  --runtime "PYTHON|3.9"
```

### 3. Azure PostgreSQL Flexible Server (Opsiyonel)
```bash
# PostgreSQL server oluştur (Burstable tier - düşük maliyet)
az postgres flexible-server create \
  --name postgres-cloud-dashboard-[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard \
  --location "East US" \
  --admin-user azureuser \
  --admin-password [STRONG-PASSWORD] \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32

# Database oluştur
az postgres flexible-server db create \
  --resource-group rg-cloud-dashboard \
  --server-name postgres-cloud-dashboard-[UNIQUE-ID] \
  --database-name cloud_deployment_dashboard
```

---

## ⚙️ **UYGULAMA KONFIGÜRASYONU**

### 1. Environment Variables Ayarlama
```bash
# App Service'e environment variables ekle
az webapp config appsettings set \
  --name cloud-deployment-dashboard-[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard \
  --settings \
    FLASK_ENV=production \
    SECRET_KEY=[RANDOM-SECRET-KEY] \
    SUPABASE_URL=[YOUR-SUPABASE-URL] \
    SUPABASE_ANON_KEY=[YOUR-SUPABASE-ANON-KEY] \
    SUPABASE_SERVICE_KEY=[YOUR-SUPABASE-SERVICE-KEY]
```

### 2. Startup Command Ayarlama
```bash
# Startup command'ı ayarla
az webapp config set \
  --name cloud-deployment-dashboard-[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard \
  --startup-file "startup.py"
```

---

## 🔄 **GITHUB ACTIONS DEPLOYMENT**

### 1. Azure Service Principal Oluşturma
```bash
# Service Principal oluştur
az ad sp create-for-rbac \
  --name "sp-cloud-dashboard" \
  --role contributor \
  --scopes /subscriptions/[SUBSCRIPTION-ID]/resourceGroups/rg-cloud-dashboard \
  --sdk-auth

# Çıktıyı kopyala - GitHub Secrets'a ekleyeceğiz
```

### 2. GitHub Repository Secrets
GitHub repository'nde **Settings > Secrets and variables > Actions** bölümüne git:

```
AZURE_CREDENTIALS = {Service Principal JSON çıktısı}
AZURE_WEBAPP_PUBLISH_PROFILE = {App Service'den indir}
AZURE_WEBAPP_NAME = cloud-deployment-dashboard-[UNIQUE-ID]
AZURE_RESOURCE_GROUP = rg-cloud-dashboard
```

### 3. Publish Profile İndirme
```bash
# Publish profile'ı indir
az webapp deployment list-publishing-profiles \
  --name cloud-deployment-dashboard-[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard \
  --xml
```

---

## 🐳 **AZURE CONTAINER APPS (ALTERNATİF)**

### 1. Container Apps Environment
```bash
# Container Apps extension ekle
az extension add --name containerapp

# Container Apps environment oluştur
az containerapp env create \
  --name env-cloud-dashboard \
  --resource-group rg-cloud-dashboard \
  --location "East US"
```

### 2. Container Registry
```bash
# Azure Container Registry oluştur
az acr create \
  --name acrcloudDashboard[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard \
  --sku Basic \
  --admin-enabled true

# Registry'ye giriş yap
az acr login --name acrcloudDashboard[UNIQUE-ID]
```

### 3. Container App Deploy
```bash
# Container app oluştur
az containerapp create \
  --name cloud-dashboard-app \
  --resource-group rg-cloud-dashboard \
  --environment env-cloud-dashboard \
  --image acrcloudDashboard[UNIQUE-ID].azurecr.io/clouddeploymentdashboard:latest \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3
```

---

## 🔧 **DEPLOYMENT ADIMLARI**

### 1. Kod Hazırlığı
```bash
# Repository'yi clone et
git clone [YOUR-REPO-URL]
cd cloud-deployment-dashboard

# Azure branch'i oluştur
git checkout -b azure-deployment

# Azure dosyalarını commit et
git add .
git commit -m "Azure deployment configuration"
git push origin azure-deployment
```

### 2. GitHub Actions Tetikleme
- GitHub'da **Actions** sekmesine git
- **Azure Deployment** workflow'unu manuel olarak çalıştır
- Deployment loglarını takip et

### 3. Domain ve SSL
```bash
# Custom domain ekle (opsiyonel)
az webapp config hostname add \
  --webapp-name cloud-deployment-dashboard-[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard \
  --hostname [YOUR-DOMAIN.com]

# SSL sertifikası (Let's Encrypt - ücretsiz)
az webapp config ssl bind \
  --certificate-thumbprint [CERT-THUMBPRINT] \
  --ssl-type SNI \
  --name cloud-deployment-dashboard-[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard
```

---

## 📊 **MONİTORİNG VE LOGGING**

### 1. Application Insights
```bash
# Application Insights oluştur
az monitor app-insights component create \
  --app cloud-dashboard-insights \
  --location "East US" \
  --resource-group rg-cloud-dashboard \
  --application-type web

# App Service'e bağla
az webapp config appsettings set \
  --name cloud-deployment-dashboard-[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=[INSTRUMENTATION-KEY]
```

### 2. Log Stream
```bash
# Canlı logları izle
az webapp log tail \
  --name cloud-deployment-dashboard-[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard
```

---

## 💰 **MALİYET OPTİMİZASYONU**

### Ücretsiz Tier Kullanımı
- **App Service**: F1 (Free) - 1GB disk, 1GB RAM
- **PostgreSQL**: Burstable B1ms - $7.12/ay (Student kredisinden)
- **Container Registry**: Basic - $5/ay
- **Application Insights**: İlk 5GB ücretsiz

### Maliyet Takibi
```bash
# Maliyet analizi
az consumption usage list \
  --start-date 2024-01-01 \
  --end-date 2024-01-31

# Budget oluştur
az consumption budget create \
  --budget-name student-budget \
  --amount 50 \
  --resource-group rg-cloud-dashboard
```

---

## 🚨 **SORUN GİDERME**

### Yaygın Hatalar

1. **Deployment Hatası**
```bash
# Deployment loglarını kontrol et
az webapp log download \
  --name cloud-deployment-dashboard-[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard
```

2. **Database Bağlantı Hatası**
```bash
# Connection string'i kontrol et
az webapp config connection-string list \
  --name cloud-deployment-dashboard-[UNIQUE-ID] \
  --resource-group rg-cloud-dashboard
```

3. **SSL Sertifika Hatası**
```bash
# SSL binding'i kontrol et
az webapp config ssl list \
  --resource-group rg-cloud-dashboard
```

### Destek Kanalları
- **Azure Student Support**: [Azure Education Hub](https://portal.azure.com/#blade/Microsoft_Azure_Education/EducationMenuBlade/overview)
- **Azure Documentation**: [docs.microsoft.com/azure](https://docs.microsoft.com/azure)
- **Community Support**: [Microsoft Q&A](https://docs.microsoft.com/answers/)

---

## ✅ **DEPLOYMENT CHECKLIST**

- [ ] Azure Student Pack aktif
- [ ] Resource Group oluşturuldu
- [ ] App Service/Container App oluşturuldu
- [ ] Database kuruldu (Supabase veya Azure PostgreSQL)
- [ ] Environment variables ayarlandı
- [ ] GitHub Secrets konfigüre edildi
- [ ] GitHub Actions workflow çalıştırıldı
- [ ] SSL sertifikası aktif
- [ ] Monitoring kuruldu
- [ ] Domain bağlandı (opsiyonel)

---

## 🎯 **SONUÇ**

Bu rehberi takip ederek Cloud Deployment Dashboard'unuzu Azure'da **tamamen ücretsiz** olarak çalıştırabilirsiniz. Azure Student Pack ile **$100 kredi** ve **12 ay ücretsiz** hizmetlerden faydalanabilirsiniz.

**Önemli**: Kredi kartı bilgisi gerektirmez ve otomatik ücretlendirme yoktur! 🎓✨