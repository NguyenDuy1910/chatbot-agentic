# Amazon Athena Table Preview - Fix Guide

## 🐛 Problem
When previewing table data from Amazon Athena, you get an error:
```
Query FAILED: [ErrorCode: INTERNAL_ERROR_QUERY_ENGINE] Amazon Athena experienced an internal error while executing this query.
```

## 🔍 Root Causes

### 1. **Incorrect SQL Syntax for Identifiers**
- **Issue**: Using double quotes `"` for table/schema names
- **Why**: Athena uses backticks `` ` `` for identifier escaping, not double quotes
- **Impact**: Causes internal query engine errors

### 2. **Missing Database Context**
- **Issue**: Query doesn't specify the database properly
- **Why**: Athena requires explicit database context in some cases
- **Impact**: Query execution fails

### 3. **Reserved Keywords**
- **Issue**: Table or schema names might be reserved SQL keywords
- **Why**: Without proper escaping, Athena treats them as keywords
- **Impact**: Syntax errors

## ✅ Fixes Applied

### Fix 1: Updated Query Syntax in `athenaClient.ts`
**File**: `finx-ui/src/lib/athenaClient.ts` (Line 417)

**Before**:
```typescript
const query = `SELECT * FROM "${databaseName}"."${tableName}" LIMIT ${limit}`;
```

**After**:
```typescript
const query = `SELECT * FROM \`${databaseName}\`.\`${tableName}\` LIMIT ${limit}`;
```

**Why**: Backticks are the correct identifier delimiter for Athena

### Fix 2: Updated Query Syntax in `schemaAPI.ts`
**File**: `finx-ui/src/lib/schemaAPI.ts` (Line 156)

**Before**:
```typescript
query: `SELECT * FROM "${schemaName}"."${tableName}" LIMIT ${limit}`,
```

**After**:
```typescript
query: `SELECT * FROM \`${schemaName}\`.\`${tableName}\` LIMIT ${limit}`,
```

**Why**: Consistency across all query execution paths

### Fix 3: Added Enhanced Logging
**File**: `finx-ui/src/lib/athenaClient.ts` (Lines 383-413)

Added console logging to track:
- Query being executed
- Query execution ID
- Query status changes
- Execution time
- Error details

**Benefits**:
- Easier debugging
- Better error tracking
- Performance monitoring

## 🧪 Testing the Fix

### Step 1: Open Browser Console
1. Open your application in browser
2. Press `F12` to open Developer Tools
3. Go to **Console** tab

### Step 2: Navigate to Athena Connection
1. Go to **Connections** page
2. Create or select an Athena connection
3. Click **Preview** (eye icon) on any table

### Step 3: Monitor Console Output
You should see logs like:
```
[Athena] Executing query: SELECT * FROM `database`.`table` LIMIT 10
[Athena] Query execution ID: 12345678-1234-1234-1234-123456789012
[Athena] Query status: QUEUED
[Athena] Query status: RUNNING
[Athena] Query status: SUCCEEDED
[Athena] Query succeeded in 1234ms
```

### Step 4: Verify Data Display
- Modal should show table data
- Columns should be displayed correctly
- Rows should be populated

## 🚨 Troubleshooting

### Issue: Still Getting Internal Error
**Solution**:
1. Check browser console for detailed error message
2. Verify table name doesn't contain special characters
3. Ensure database name is correct
4. Check AWS Athena permissions

### Issue: Query Timeout
**Solution**:
1. Check if table is very large
2. Verify S3 output location is accessible
3. Check AWS Athena workgroup settings
4. Increase timeout in `executeQueryAndWait` (default: 30s)

### Issue: No Data Returned
**Solution**:
1. Verify table actually contains data
2. Check if table is empty
3. Verify SELECT permissions on table
4. Check if table is external or internal

## 📝 SQL Syntax Reference for Athena

### Correct Identifier Escaping
```sql
-- ✅ CORRECT - Use backticks
SELECT * FROM `database`.`table`
SELECT * FROM `my-database`.`my-table`

-- ❌ WRONG - Don't use double quotes
SELECT * FROM "database"."table"

-- ❌ WRONG - Don't use square brackets
SELECT * FROM [database].[table]
```

### Reserved Keywords
If your table/schema name is a reserved keyword, use backticks:
```sql
-- ✅ CORRECT
SELECT * FROM `select`.`from`

-- ❌ WRONG
SELECT * FROM select.from
```

## 🔧 Configuration Checklist

- [ ] Athena connection has correct region
- [ ] S3 output location is accessible
- [ ] Workgroup is configured correctly
- [ ] AWS credentials have Athena permissions
- [ ] Database exists in Athena
- [ ] Table exists in database
- [ ] Table contains data

## 📊 Performance Tips

1. **Use LIMIT clause**: Always limit results for preview
2. **Specify columns**: Instead of `SELECT *`, specify needed columns
3. **Add WHERE clause**: Filter data when possible
4. **Use LIMIT 10-100**: Don't preview large datasets

## 🔗 Related Files

- `finx-ui/src/lib/athenaClient.ts` - Athena client implementation
- `finx-ui/src/lib/schemaAPI.ts` - Schema API with preview functionality
- `finx-ui/src/components/features/data-connections/schema/AthenaSchemaExplorer.tsx` - UI component

## 📚 AWS Athena Documentation

- [Athena SQL Reference](https://docs.aws.amazon.com/athena/latest/ug/querying-supported-statements.html)
- [Athena Best Practices](https://docs.aws.amazon.com/athena/latest/ug/best-practices.html)
- [Athena Quotas and Limits](https://docs.aws.amazon.com/athena/latest/ug/service-limits.html)

---

**Last Updated**: 2025-10-18
**Status**: ✅ Fixed

