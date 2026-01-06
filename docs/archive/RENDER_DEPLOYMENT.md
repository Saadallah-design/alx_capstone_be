# Render Deployment Guide 🚀

## Prerequisites
- GitHub repository with your code
- Render account (free tier available)
- PostgreSQL database (Render provides this)

---

## Step 1: Create a PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New** → **PostgreSQL**
3. Configure:
   - **Name**: `alx-car-rental-db` (or your choice)
   - **Database**: `alx_rental`
   - **User**: `alx_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free (or paid for production)
4. Click **Create Database**
5. **Save the Internal Database URL** - you'll need this for environment variables

---

## Step 2: Create a Web Service on Render

1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `alx-car-rental-api`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn carRentalConfig.wsgi:application`
   - **Plan**: Free (or paid for production)

---

## Step 3: Set Environment Variables

In the Render dashboard for your web service, go to **Environment** and add:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here-generate-a-new-one
DEBUG=False
RENDER_EXTERNAL_HOSTNAME=your-app-name.onrender.com

# Database (Copy from your PostgreSQL service)
DATABASE_URL=postgresql://user:password@host:port/database

# CORS (Your frontend URL)
CORS_ALLOWED_ORIGINS=https://alx-capstone-fe.vercel.app

# Stripe
STRIPE_TEST_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Site URL (Your frontend URL for redirects)
SITE_URL=https://alx-capstone-fe.vercel.app
```

### Important Notes:
- **SECRET_KEY**: Generate a new one using `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- **DATABASE_URL**: Render auto-provides this if you link the database
- **RENDER_EXTERNAL_HOSTNAME**: Will be `your-service-name.onrender.com`

---

## Step 4: Deploy

1. Click **Create Web Service**
2. Render will automatically:
   - Clone your repo
   - Run `./build.sh` (installs deps, migrates DB, collects static files)
   - Start the app with `gunicorn`

---

## Step 5: Verify Deployment

### Check API Health
```bash
curl https://your-app-name.onrender.com/api/schema/
```

### Check Admin Panel
```bash
https://your-app-name.onrender.com/admin/
```

### Create Superuser (via Render Shell)
1. Go to your web service dashboard
2. Click **Shell** tab
3. Run:
```bash
python manage.py createsuperuser
```

---

## Step 6: Configure Stripe Webhooks for Production

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Click **Add endpoint**
3. Enter: `https://your-app-name.onrender.com/api/payments/webhook/`
4. Select events: `checkout.session.completed`, `payment_intent.payment_failed`, `charge.refunded`
5. Copy the **Signing Secret** and update `STRIPE_WEBHOOK_SECRET` in Render environment variables

---

## Troubleshooting

### Build Fails
- Check **Logs** in Render dashboard
- Common issues:
  - Missing dependencies in `requirements.txt`
  - Database connection errors (check `DATABASE_URL`)
  - Static files errors (ensure `STATIC_ROOT` is set)

### App Crashes
- Check **Logs** for Python errors
- Verify all environment variables are set
- Ensure `DEBUG=False` in production

### Static Files Not Loading
- Verify `whitenoise` is in `MIDDLEWARE`
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Run `python manage.py collectstatic` manually in Shell

### Database Connection Issues
- Ensure `DATABASE_URL` is correct
- Check if database is in the same region
- Verify database is running (check PostgreSQL service)

---

## Production Checklist ✅

- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY` (never commit to git)
- [ ] `ALLOWED_HOSTS` includes Render domain
- [ ] Database backups enabled
- [ ] CORS configured for frontend domain only
- [ ] Stripe webhook endpoint updated
- [ ] SSL/HTTPS enabled (Render provides this automatically)
- [ ] Environment variables secured
- [ ] Superuser account created
- [ ] Static files collected and served

---

## Updating Your Deployment

1. Push changes to `main` branch on GitHub
2. Render will automatically detect and redeploy
3. Monitor the **Logs** during deployment

---

## Cost Optimization (Free Tier)

Render free tier limitations:
- App sleeps after 15 minutes of inactivity
- 750 hours/month free (enough for one service)
- Database has 90-day expiration (backup your data!)

**Tip**: For production, upgrade to paid tier for:
- No sleep
- Persistent database
- Better performance
