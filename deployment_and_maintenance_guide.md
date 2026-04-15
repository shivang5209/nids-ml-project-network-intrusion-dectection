# Deployment and Maintenance Guide for NIDS

## Objective

Define the steps required to deploy, run, and maintain the NIDS project.

## Deployment Requirements

- Python environment
- Frontend runtime or static hosting
- Database server
- Saved ML model file
- Environment variables

## Deployment Steps

### 1. Environment Setup

- Install Python dependencies
- Install frontend dependencies
- Configure `.env` values

### 2. Database Setup

- Create database
- Run migrations
- Create admin user if needed

### 3. ML Setup

- Place serialized model in configured path
- Verify scaler/encoder files if required

### 4. Backend Startup

- Start backend server
- Verify health endpoint

### 5. Frontend Startup

- Start frontend application
- Confirm API base URL configuration

## Maintenance Tasks

- Review system logs
- Back up database
- Rotate secrets if exposed
- Retrain model when needed
- Update dependencies
- Review unresolved alerts

## Recovery Notes

- Restore database from backup
- Re-deploy model artifact if corrupted
- Restart backend and frontend services
- Re-run health verification

## Deliverables

- Deployment checklist
- Maintenance checklist
- Recovery reference

