# 🚀 AetherOS Deployment Quick Reference

## Automated CI/CD Workflow

### ✅ What Happens on Every Push to `main`

```yaml
Trigger: Push to main branch (apps/portal/**)
         OR manual workflow dispatch
         
Pipeline:
  1. 🔨 Build & Verify (15-20 min)
     ├─ Checkout code
     ├─ Install Node.js dependencies  
     ├─ TypeScript type check
     ├─ Next.js production build
     └─ Upload build artifacts
     
  2. 🚀 Firebase Deploy (2-5 min)
     ├─ Download artifacts
     ├─ Authenticate with Firebase
     ├─ Deploy to Firebase Hosting
     └─ Create GitHub deployment status
     
  3. 🔍 Validation (1-2 min)
     ├─ Wait for CDN propagation
     ├─ Health check (HTTP 200)
     ├─ Asset verification
     └─ Lighthouse performance audit
     
  4. 📢 Notifications
     └─ Discord webhook (if configured)
```

## Manual Deployment

### Local Build & Deploy:
```bash
# Build locally
cd apps/portal
npm install
npm run build

# Deploy to Firebase
firebase deploy --only hosting --project notional-armor-456623-e8
```

### Using Deployment Script:
```bash
# Deploy both Firebase + Local
bash scripts/deploy.sh

# Deploy Firebase only
bash scripts/deploy.sh --firebase

# Deploy local only
bash scripts/deploy.sh --local
```

## Rollback

### Quick Rollback:
```bash
bash scripts/firebase_rollback.sh
```

### Manual Rollback:
```bash
# List versions
firebase hosting:releases list --project notional-armor-456623-e8

# Rollback to specific version
firebase hosting:rollback 10 --project notional-armor-456623-e8
```

## Required Secrets

Configure in GitHub → Settings → Secrets and variables → Actions:

| Secret | Value | Required |
|--------|-------|----------|
| `FIREBASE_TOKEN` | Firebase CI token | ✅ Yes |
| `NEXT_PUBLIC_GEMINI_KEY` | Gemini API key | ✅ Yes |
| `NEXT_PUBLIC_AETHER_GATEWAY_URL` | Backend URL | ✅ Yes |
| `DISCORD_WEBHOOK` | Discord webhook | ❌ Optional |

### Get Firebase Token:
```bash
firebase login:ci
# Copy the token and add to GitHub secrets
```

## Monitoring

### GitHub Actions:
https://github.com/YOUR_REPO/actions/workflows/firebase_deploy.yml

### Firebase Console:
https://console.firebase.google.com/project/notional-armor-456623-e8/hosting

### Live Site:
https://notional-armor-456623-e8.web.app

## Troubleshooting

### Build Fails:
```bash
cd apps/portal
npm ci
npm run build  # Test locally
```

### Deploy Permission Error:
- Regenerate Firebase token: `firebase login:ci`
- Update GitHub secret: `FIREBASE_TOKEN`

### Slow Deployments:
- Check artifact size (should be <50MB)
- Review workflow logs for bottlenecks
- Enable npm caching (already configured)

### 404 After Deploy:
- Wait 30-60 seconds for CDN propagation
- Hard refresh browser (Cmd+Shift+R)
- Check Firebase Console for errors

## Optimization Tips

1. **Reduce Build Time:**
   - Keep `node_modules` cached (automatic)
   - Use incremental builds when possible
   - Split large components

2. **Minimize Bundle Size:**
   ```bash
   npm run analyze  # Check bundle size
   ```

3. **Faster Feedback:**
   - Run tests before pushing
   - Use PR preview channels
   - Enable parallel jobs

## Security Checklist

- ✅ Never commit `.env` files
- ✅ Rotate Firebase token every 90 days
- ✅ Use GitHub Secrets for all sensitive data
- ✅ Enable 2FA on Firebase account
- ✅ Review deployment logs weekly
- ✅ Restrict deployment permissions

## Cost Management

Firebase Free Tier (Spark):
- 10 GB storage
- 360 MB/day transfer
- Unlimited SSL

Blaze Plan (Pay-as-you-go):
- $0.026/GB additional storage
- $0.12/GB additional transfer

Monitor usage: https://console.firebase.google.com/project/YOUR_PROJECT_ID/usage

---

**Last Updated:** March 7, 2026  
**Workflow File:** `.github/workflows/firebase_deploy.yml`  
**Project ID:** notional-armor-456623-e8
