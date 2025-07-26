# BowersWorld.com Migration Guide
# From Misk Hosting to GitHub Pages

## Phase 1: GitHub Repository Setup

### Repository Structure for BowersWorld-com:
```
BowersWorld-com/
├── index.html              # Main homepage
├── about.html              # About the educational mission
├── download.html           # AndyLibrary download page
├── contact.html            # Contact information
├── CNAME                   # Custom domain configuration
├── _config.yml             # Jekyll configuration (optional)
├── assets/
│   ├── css/
│   │   └── style.css       # Custom styling
│   ├── js/
│   │   └── app.js          # Dynamic content loading
│   └── images/
│       ├── logo.png        # BowersWorld logo
│       └── andylibrary/    # AndyLibrary screenshots
├── data/
│   └── andylibrary.json    # Auto-updated from AndyLibrary repo
└── .github/
    └── workflows/
        ├── deploy.yml      # Auto-deploy to Pages
        └── update.yml      # Receive updates from AndyLibrary
```

## Phase 2: DNS Configuration at Misk

### Current DNS Records (keep):
```
MX Records (Email - Keep These!)
mail.bowersworld.com    IN  MX  10  mail.misk.com
@                       IN  MX  10  mail.misk.com
```

### New DNS Records (change these):
```
A Records (Website - Change These!)
@                       IN  A   185.199.108.153
@                       IN  A   185.199.109.153  
@                       IN  A   185.199.110.153
@                       IN  A   185.199.111.153

CNAME Records
www                     IN  CNAME  callmechewy.github.io
```

## Phase 3: GitHub Pages Configuration

### CNAME File Content:
```
bowersworld.com
```

### _config.yml Content:
```yaml
title: "BowersWorld - Educational Mission"
description: "Getting education into the hands of people who can least afford it!"
url: "https://bowersworld.com"
baseurl: ""

# Jekyll settings
markdown: kramdown
highlighter: rouge
theme: minima

# Educational mission settings
mission:
  primary: "Getting education into the hands of people who can least afford it!"
  focus_areas:
    - "Cost protection for students"
    - "Offline-first educational access" 
    - "Budget device optimization"
    - "Global educational equity"

# AndyLibrary integration
andylibrary:
  repository: "CallMeChewy/AndyLibrary"
  download_base: "https://github.com/CallMeChewy/AndyLibrary/releases/latest"
  
# Social links
social:
  github: "CallMeChewy"
  email: "contact@bowersworld.com"
```

## Phase 4: Migration Timeline

### Week 1: Preparation
- [ ] Create BowersWorld-com repository
- [ ] Build GitHub Pages site
- [ ] Test on temporary URL (callmechewy.github.io/BowersWorld-com)
- [ ] Set up automation workflows

### Week 2: Testing
- [ ] Add CNAME file to repository
- [ ] Enable GitHub Pages with custom domain
- [ ] Test DNS propagation with dig/nslookup
- [ ] Verify email still works with Misk

### Week 3: Migration
- [ ] Update DNS at Misk to point to GitHub
- [ ] Monitor propagation (24-48 hours)
- [ ] Test all functionality
- [ ] Update any external links

### Week 4: Optimization
- [ ] Set up SSL certificate (automatic with GitHub Pages)
- [ ] Configure CDN if needed
- [ ] Optimize for educational mission
- [ ] Set up analytics/monitoring

## Phase 5: Educational Mission Integration

### Automated Content Updates:
```javascript
// Auto-update AndyLibrary information
fetch('https://api.github.com/repos/CallMeChewy/AndyLibrary/releases/latest')
  .then(response => response.json())
  .then(release => {
    updateDownloadSection(release);
    updateMissionProgress(release);
  });
```

### Mission-Focused Design:
- Highlight educational impact
- Student testimonials section
- Global reach statistics
- Cost transparency information
- Offline capability emphasis

## Benefits of Migration

### Cost Savings:
- ✅ Zero hosting costs with GitHub Pages
- ✅ Free SSL certificates
- ✅ Global CDN included
- ✅ Keep email with Misk (minimal cost)

### Technical Advantages:
- ✅ Version control for website changes
- ✅ Automated deployments
- ✅ Integration with AndyLibrary development
- ✅ Professional development workflow

### Educational Mission Benefits:
- ✅ Transparent development process
- ✅ Community contributions possible
- ✅ Global accessibility
- ✅ Reliable uptime (GitHub's infrastructure)