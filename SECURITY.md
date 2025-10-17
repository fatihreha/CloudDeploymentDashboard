# Security Guidelines

## Environment Variables Setup

This project uses environment variables to manage sensitive configuration data. Follow these steps to set up your environment securely:

### 1. Copy Environment Template
```bash
cp .env.example .env
```

### 2. Update Environment Variables
Edit the `.env` file and replace all placeholder values with your actual credentials:

#### Supabase Configuration
- `SUPABASE_URL`: Your Supabase project URL (e.g., https://your-project-ref.supabase.co)
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key

#### Database Configuration
- `DATABASE_URL`: Your Supabase PostgreSQL connection string

### 3. Security Best Practices

#### ✅ DO:
- Keep your `.env` file local and never commit it to version control
- Use strong, unique passwords for all services
- Rotate your API keys regularly
- Use environment-specific configurations (dev, staging, prod)
- Enable two-factor authentication on all cloud services

#### ❌ DON'T:
- Never commit real credentials to version control
- Don't share your `.env` file via email or messaging
- Don't use the same credentials across multiple environments
- Don't hardcode credentials in your source code

### 4. Credential Management

#### For Development:
1. Create your own Supabase project at https://supabase.com
2. Get your project credentials from the Supabase dashboard
3. Update your local `.env` file with these credentials

#### For Production:
1. Use environment variables or secret management services
2. Never use development credentials in production
3. Consider using services like AWS Secrets Manager, Azure Key Vault, or similar

### 5. Placeholder Format Guidelines

When creating example files (like `.env.example`), use generic placeholders that won't trigger secret detection:

#### ✅ GOOD Placeholder Formats:
```
# Database connections
MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/DATABASE_NAME
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME

# API Keys
SUPABASE_ANON_KEY=SUPABASE_ANON_KEY_HERE
SUPABASE_SERVICE_KEY=SUPABASE_SERVICE_KEY_HERE
DIGITALOCEAN_ACCESS_TOKEN=DIGITALOCEAN_TOKEN_HERE
HEROKU_API_KEY=HEROKU_API_KEY_HERE

# Secrets
JWT_SECRET_KEY=YOUR_JWT_SECRET_KEY_HERE
GITHUB_WEBHOOK_SECRET=YOUR_WEBHOOK_SECRET_HERE
```

#### ❌ AVOID These Patterns:
```
# These may trigger secret detection
MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/your-database
API_KEY=sk-1234567890abcdef1234567890abcdef
SECRET_KEY=abc123def456ghi789jkl012mno345pqr
```

### 6. Git Security

The following files are already configured in `.gitignore`:
- `.env` - Contains sensitive environment variables
- `*.log` - May contain sensitive information
- `config/secrets.json` - If you create additional secret files

### 7. Secret Detection and Remediation

If GitHub or other tools detect secrets in your repository:

1. **Immediate Actions:**
   - Rotate and revoke the exposed credentials immediately
   - Update all systems using those credentials
   - Check access logs for any unauthorized usage

2. **Repository Cleanup:**
   - Remove the secrets from the repository history if needed
   - Update example files with proper placeholders
   - Ensure `.gitignore` is properly configured

3. **Prevention:**
   - Use the placeholder formats outlined above
   - Regularly audit your repository for potential secrets
   - Consider using pre-commit hooks to scan for secrets

### 8. Reporting Security Issues

If you discover a security vulnerability, please report it to the project maintainers immediately. Do not create public issues for security vulnerabilities.

## Additional Resources

- [Supabase Security Best Practices](https://supabase.com/docs/guides/platform/security)
- [OWASP Environment Variable Security](https://owasp.org/www-community/vulnerabilities/Insecure_Storage_of_Sensitive_Information)
- [12-Factor App Config](https://12factor.net/config)