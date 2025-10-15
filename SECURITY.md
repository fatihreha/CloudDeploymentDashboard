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

### 5. Git Security

The following files are already configured in `.gitignore`:
- `.env` - Contains sensitive environment variables
- `*.log` - May contain sensitive information
- `config/secrets.json` - If you create additional secret files

### 6. Reporting Security Issues

If you discover a security vulnerability, please report it to the project maintainers immediately. Do not create public issues for security vulnerabilities.

## Additional Resources

- [Supabase Security Best Practices](https://supabase.com/docs/guides/platform/security)
- [OWASP Environment Variable Security](https://owasp.org/www-community/vulnerabilities/Insecure_Storage_of_Sensitive_Information)
- [12-Factor App Config](https://12factor.net/config)