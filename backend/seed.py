"""
Seed script — 50 projects, 150+ tasks, 60+ comments.
Run from the backend/ directory:
    python seed.py
"""
import asyncio, sys, os, random
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import engine
from app.db.database import Base
from app.models.models import (
    User, Project, Task, Comment,
    UserRole, TaskStatus, TaskPriority, generate_uuid,
)
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import text

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
today = date.today()
rng = random.Random(42)   # deterministic seed

# ─── catalogue data ─────────────────────────────────────────────────────────

PROJECTS = [
    ("Website Redesign",             "Redesign the company marketing site with modern UI/UX"),
    ("Mobile App v2",                "New features for iOS and Android apps"),
    ("API Gateway Migration",        "Move legacy REST API to FastAPI microservices"),
    ("Data Analytics Dashboard",     "Real-time dashboard for KPIs and sales metrics"),
    ("DevOps Automation",            "CI/CD pipeline, Docker, and Kubernetes configs"),
    ("E-Commerce Platform",          "Build a full-featured online store with cart and checkout"),
    ("CRM Integration",              "Integrate Salesforce and HubSpot into the internal portal"),
    ("HR Management System",         "Leave, payroll and performance management modules"),
    ("Inventory Management",         "Track stock levels, suppliers, and purchase orders"),
    ("Customer Support Portal",      "Ticket system with SLA tracking and knowledge base"),
    ("Payment Gateway",              "Stripe and PayPal checkout with refund workflows"),
    ("Email Marketing Platform",     "Campaign builder, A/B testing, and analytics"),
    ("Video Streaming Service",      "HLS-based player with adaptive bitrate"),
    ("Machine Learning Pipeline",    "Data ingestion, training jobs, and model registry"),
    ("Security Audit",               "Pen-testing and vulnerability remediation"),
    ("Search Engine Optimisation",   "Technical SEO audit and structured data markup"),
    ("Real-time Chat App",           "WebSocket-powered messaging with presence indicators"),
    ("Notification Service",         "Multi-channel alerts: email, SMS, push, Slack"),
    ("Reporting Module",             "Scheduled PDF/Excel reports with dynamic filters"),
    ("Authentication Overhaul",      "OAuth2, MFA, and passkey support"),
    ("Content Management System",    "Headless CMS with multilingual support"),
    ("Supply Chain Tracker",         "End-to-end shipment visibility with map view"),
    ("Booking & Scheduling",         "Calendar widget with resource conflict detection"),
    ("Document Management",          "Version-controlled file storage with preview"),
    ("IoT Device Management",        "Fleet dashboard for 10k+ connected sensors"),
    ("Microservices Refactor",       "Break monolith into 12 independent services"),
    ("Data Warehouse Migration",     "Move on-prem DWH to Snowflake"),
    ("Accessibility Compliance",     "WCAG 2.1 AA audit and remediation"),
    ("Dark Mode Support",            "Theme switcher respecting system preference"),
    ("Internationalisation",         "i18n for 12 locales including RTL languages"),
    ("GraphQL API Layer",            "Expose REST data via a federated GraphQL gateway"),
    ("Blockchain POC",               "Smart-contract prototype on Ethereum testnet"),
    ("AI Chatbot",                   "LLM-powered support bot with retrieval-augmented generation"),
    ("Rate Limiting Service",        "Token-bucket and sliding-window rate limiters"),
    ("Audit Logging",                "Immutable event log with export to SIEM"),
    ("Feature Flag System",          "Progressive rollout and A/B experiment management"),
    ("Disaster Recovery Plan",       "RTO/RPO review, runbook creation, and DR drills"),
    ("Performance Optimisation",     "Frontend Core Web Vitals + backend query tuning"),
    ("Automated Testing Suite",      "E2E Playwright tests covering 200+ user journeys"),
    ("Service Level Agreements",     "SLA dashboard with breach alerts and monthly reports"),
    ("Cloud Cost Optimisation",      "RightSize EC2, Reserved Instances, savings plans"),
    ("Internal Wiki",                "Confluence-style knowledge base with search"),
    ("Ad Campaign Manager",          "Budget pacing, creative management, reporting"),
    ("Affiliate Program",            "Referral tracking with commission calculations"),
    ("Loyalty Rewards System",       "Points engine, tier badges, redemption flows"),
    ("Vendor Onboarding Portal",     "KYC checks, contract e-sign, and approval workflows"),
    ("Fleet Management",             "GPS tracking, maintenance schedules, driver logs"),
    ("Legal Contract Lifecycle",     "Template library, redline workflow, deadline alerts"),
    ("Student Learning Platform",    "Course builder with quizzes and progress tracking"),
    ("Health & Wellness App",        "Workout logging, nutrition diary, goal setting"),
]

