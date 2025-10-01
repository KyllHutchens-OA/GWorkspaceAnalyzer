# GWorkspace Analyzer - Development Tasks (Updated)

## Current Status: MVP Foundation Complete

### Backend: ~85% Complete
- Database schema deployed and verified
- Google OAuth + Gmail integration working
- Invoice parsing (PDF + HTML) functional
- Duplicate detection algorithms implemented
- Background scan job processing implemented
- REST API endpoints complete

### Frontend: ~70% Complete
- UI components built (12 components)
- Dashboard layout complete with mock data
- Login page designed
- Auth callback flow stubbed
- Types and interfaces defined

---

## Priority Tasks to Complete MVP

### HIGH PRIORITY - Critical for Launch

#### 1. Frontend API Integration (5 tasks)
- [ ] Create API client service (`/frontend/src/lib/api.ts`)
- [ ] Implement authentication state management (Context/hooks)
- [ ] Wire login page to backend OAuth flow (`/api/v1/auth/google/login`)
- [ ] Connect dashboard to real API endpoints (scan jobs, invoices, findings)
- [ ] Implement error handling and loading states

#### 2. OAuth Flow Completion (2 tasks)
- [ ] Make login button functional (redirect to backend OAuth endpoint)
- [ ] Handle OAuth callback and token storage (cookies/localStorage)

#### 3. Scan Job UI (3 tasks)
- [ ] Create "Start New Scan" button/modal
- [ ] Implement scan job progress polling/websocket
- [ ] Show real-time scan status (queued → processing → completed)

#### 4. Analysis Algorithms - Missing Features (3 tasks)
- [ ] Implement subscription tracking logic (recurring vendor detection)
- [ ] Build price monitoring system (month-over-month comparison)
- [ ] Create total waste calculation aggregator

---

## MEDIUM PRIORITY - Enhanced User Experience

### User Actions & Interactivity (4 tasks)
- [ ] Implement "Mark as Resolved" functionality (frontend + backend hook-up)
- [ ] Add "Dismiss" issue action
- [ ] Implement "Add Notes" to findings
- [ ] Build filtering/sorting on findings table

### Settings & Preferences (3 tasks)
- [ ] Create settings page UI
- [ ] Implement alert threshold configuration
- [ ] Add vendor exclusion list management

### Email Notifications (3 tasks)
- [ ] Set up email service (SendGrid/AWS SES/Resend)
- [ ] Implement weekly digest email template
- [ ] Create email job scheduler (cron/background task)

### Onboarding Flow (2 tasks)
- [ ] Build initial scan loading screen with progress
- [ ] Create "first results" reveal animation/flow

---

## LOW PRIORITY - Nice to Have

### Performance & Optimization (3 tasks)
- [ ] Implement Gmail API rate limiting (exponential backoff)
- [ ] Add caching for invoice data
- [ ] Optimize database queries (indexes verified, but could add more)

### Payment & Monetization (4 tasks)
- [ ] Set up Stripe integration
- [ ] Build subscription management endpoints
- [ ] Implement free trial countdown logic (7 days)
- [ ] Create upgrade flow and paywall

### Advanced Features - Phase 2 (2 tasks)
- [ ] Set up Google Cloud Vision API for OCR
- [ ] Implement image invoice processing

### Distribution (1 task)
- [ ] Create Google Workspace Marketplace listing

---

## BUGS & FIXES

### Known Issues
- [ ] Fix auth callback error handling (currently just shows error page)
- [ ] Ensure mobile responsiveness on all dashboard components
- [ ] Add proper TypeScript types for API responses
- [ ] Handle expired OAuth tokens (refresh token flow)

---

## Testing & Documentation

### Testing (4 tasks)
- [ ] Write API integration tests
- [ ] Add frontend component tests (React Testing Library)
- [ ] End-to-end testing for OAuth flow
- [ ] Load testing for scan job processing

### Documentation (2 tasks)
- [ ] Create user documentation (how to use the app)
- [ ] Write developer setup guide (README improvements)

---

## Progress Summary

### Phase 1: Core MVP (85% Complete)
**Completed:**
- ✅ Database schema (9 tables, RLS, indexes)
- ✅ Gmail API integration (search, fetch, attachments)
- ✅ Invoice parsing (PDF + HTML)
- ✅ Duplicate detection (exact + probable)
- ✅ Backend API endpoints (auth, scan, invoices, findings)
- ✅ Background scan job processor
- ✅ Frontend UI components (dashboard, login, cards)
- ✅ Mock data implementation

**In Progress:**
- 🔄 Frontend-backend integration (API client needed)
- 🔄 OAuth flow completion (wiring needed)
- 🔄 Real-time scan job status

**Blocked/Pending:**
- ❌ Subscription tracking algorithm
- ❌ Price monitoring algorithm
- ❌ Waste calculation engine
- ❌ Email notifications

### Phase 2: Engagement & Retention (10% Complete)
- Email digest system
- User action tracking
- Settings management
- Onboarding optimization

### Phase 3: Monetization (0% Complete)
- Stripe integration
- Free trial management
- Upgrade flows

---

## Immediate Next Steps (This Sprint)

1. **Build API Client** (`frontend/src/lib/api.ts`)
   - Create fetchAPI wrapper with auth headers
   - Define type-safe API methods (getScanJobs, getInvoices, etc.)

2. **Wire Up Authentication**
   - Implement auth context provider
   - Connect login button to backend OAuth
   - Handle callback and store tokens

3. **Connect Dashboard to Real Data**
   - Replace mockData with API calls
   - Add loading states
   - Implement error boundaries

4. **Implement Scan Job Flow**
   - "Start Scan" button triggers POST /api/v1/scan/start
   - Poll GET /api/v1/scan/jobs/{id} for status
   - Update UI when scan completes

5. **Complete Missing Analysis Algorithms**
   - Subscription tracking (detect recurring charges)
   - Price monitoring (compare historical invoices)
   - Waste calculation (aggregate findings)

---

## Definition of Done (MVP Launch Checklist)

- [ ] User can log in with Google OAuth
- [ ] User can trigger a Gmail scan
- [ ] Scan processes in background and shows progress
- [ ] Dashboard displays real findings from database
- [ ] User can see duplicate charges detected
- [ ] User can mark issues as resolved
- [ ] Basic error handling and loading states
- [ ] Mobile responsive
- [ ] Privacy policy and terms pages
- [ ] Basic analytics tracking (optional)

**Estimated Time to MVP Launch:** 2-3 weeks of focused development

---

## Notes

- Frontend is surprisingly complete (UI/UX is solid)
- Backend is production-ready except for missing algorithms
- **Main blocker:** Frontend-backend integration layer
- Once API client is built, connecting everything should be fast
- Email notifications are important for retention but not MVP-critical
- Payment can be delayed until after initial user feedback
