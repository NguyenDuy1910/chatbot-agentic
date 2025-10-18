# Testing Script - Connection Type Modal

## 🧪 Manual Testing Steps

### Test 1: Open Modal
1. Navigate to Connection Dashboard
2. Click "New Connection" button (top right)
3. **Expected**: Modal popup hiển thị với 3 database options
4. **Verify**: 
   - Modal có backdrop blur
   - Title "Choose Connection Type"
   - 3 cards: PostgreSQL, Athena, DuckDB
   - Search bar visible

### Test 2: Search Functionality
1. In modal, type "post" in search box
2. **Expected**: Only PostgreSQL card shows
3. Clear search, type "athena"
4. **Expected**: Only Athena card shows
5. Type "xyz"
6. **Expected**: "No connection types found" message

### Test 3: Select PostgreSQL
1. Click on PostgreSQL card
2. **Expected**: 
   - Modal closes
   - PostgreSQL connection form displays
   - Back button present
   - Form fields: host, port, database, username, password
3. Click back button
4. **Expected**: Return to dashboard

### Test 4: Select Athena
1. Click "New Connection"
2. Click on Athena card
3. **Expected**:
   - Modal closes
   - Athena connection form displays
   - Form fields: region, workgroup, output location, etc.
4. Click back button
5. **Expected**: Return to dashboard

### Test 5: Select DuckDB
1. Click "New Connection"
2. Click on DuckDB card
3. **Expected**:
   - Modal closes
   - DuckDB connection form displays
4. Click back button
5. **Expected**: Return to dashboard

### Test 6: Cancel Modal
1. Click "New Connection"
2. Click "Cancel" button at bottom
3. **Expected**: Modal closes, stay on dashboard
4. Click "New Connection"
5. Press ESC key
6. **Expected**: Modal closes

### Test 7: Responsive Design
**Desktop (1920x1080)**:
- Modal should show 3 cards in a row
- Cards should have good spacing
- Icons and text readable

**Tablet (768x1024)**:
- Modal should show 3 cards still
- Slightly narrower cards
- All content visible

**Mobile (375x667)**:
- Cards should stack vertically (1 column)
- Modal should be full width with margins
- Scrollable if needed

### Test 8: Hover Effects
1. Open modal
2. Hover over PostgreSQL card
3. **Expected**:
   - Card scales up (1.03x)
   - Shadow increases
   - Border color appears (blue)
   - Icon scales up (1.1x)
4. Repeat for other cards

### Test 9: Complete Flow - PostgreSQL
1. Click "New Connection"
2. Select PostgreSQL
3. Fill in form:
   ```
   Name: Test PostgreSQL
   Host: localhost
   Port: 5432
   Database: testdb
   Username: postgres
   Password: password123
   ```
4. Click "Test Connection"
5. **Expected**: Success message or error
6. If success, click "Continue"
7. **Expected**: Schema explorer shows

### Test 10: Complete Flow - Athena
1. Click "New Connection"
2. Select Athena
3. Fill in form:
   ```
   Name: Test Athena
   Region: us-east-1
   Workgroup: primary
   Output Location: s3://my-bucket/output/
   ```
4. Click "Test Connection"
5. **Expected**: Connection validates
6. Click "Continue"
7. **Expected**: Catalog selector shows
8. Select catalog (e.g., AwsDataCatalog)
9. **Expected**: Schema explorer shows databases

## 🎯 Expected Behavior Summary

| Action | Before | After |
|--------|--------|-------|
| Click "New Connection" | Navigate to new page | Modal pops up |
| Select database | Click card on page | Click card in modal |
| Modal closes | N/A | Auto closes after selection |
| Navigation | Page transition | Seamless in-place update |
| Back button | Go to previous page | Return to dashboard |

## ✅ Success Criteria

- [ ] Modal opens instantly on button click
- [ ] All 3 database options visible and clickable
- [ ] Search filters correctly
- [ ] Clicking option closes modal and shows form
- [ ] Back button returns to dashboard
- [ ] No console errors
- [ ] Smooth animations
- [ ] Responsive on all screen sizes
- [ ] Keyboard accessible (Tab, Enter, Esc)
- [ ] Visual feedback on hover

## 🐛 Known Issues / Edge Cases

1. **Empty Search**: If search returns no results, show helpful message ✅
2. **ESC Key**: Should close modal ✅ (handled by HeroUI)
3. **Click Outside**: Should close modal ✅ (handled by HeroUI)
4. **Multiple Clicks**: Prevent rapid clicking that opens multiple modals ✅
5. **Form Validation**: Each form has its own validation

## 📸 Screenshots to Capture

1. Dashboard with "New Connection" button
2. Modal popup with 3 database cards
3. Search functionality filtering results
4. PostgreSQL form after selection
5. Athena form after selection
6. DuckDB form after selection
7. Hover state on card
8. Mobile view of modal

## 🔄 Regression Testing

After implementing this feature, verify these still work:

- [ ] Reusing saved connections from session
- [ ] Editing existing connections
- [ ] Deleting connections
- [ ] Connection stats display correctly
- [ ] Tabs (Connections, Templates, Analytics) still work
- [ ] Saved connections list still functions
- [ ] "Explore Schema" button still works

## 📊 Performance Metrics

Monitor these:
- Modal open time: < 100ms
- Modal close time: < 100ms
- Search response time: instant (< 50ms)
- Card hover response: instant
- Page doesn't freeze during operations

## 🎨 Visual Consistency

Check these match design system:
- [ ] Colors match brand palette
- [ ] Fonts consistent with app
- [ ] Spacing follows 4px/8px grid
- [ ] Icons from lucide-react
- [ ] Gradients match existing patterns
- [ ] Shadows match design tokens