TASK_TEMPLATES = [
    ("Requirements gathering",        "Collect and document stakeholder requirements",               TaskPriority.high),
    ("System design document",        "Architecture diagrams, sequence diagrams, ERD",               TaskPriority.high),
    ("Database schema design",        "Design normalised schema and write migration scripts",        TaskPriority.high),
    ("Backend API development",       "Implement CRUD endpoints with validation",                    TaskPriority.high),
    ("Frontend UI components",        "Build reusable React components from Figma designs",         TaskPriority.medium),
    ("Unit test coverage",            "Achieve >=80% unit test coverage with pytest/jest",          TaskPriority.medium),
    ("Integration testing",           "End-to-end tests for critical user flows",                   TaskPriority.medium),
    ("Code review",                   "Peer review all PRs and address feedback",                   TaskPriority.medium),
    ("CI/CD pipeline setup",          "GitHub Actions: lint, test, build, deploy stages",           TaskPriority.medium),
    ("Security review",               "OWASP Top 10 checklist and dependency audit",                TaskPriority.high),
    ("Performance profiling",         "Identify and fix N+1 queries and slow endpoints",            TaskPriority.medium),
    ("Documentation",                 "Update README, API docs, and runbook",                       TaskPriority.low),
    ("Staging deployment",            "Deploy to staging with production-like config",              TaskPriority.medium),
    ("UAT sign-off",                  "Coordinate user acceptance testing with stakeholders",       TaskPriority.high),
    ("Production release",            "Blue-green deploy, smoke test, rollback plan",              TaskPriority.high),
    ("Post-launch monitoring",        "Set up Grafana alerts for error rate and latency",           TaskPriority.medium),
    ("Accessibility audit",           "Run axe-core and fix critical/serious violations",           TaskPriority.low),
    ("Localisation strings",          "Extract hard-coded strings and add i18n keys",               TaskPriority.low),
    ("Mobile responsiveness",         "Test and fix layouts on 320px to 1440px viewports",          TaskPriority.medium),
    ("Error handling & logging",      "Structured logs, Sentry integration, friendly error pages",  TaskPriority.medium),
    ("Rate limiting implementation",  "Apply per-user and per-IP throttling middleware",            TaskPriority.medium),
    ("Data migration script",         "One-time migration of legacy records with rollback",         TaskPriority.high),
    ("Caching layer",                 "Redis cache for hot queries and session storage",            TaskPriority.medium),
    ("Feature flag integration",      "Wrap new features behind LaunchDarkly flags",               TaskPriority.low),
    ("Retrospective & lessons learned","Team retro, action items, and knowledge-base update",      TaskPriority.low),
]

STATUSES       = [TaskStatus.todo, TaskStatus.in_progress, TaskStatus.done]
STATUS_WEIGHTS = [0.40, 0.35, 0.25]

