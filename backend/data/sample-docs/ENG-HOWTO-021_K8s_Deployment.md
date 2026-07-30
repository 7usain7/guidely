# Technical How-To: Deploying Microservices to Production Kubernetes (EKS)

**Document ID:** ENG-HOWTO-021  
**Category:** DevOps & Infrastructure Engineering  
**Version:** 3.4.0  
**Target Audience:** Backend Developers, Site Reliability Engineers (SREs)

---

## 1. Deployment Overview & Requirements

This guide covers the end-to-end workflow for deploying containerized microservices into our Amazon EKS production clusters via ArgoCD and Helm.

### Prerequisites Checklist

- Installed **kubectl** (v1.28 or later) and **AWS CLI v2**.
- Authenticated with AWS SSO using `aws sso login --profile production-admin`.
- Merged pull request into the `main` branch with passing GitHub Actions CI checks (linting, unit testing, SAST security scans).

---

## 2. Step-by-Step Deployment Procedure

### Step 1: Update Helm Values & Service Version

Navigate to the GitOps configuration repository (`github.com/company-org/gitops-prod`) and locate your service directory under `/apps/services/[your-service-name]/`.

Edit `values-prod.yaml` to update the image tag and resource limits:

```yaml
image:
  repository: [123456789012.dkr.ecr.us-east-1.amazonaws.com/service-name](https://123456789012.dkr.ecr.us-east-1.amazonaws.com/service-name)
  tag: "v2.14.0" # Match latest release commit SHA
resources:
  limits:
    cpu: "1000m"
    memory: "1024Mi"
  requests:
    cpu: "250m"
    memory: "512Mi"
Step 2: Trigger GitOps Sync via ArgoCD
Once your PR is approved and merged into gitops-prod:

Open the internal ArgoCD dashboard at https://argocd.internal.company.com.

Search for your application target name (prod-[service-name]).

Click Sync -> Select Prune and Apply options.

Verify deployment strategy: Production services default to a Canary Deployment pattern (10% traffic for 15 minutes before 100% rollout).

3. Troubleshooting & Emergency Rollbacks
Emergency Rollback Instructions
If metrics (Datadog Error Rate or Latency P99) breach threshold alarms during Canary deployment:

Open ArgoCD and select your service.

Click History and Rollback.

Select the previous stable deployment revision number (e.g., Revision 142) and click Rollback.

Alternatively, execute the CLI emergency override command:

Bash
argocd app rollback prod-[service-name] [REVISION_ID] --prune
```
