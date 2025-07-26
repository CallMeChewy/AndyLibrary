# DNS Migration Instructions for BowersWorld.com
# From Misk Hosting to GitHub Pages

## 🎯 Migration Overview

**Goal:** Point BowersWorld.com domain to GitHub Pages while keeping email with Misk

**Timeline:** 2-3 days for complete DNS propagation

## 📋 Step-by-Step DNS Changes at Misk

### Step 1: Login to Misk Control Panel
1. Go to your Misk hosting control panel
2. Navigate to DNS Management / Domain Settings
3. Locate BowersWorld.com domain settings

### Step 2: Keep Email Records (IMPORTANT!)
**DO NOT CHANGE THESE - Keep for email:**
```
Record Type: MX
Name: @
Value: mail.misk.com (or whatever your current mail server is)
Priority: 10

Record Type: MX  
Name: mail
Value: mail.misk.com
Priority: 10
```

### Step 3: Change Website Records
**CHANGE THESE for GitHub Pages:**

#### Remove Old A Records:
Delete any existing A records pointing to Misk servers (usually look like 192.168.x.x or similar)

#### Add New A Records:
```
Record Type: A
Name: @
Value: 185.199.108.153

Record Type: A
Name: @  
Value: 185.199.109.153

Record Type: A
Name: @
Value: 185.199.110.153

Record Type: A
Name: @
Value: 185.199.111.153
```

#### Add CNAME Record:
```
Record Type: CNAME
Name: www
Value: callmechewy.github.io
```

### Step 4: Verification Commands

After making DNS changes, verify with these commands:

```bash
# Check A records
dig bowersworld.com A

# Check CNAME 
dig www.bowersworld.com CNAME

# Check MX records (should still point to Misk)
dig bowersworld.com MX

# Check from different locations
nslookup bowersworld.com 8.8.8.8
nslookup bowersworld.com 1.1.1.1
```

**Expected Results:**
- bowersworld.com should resolve to GitHub IPs (185.199.108.153, etc.)
- www.bowersworld.com should point to callmechewy.github.io
- MX records should still point to your Misk mail servers

## 🚀 GitHub Repository Setup

### Step 1: Create BowersWorld-com Repository
1. Go to GitHub.com
2. Create new repository named: `BowersWorld-com`
3. Make it public
4. Initialize with README

### Step 2: Upload Website Files
1. Upload all files from bowersworld-template/ folder
2. Ensure CNAME file contains: `bowersworld.com`
3. Commit all changes

### Step 3: Enable GitHub Pages
1. Go to repository Settings
2. Scroll to Pages section
3. Source: Deploy from a branch
4. Branch: main
5. Folder: / (root)
6. Custom domain: bowersworld.com
7. Save

### Step 4: Verify SSL Certificate
GitHub will automatically provision SSL certificate for bowersworld.com
- May take 15-30 minutes after DNS propagation
- Check that https://bowersworld.com works with green lock

## 📊 Testing Checklist

### Pre-Migration Testing:
- [ ] Test site on temporary URL: callmechewy.github.io/BowersWorld-com
- [ ] Verify all links work
- [ ] Test AndyLibrary download integration
- [ ] Check mobile responsiveness

### Post-Migration Testing:
- [ ] bowersworld.com loads correctly
- [ ] www.bowersworld.com redirects properly  
- [ ] https://bowersworld.com has valid SSL
- [ ] Email still works (send test email)
- [ ] Download links update automatically
- [ ] All pages load correctly

## ⚠️ Troubleshooting

### Common Issues:

**"Domain already taken" error in GitHub:**
- Wait for DNS propagation (up to 48 hours)
- Verify DNS records are correct
- Try removing and re-adding custom domain

**Email stops working:**
- Check that MX records still point to Misk
- Verify email settings haven't changed
- Contact Misk support if needed

**SSL certificate issues:**
- Wait 24 hours for automatic provisioning
- Verify CNAME file is correct
- Check DNS propagation is complete

**Site not loading:**
- Check DNS with dig/nslookup commands
- Verify GitHub Pages is enabled
- Check repository is public

## 🎯 Benefits After Migration

### Technical Benefits:
- ✅ Zero hosting costs (GitHub Pages is free)
- ✅ Automatic SSL certificates
- ✅ Global CDN (faster loading worldwide)
- ✅ Version control for website changes
- ✅ Automated deployments

### Educational Mission Benefits:
- ✅ Integrated with AndyLibrary development
- ✅ Automatic download link updates
- ✅ Transparent development process
- ✅ Community contributions possible
- ✅ Global accessibility infrastructure

### Cost Savings:
- ✅ Eliminate web hosting fees
- ✅ Keep email with Misk (minimal cost)  
- ✅ Free SSL certificates
- ✅ No bandwidth charges

## 📞 Support

If you encounter issues:

1. **DNS Issues:** Contact Misk support for DNS configuration help
2. **GitHub Issues:** Check GitHub Pages documentation or GitHub support
3. **Email Issues:** Verify MX records with Misk support
4. **SSL Issues:** Usually resolve automatically within 24 hours

## 🎉 Success Criteria

Migration is complete when:
- ✅ bowersworld.com loads from GitHub Pages
- ✅ https works with valid certificate
- ✅ Email continues working normally
- ✅ AndyLibrary downloads update automatically
- ✅ All existing links continue working