COMMENTS = [
    "Looks good — merging after CI is green.",
    "Blocked on infra access. Raised ticket with DevOps.",
    "Draft PR is up: #142. Please review by EOD.",
    "Completed ahead of schedule. Updating Jira.",
    "Need clarification from product before proceeding.",
    "Dependency on the auth service is still pending.",
    "Test coverage at 87%. Closing this one.",
    "Flagging for tech-debt: refactor in Q3.",
    "Design approved by UX. Starting implementation.",
    "Performance numbers look healthy in staging.",
    "Found an edge case — adding regression test.",
    "Stakeholder demo scheduled for Friday 2 PM.",
    "Rollback plan documented in the runbook.",
    "Merging to main after security sign-off.",
    "Monitoring alerts configured. Handing over to ops.",
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # ── wipe existing data ────────────────────────────────────────────
        for tbl in ("comments", "tasks", "projects", "users"):
            await session.execute(text(f"DELETE FROM {tbl}"))
        await session.commit()

        # ── users ─────────────────────────────────────────────────────────
        admin = User(id=generate_uuid(), name="Alice Admin",    email="admin@demo.com",  password_hash=get_password_hash("Admin@123"), role=UserRole.admin)
        bob   = User(id=generate_uuid(), name="Bob Developer",  email="bob@demo.com",    password_hash=get_password_hash("User@123"),  role=UserRole.user)
        carol = User(id=generate_uuid(), name="Carol Designer", email="carol@demo.com",  password_hash=get_password_hash("User@123"),  role=UserRole.user)
        dave  = User(id=generate_uuid(), name="Dave QA",        email="dave@demo.com",   password_hash=get_password_hash("User@123"),  role=UserRole.user)
        eve   = User(id=generate_uuid(), name="Eve DevOps",     email="eve@demo.com",    password_hash=get_password_hash("User@123"),  role=UserRole.user)
        all_users = [admin, bob, carol, dave, eve]
        non_admin = [bob, carol, dave, eve]
        session.add_all(all_users)
        await session.flush()

        # ── projects (50) ─────────────────────────────────────────────────
        project_rows = []
        for i, (name, desc) in enumerate(PROJECTS):
            owner = admin if i % 5 == 0 else rng.choice(non_admin)
            p = Project(id=generate_uuid(), name=name, description=desc, created_by=owner.id)
            project_rows.append((p, owner))
            session.add(p)
        await session.flush()

        # ── tasks (3–5 per project, guaranteed >= 25 per project group) ───
        all_tasks = []
        for proj, owner in project_rows:
            n_tasks = rng.randint(3, 5)
            chosen_templates = rng.sample(TASK_TEMPLATES, n_tasks)
            for title, desc, priority in chosen_templates:
                status   = rng.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
                due_off  = rng.randint(-14, 60)
                assignee = rng.choice(non_admin)
                t = Task(
                    id=generate_uuid(),
                    title=title,
                    description=desc,
                    status=status,
                    priority=priority,
                    due_date=today + timedelta(days=due_off),
                    project_id=proj.id,
                    created_by=owner.id,
                    assigned_to=assignee.id,
                )
                all_tasks.append(t)
                session.add(t)
        await session.flush()

        # ── comments (1–3 on ~40% of tasks) ──────────────────────────────
        all_comments = []
        for t in all_tasks:
            if rng.random() > 0.40:
                continue
            for _ in range(rng.randint(1, 3)):
                c = Comment(
                    id=generate_uuid(),
                    content=rng.choice(COMMENTS),
                    task_id=t.id,
                    created_by=rng.choice(all_users).id,
                )
                all_comments.append(c)
                session.add(c)

        await session.commit()

    print("Seed complete!")
    print(f"  Users    : {len(all_users)}  (admin@demo.com/Admin@123 | bob|carol|dave|eve@demo.com/User@123)")
    print(f"  Projects : {len(project_rows)}")
    print(f"  Tasks    : {len(all_tasks)}")
    print(f"  Comments : {len(all_comments)}")


if __name__ == "__main__":
    asyncio.run(seed())

