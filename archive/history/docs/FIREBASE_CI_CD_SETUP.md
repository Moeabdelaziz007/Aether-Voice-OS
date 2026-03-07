# 🔥 Firebase CI/CD Setup Guide

## Overview

This guide walks you through setting up automated Firebase deployments for AetherOS.

## Prerequisites

- Firebase CLI installed (`npm install -g firebase-tools`)
- Firebase project: `notional-armor-456623-e8`
- GitHub repository with admin access

## Step 1: Generate Firebase CI Token

### Option A: Using Firebase CLI (Recommended)

```bash
# Login to Firebase
firebase login:ci

# This will output a token like:
# 1//0eXaMpLeToKeN...
```

**Important:** Save this token securely - you won't be able to see it again!

### Option B: Using Service Account

```bash
# In Google Cloud Console:
# 1. Go to https://console.cloud.google.com/iam-admin/serviceaccounts
# 2. Create new service account: "github-actions-deployer"
# 3. Grant role: "Firebase Hosting Admin"
# 4. Create JSON key and download
# 5. Save as FIREBASE_SERVICE_ACCOUNT secret in GitHub
```

## Step 2: Configure GitHub Secrets

Navigate to your GitHub repository → Settings → Secrets and variables → Actions

### Required Secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `FIREBASE_TOKEN` | Token from Step 1 | Firebase CI authentication |
| `NEXT_PUBLIC_GEMINI_KEY` | Your Gemini API key | Frontend AI integration |
| `NEXT_PUBLIC_AETHER_GATEWAY_URL` | `ws://localhost:18789` | Backend gateway URL |
| `DISCORD_WEBHOOK` *(Optional)* | Discord webhook URL | Deployment notifications |

### Adding Secrets:

1. Click "New repository secret"
2. Enter the secret name and value
3. Click "Add secret"
4. Repeat for all required secrets

## Step 3: Verify Configuration

### Test Locally First:

```bash
# Build the portal
cd apps/portal
npm install
npm run build

# Test Firebase deploy (dry run)
firebase hosting:channel:deploy test-preview --expires 30m
```

### Verify GitHub Workflow:

1. Push a small change to `main` branch
2. Go to GitHub → Actions tab
3. Watch "🔥 Firebase Deploy" workflow run
4. Check all stages complete successfully

## Step 4: Deployment Workflow

### Automatic Deployment:

The workflow triggers on:
- ✅ Every push to `main` branch (that modifies `apps/portal/**`)
- ✅ Manual trigger via "Run workflow" button in GitHub Actions

### Deployment Stages:

```
1. 🔨 Build & Verify
   ├─ Install Node.js dependencies
   ├─ TypeScript type checking
   ├─ Next.js production build
   └─ Upload build artifacts

2. 🚀 Deploy to Firebase
   ├─ Download build artifacts
   ├─ Deploy to Firebase Hosting
   └─ Create deployment status

3. 🔍 Validate Deployment
   ├─ Health check (HTTP 200)
   ├─ Asset verification
   └─ Lighthouse performance audit

4. 📢 Notifications
   └─ Discord webhook notification
```

## Step 5: Monitor Deployments

### GitHub Actions:
- View logs: https://github.com/YOUR_REPO/actions
- Filter by "Firebase Deploy" workflow

### Firebase Console:
- Hosting dashboard: https://console.firebase.google.com/project/YOUR_PROJECT_ID/hosting
- See deployment history and rollback options

## Troubleshooting

### ❌ Build Fails:
```bash
# Test build locally
cd apps/portal
npm ci
npm run build

# Check for TypeScript errors
npx tsc --noEmit
```

### ❌ Deploy Fails with "Permission Denied":
- Verify `FIREBASE_TOKEN` secret is correct
- Regenerate token: `firebase login:ci`
- Update GitHub secret

### ❌ Slow Deployments:
- Enable caching in workflow (already configured)
- Reduce build artifact retention days (default: 7)

### ❌ 404 After Deploy:
- Wait 30 seconds for CDN propagation
- Check `firebase.json` rewrites configuration
- Verify build output in `apps/portal/out/`

## Advanced Configuration

### Deploy Previews for PRs:

Add to `.github/workflows/firebase_deploy.yml`:

```yaml
on:
  pull_request:
    branches: [main]
```

Then modify deploy step:
```yaml
- name: Deploy Preview
  run: |
    firebase hosting:channel:deploy pr-${{ github.event.pull_request.number }} \
      --token "${{ secrets.FIREBASE_TOKEN }}" \
      --expires 7d
```

### Rollback to Previous Version:

```bash
# List versions
firebase hosting:releases list

# Rollback
firebase hosting:rollback
```

### Custom Domain:

1. Firebase Console → Hosting → Add custom domain
2. Follow DNS configuration steps
3. Update `.firebaserc` if needed

## Cost Optimization

Firebase Hosting Free Tier includes:
- ✅ 10 GB storage
- ✅ 360 MB/day transfer
- ✅ Unlimited SSL certificates

For higher usage, upgrade to Blaze plan (pay-as-you-go).

## Security Best Practices

- ✅ Never commit `FIREBASE_TOKEN` to repository
- ✅ Use GitHub Secrets for all sensitive values
- ✅ Rotate tokens every 90 days
- ✅ Enable two-factor authentication on Firebase account
- ✅ Review deployment logs regularly

## Support Resources

- Firebase Docs: https://firebase.google.com/docs/hosting
- GitHub Actions: https://docs.github.com/en/actions
- Next.js Build: https://nextjs.org/docs/deployment

---

**Last Updated:** March 7, 2026  
**Project:** notional-armor-456623-e8
