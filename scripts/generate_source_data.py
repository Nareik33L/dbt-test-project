"""Generate deterministic synthetic source data for Oakwell.

Oakwell is a fictional B2B SaaS operations platform. This script writes dbt
seed CSVs that represent extracts from the production application, billing
system, usage pipeline, and support desk.

The generator is intentionally a little messy in the ways real SaaS data is
messy (unpaid invoices, missing optional fields, short-lived customers,
reactivation, proration-free mid-term seat changes), but it is fully
deterministic given the seed.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
AS_OF = date(2026, 8, 31)
PERIOD_START = date(2022, 7, 1)
N_PAYING_CUSTOMERS = 480
N_FAILED_TRIALS = 90

ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "seeds"

PLANS = [
    {
        "plan_id": 1,
        "plan_code": "starter",
        "plan_name": "Starter",
        "plan_tier": 1,
        "list_price_monthly": 29.00,
        "billing_intervals": "monthly",
        "max_seats": 10,
        "includes_sso": False,
        "includes_premium_support": False,
        "includes_api_access": False,
    },
    {
        "plan_id": 2,
        "plan_code": "team",
        "plan_name": "Team",
        "plan_tier": 2,
        "list_price_monthly": 59.00,
        "billing_intervals": "monthly,annual",
        "max_seats": 50,
        "includes_sso": False,
        "includes_premium_support": False,
        "includes_api_access": True,
    },
    {
        "plan_id": 3,
        "plan_code": "business",
        "plan_name": "Business",
        "plan_tier": 3,
        "list_price_monthly": 99.00,
        "billing_intervals": "monthly,annual",
        "max_seats": None,
        "includes_sso": True,
        "includes_premium_support": False,
        "includes_api_access": True,
    },
    {
        "plan_id": 4,
        "plan_code": "enterprise",
        "plan_name": "Enterprise",
        "plan_tier": 4,
        "list_price_monthly": 149.00,
        "billing_intervals": "annual",
        "max_seats": None,
        "includes_sso": True,
        "includes_premium_support": True,
        "includes_api_access": True,
    },
]
PLAN_BY_ID = {p["plan_id"]: p for p in PLANS}

COUNTRIES = [
    # country_code, country_name, region, subregion, weight, legal_suffixes
    ("US", "United States", "North America", "United States", 0.40, ["Inc", "LLC", "Corp"]),
    ("CA", "Canada", "North America", "Canada", 0.08, ["Inc", "Ltd"]),
    ("GB", "United Kingdom", "Europe", "United Kingdom", 0.12, ["Ltd", "LLP"]),
    ("DE", "Germany", "Europe", "DACH", 0.10, ["GmbH", "AG"]),
    ("FR", "France", "Europe", "Western Europe", 0.07, ["SAS", "SARL"]),
    ("NL", "Netherlands", "Europe", "Western Europe", 0.05, ["B.V."]),
    ("SE", "Sweden", "Europe", "Nordics", 0.05, ["AB"]),
    ("AU", "Australia", "APAC", "Australia", 0.13, ["Pty Ltd"]),
]

US_SUBREGIONS = [
    ("West", 0.28),
    ("Midwest", 0.20),
    ("Northeast", 0.24),
    ("South", 0.28),
]

INDUSTRIES = [
    ("professional_services", 0.22),
    ("logistics", 0.14),
    ("manufacturing", 0.13),
    ("healthcare", 0.12),
    ("facilities", 0.10),
    ("construction", 0.09),
    ("retail", 0.08),
    ("financial_services", 0.07),
    ("education", 0.05),
]

ADJECTIVES = [
    "North", "Bright", "Cedar", "Iron", "Silver", "Harbour", "Summit", "Atlas",
    "Pioneer", "Amber", "Copper", "River", "Forest", "Granite", "Oak", "Maple",
    "Blue", "Golden", "Pacific", "Alpine", "Urban", "Coastal", "Prairie", "Metro",
    "Apex", "Vertex", "Nimbus", "Lumen", "Forge", "Anchor", "Beacon", "Canyon",
]
NOUNS = [
    "Logistics", "Partners", "Systems", "Works", "Studios", "Collective",
    "Holdings", "Group", "Labs", "Services", "Industries", "Solutions",
    "Operations", "Workshops", "Studios", "Ventures", "Advisory", "Networks",
    "Fabrication", "Clinics", "Retail", "Properties", "Engineering", "Supply",
]

TICKET_CATEGORIES = ["how_to", "bug", "billing", "feature_request", "outage", "onboarding"]
TICKET_PRIORITIES = ["low", "medium", "high", "urgent"]


def month_start(d: date) -> date:
    return date(d.year, d.month, 1)


def add_months(d: date, months: int) -> date:
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    return date(year, month, 1)


def month_end(d: date) -> date:
    nxt = add_months(month_start(d), 1)
    return nxt - timedelta(days=1)


def months_between(start: date, end: date) -> list[date]:
    out = []
    cur = month_start(start)
    last = month_start(end)
    while cur <= last:
        out.append(cur)
        cur = add_months(cur, 1)
    return out


def daterange(start: date, end: date) -> list[date]:
    """Inclusive date range."""
    days = (end - start).days
    return [start + timedelta(days=i) for i in range(days + 1)]


def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def round_money(x: float) -> float:
    return round(float(x) + 1e-9, 2)


def weighted_choice(rng: random.Random, pairs: list[tuple]) -> object:
    items = [p[0] if not isinstance(p[0], tuple) else p for p in pairs]
    # pairs are (value, weight) or ((tuple), weight)
    values = []
    weights = []
    for p in pairs:
        if isinstance(p, tuple) and len(p) == 2 and not isinstance(p[0], tuple):
            values.append(p[0])
            weights.append(p[1])
        elif isinstance(p, tuple) and isinstance(p[0], tuple):
            values.append(p[0])
            weights.append(p[1])
        else:
            raise ValueError(p)
    return rng.choices(values, weights=weights, k=1)[0]


def choose_country(rng: random.Random) -> dict:
    weights = [c[4] for c in COUNTRIES]
    row = rng.choices(COUNTRIES, weights=weights, k=1)[0]
    code, name, region, subregion, _w, suffixes = row
    if code == "US":
        subregion = rng.choices(
            [s[0] for s in US_SUBREGIONS],
            weights=[s[1] for s in US_SUBREGIONS],
            k=1,
        )[0]
    return {
        "country_code": code,
        "country_name": name,
        "region": region,
        "subregion": subregion,
        "legal_suffix": rng.choice(suffixes),
    }


def choose_industry(rng: random.Random) -> str | None:
    # ~3% missing industry, as a CRM completeness issue.
    if rng.random() < 0.03:
        return None
    return rng.choices(
        [i[0] for i in INDUSTRIES],
        weights=[i[1] for i in INDUSTRIES],
        k=1,
    )[0]


def segment_from_employees(n: int) -> str:
    if n < 50:
        return "SMB"
    if n < 500:
        return "Mid-Market"
    return "Enterprise"


def draw_employees(rng: random.Random, segment: str) -> int:
    if segment == "SMB":
        return rng.randint(6, 49)
    if segment == "Mid-Market":
        return clamp(int(rng.lognormvariate(4.6, 0.55)), 50, 499)
    n = int(rng.lognormvariate(6.6, 0.5))
    return clamp(n, 500, 9000)


def draw_segment(rng: random.Random) -> str:
    return rng.choices(
        ["SMB", "Mid-Market", "Enterprise"],
        weights=[0.52, 0.33, 0.15],
        k=1,
    )[0]


def draw_channel(rng: random.Random, segment: str) -> str:
    if segment == "SMB":
        return rng.choices(
            ["self_serve", "inbound", "event", "outbound", "partner"],
            weights=[0.50, 0.24, 0.12, 0.08, 0.06],
            k=1,
        )[0]
    if segment == "Mid-Market":
        return rng.choices(
            ["self_serve", "inbound", "outbound", "partner", "event"],
            weights=[0.14, 0.34, 0.28, 0.16, 0.08],
            k=1,
        )[0]
    return rng.choices(
        ["self_serve", "inbound", "outbound", "partner", "event"],
        weights=[0.04, 0.22, 0.40, 0.28, 0.06],
        k=1,
    )[0]


def draw_initial_plan(rng: random.Random, segment: str) -> int:
    if segment == "SMB":
        return rng.choices([1, 2, 3], weights=[0.52, 0.40, 0.08], k=1)[0]
    if segment == "Mid-Market":
        return rng.choices([1, 2, 3, 4], weights=[0.08, 0.40, 0.42, 0.10], k=1)[0]
    return rng.choices([2, 3, 4], weights=[0.06, 0.34, 0.60], k=1)[0]


def draw_billing_interval(rng: random.Random, plan_id: int, segment: str) -> str:
    allowed = PLAN_BY_ID[plan_id]["billing_intervals"].split(",")
    if allowed == ["monthly"]:
        return "monthly"
    if allowed == ["annual"]:
        return "annual"
    annual_p = {"SMB": 0.28, "Mid-Market": 0.55, "Enterprise": 0.88}[segment]
    return "annual" if rng.random() < annual_p else "monthly"


def draw_seats(rng: random.Random, employees: int, plan_id: int) -> int:
    ratio = rng.uniform(0.12, 0.42)
    seats = int(round(employees * ratio))
    seats = max(2, seats)
    max_seats = PLAN_BY_ID[plan_id]["max_seats"]
    if max_seats:
        seats = min(seats, max_seats)
    return seats


def list_price(plan_id: int) -> float:
    return PLAN_BY_ID[plan_id]["list_price_monthly"]


def compute_mrr(plan_id: int, seats: int, billing_interval: str) -> float:
    unit = list_price(plan_id)
    if billing_interval == "annual":
        # Two months free on annual prepay: collect 10 months, recognise over 12.
        unit = unit * (10.0 / 12.0)
    return round_money(unit * seats)


def company_name(rng: random.Random, suffix: str) -> str:
    name = f"{rng.choice(ADJECTIVES)} {rng.choice(NOUNS)} {suffix}"
    return " ".join(name.split())


def slug(name: str) -> str:
    keep = "".join(ch.lower() if ch.isalnum() else " " for ch in name)
    return "-".join(keep.split())


def random_day_in_month(rng: random.Random, month: date, lo: int = 1, hi: int | None = None) -> date:
    last = month_end(month).day
    hi_ = last if hi is None else min(hi, last)
    day = rng.randint(lo, hi_)
    return date(month.year, month.month, day)


def poisson(rng: random.Random, lam: float) -> int:
    # Knuth for small lambda, otherwise round a normal approximation.
    if lam <= 0:
        return 0
    if lam < 30:
        l = math.exp(-lam)
        k = 0
        p = 1.0
        while p > l:
            k += 1
            p *= rng.random()
        return k - 1
    return max(0, int(round(rng.gauss(lam, math.sqrt(lam)))))


def signup_month_weights() -> list[tuple[date, float]]:
    months = months_between(PERIOD_START, AS_OF)
    out = []
    for i, m in enumerate(months):
        trend = 7.0 + i * 0.42
        seasonal = 1.0 + 0.14 * math.sin(2 * math.pi * (m.month - 3) / 12.0)
        w = trend * seasonal
        if m.year == 2024:
            w *= 1.18
        if m.year == 2026:
            w *= 0.86
        # Summer dip for Europe-heavy sales is already partly in seasonality.
        out.append((m, w))
    return out


@dataclass
class HistoryRow:
    subscription_id: int
    customer_id: int
    plan_id: int
    seats: int
    billing_interval: str
    mrr: float
    status: str
    valid_from: date
    valid_to: date | None = None


@dataclass
class Subscription:
    subscription_id: int
    customer_id: int
    plan_id: int
    seats: int
    billing_interval: str
    started_at: date
    ended_at: date | None
    status: str
    cancellation_reason: str | None = None
    mrr: float = 0.0


@dataclass
class Customer:
    customer_id: int
    customer_code: str
    organisation_name: str
    country_code: str
    country_name: str
    region: str
    subregion: str
    industry: str | None
    employee_count: int
    segment: str
    acquisition_channel: str
    signup_date: date
    trial_start_date: date | None
    trial_converted: bool
    status: str
    usage_propensity: float
    support_need: float
    growth_appetite: float
    is_failed_trial: bool = False
    subscriptions: list[Subscription] = field(default_factory=list)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = {}
            for k in fieldnames:
                v = row.get(k)
                if v is None:
                    out[k] = ""
                elif isinstance(v, bool):
                    out[k] = "true" if v else "false"
                elif isinstance(v, date):
                    out[k] = v.isoformat()
                elif isinstance(v, float):
                    out[k] = f"{v:.2f}" if k.endswith(("_amount", "mrr", "arr", "price", "unit_price", "total")) or "amount" in k or k in {"mrr", "arr"} else f"{v:.4f}".rstrip("0").rstrip(".")
                else:
                    out[k] = v
            writer.writerow(out)


def simulate(rng: random.Random) -> dict:
    month_weights = signup_month_weights()
    months = [m for m, _ in month_weights]
    weights = [w for _, w in month_weights]

    customers: list[Customer] = []
    subscriptions: list[Subscription] = []
    history: list[HistoryRow] = []
    events: list[dict] = []
    next_sub_id = 1
    next_event_id = 1

    def add_event(sub: Subscription, event_at: date, event_type: str, **extra: object) -> None:
        nonlocal next_event_id
        events.append(
            {
                "event_id": next_event_id,
                "subscription_id": sub.subscription_id,
                "customer_id": sub.customer_id,
                "event_at": event_at,
                "event_type": event_type,
                "plan_id": extra.get("plan_id", sub.plan_id),
                "seats": extra.get("seats", sub.seats),
                "mrr": extra.get("mrr", sub.mrr),
                "billing_interval": extra.get("billing_interval", sub.billing_interval),
                "notes": extra.get("notes"),
            }
        )
        next_event_id += 1

    def open_history(sub: Subscription, valid_from: date, status: str) -> HistoryRow:
        row = HistoryRow(
            subscription_id=sub.subscription_id,
            customer_id=sub.customer_id,
            plan_id=sub.plan_id,
            seats=sub.seats,
            billing_interval=sub.billing_interval,
            mrr=sub.mrr,
            status=status,
            valid_from=valid_from,
            valid_to=None,
        )
        history.append(row)
        return row

    def close_history(row: HistoryRow, valid_to: date) -> None:
        row.valid_to = valid_to

    def apply_change(
        sub: Subscription,
        hist: HistoryRow,
        change_date: date,
        new_plan: int | None = None,
        new_seats: int | None = None,
        new_interval: str | None = None,
        event_type: str = "updated",
        notes: str | None = None,
    ) -> HistoryRow:
        close_history(hist, change_date)
        if new_plan is not None:
            sub.plan_id = new_plan
        if new_seats is not None:
            sub.seats = new_seats
        if new_interval is not None:
            sub.billing_interval = new_interval
        sub.mrr = compute_mrr(sub.plan_id, sub.seats, sub.billing_interval)
        add_event(sub, change_date, event_type, notes=notes)
        return open_history(sub, change_date, "active")

    # ---- paying customers ----
    used_names: set[str] = set()
    for i in range(1, N_PAYING_CUSTOMERS + 1):
        signup_month = rng.choices(months, weights=weights, k=1)[0]
        # Avoid last 5 days of as-of month so new customers have a little history.
        signup = random_day_in_month(rng, signup_month)
        if signup > AS_OF:
            signup = AS_OF

        geo = choose_country(rng)
        segment = draw_segment(rng)
        # A handful of whales.
        if i in {12, 47, 118, 301}:
            segment = "Enterprise"
        employees = draw_employees(rng, segment)
        if i in {12, 47, 118, 301}:
            employees = rng.randint(1800, 7200)
        # Recompute segment from employees so they stay consistent.
        segment = segment_from_employees(employees)
        channel = draw_channel(rng, segment)
        industry = choose_industry(rng)

        name = company_name(rng, geo["legal_suffix"])
        while name in used_names:
            name = company_name(rng, geo["legal_suffix"])
        used_names.add(name)

        trial_start = None
        trial_converted = True
        if channel == "self_serve" and rng.random() < 0.72:
            trial_start = signup - timedelta(days=rng.choice([7, 14, 14, 14, 21]))
            if trial_start < PERIOD_START:
                trial_start = PERIOD_START

        cust = Customer(
            customer_id=i,
            customer_code=f"cus_{i:06d}",
            organisation_name=name,
            country_code=geo["country_code"],
            country_name=geo["country_name"],
            region=geo["region"],
            subregion=geo["subregion"],
            industry=industry,
            employee_count=employees,
            segment=segment,
            acquisition_channel=channel,
            signup_date=signup,
            trial_start_date=trial_start,
            trial_converted=trial_converted,
            status="active",
            usage_propensity=rng.betavariate(3.2, 1.8),
            support_need=rng.gammavariate(1.4, 0.55),
            growth_appetite=rng.betavariate(2.0, 2.4),
        )
        # A few chronic high-support accounts.
        if i % 37 == 0:
            cust.support_need = rng.uniform(2.8, 4.5)
        if i % 41 == 0:
            cust.usage_propensity = rng.uniform(0.12, 0.28)

        plan_id = draw_initial_plan(rng, segment)
        if i in {12, 47, 118, 301}:
            plan_id = 4
        interval = draw_billing_interval(rng, plan_id, segment)
        seats = draw_seats(rng, employees, plan_id)
        if i in {12, 47, 118, 301}:
            seats = rng.randint(220, 640)
            interval = "annual"

        sub = Subscription(
            subscription_id=next_sub_id,
            customer_id=cust.customer_id,
            plan_id=plan_id,
            seats=seats,
            billing_interval=interval,
            started_at=signup,
            ended_at=None,
            status="active",
            mrr=compute_mrr(plan_id, seats, interval),
        )
        next_sub_id += 1
        cust.subscriptions.append(sub)
        subscriptions.append(sub)
        add_event(sub, signup, "created")
        hist = open_history(sub, signup, "active")

        # Walk month by month after the signup month.
        current_month = add_months(month_start(signup), 1)
        end_limit = month_start(AS_OF)
        tenure_months = 0
        churned_once = False
        reactivated = False

        while current_month <= end_limit and sub.status == "active":
            tenure_months += 1
            # Drift usage propensity.
            cust.usage_propensity = min(0.98, max(0.05, cust.usage_propensity + rng.gauss(0, 0.03)))

            # Churn hazard.
            base = {"SMB": 0.034, "Mid-Market": 0.017, "Enterprise": 0.0075}[cust.segment]
            if tenure_months <= 3:
                base *= 1.55
            if cust.usage_propensity < 0.28:
                base *= 1.85
            if cust.support_need > 2.2:
                base *= 1.25
            if sub.billing_interval == "annual":
                base *= 0.62
            if sub.plan_id == 4:
                base *= 0.7
            # Whales almost never churn.
            if cust.customer_id in {12, 47, 118, 301}:
                base *= 0.15

            if rng.random() < base and tenure_months >= 2:
                cancel_day = random_day_in_month(rng, current_month)
                if cancel_day > AS_OF:
                    cancel_day = AS_OF
                reasons = ["price", "missing_features", "low_adoption", "competitor", "company_closed", "internal_tool"]
                reason_weights = [0.22, 0.18, 0.28, 0.16, 0.06, 0.10]
                if cust.usage_propensity < 0.3:
                    reason_weights = [0.12, 0.10, 0.48, 0.14, 0.06, 0.10]
                reason = rng.choices(reasons, weights=reason_weights, k=1)[0]
                close_history(hist, cancel_day)
                sub.ended_at = cancel_day
                sub.status = "cancelled"
                sub.cancellation_reason = reason
                add_event(sub, cancel_day, "cancelled", notes=reason, mrr=0.0, seats=sub.seats)
                cust.status = "churned"
                churned_once = True
                break

            # Expansion / contraction / plan change.
            changed = False
            # Upgrade
            if sub.plan_id < 4 and rng.random() < (0.010 + 0.018 * cust.growth_appetite + 0.012 * cust.usage_propensity):
                new_plan = sub.plan_id + 1
                # Seat cap may increase; keep seats unless over new cap (can't be over).
                if PLAN_BY_ID[new_plan]["billing_intervals"] == "annual":
                    interval = "annual"
                change_day = random_day_in_month(rng, current_month)
                hist = apply_change(
                    sub, hist, change_day, new_plan=new_plan, new_interval=interval, event_type="plan_upgraded"
                )
                changed = True
            # Downgrade
            elif sub.plan_id > 1 and rng.random() < (0.006 + (0.02 if cust.usage_propensity < 0.3 else 0)):
                new_plan = sub.plan_id - 1
                new_seats = sub.seats
                max_seats = PLAN_BY_ID[new_plan]["max_seats"]
                if max_seats and new_seats > max_seats:
                    new_seats = max_seats
                if PLAN_BY_ID[new_plan]["billing_intervals"] == "monthly":
                    interval = "monthly"
                change_day = random_day_in_month(rng, current_month)
                hist = apply_change(
                    sub,
                    hist,
                    change_day,
                    new_plan=new_plan,
                    new_seats=new_seats,
                    new_interval=interval,
                    event_type="plan_downgraded",
                )
                changed = True

            if not changed:
                # Seat expansion
                if rng.random() < (0.028 + 0.04 * cust.growth_appetite) * (1.4 if cust.usage_propensity > 0.7 else 1.0):
                    delta = max(1, int(round(sub.seats * rng.uniform(0.06, 0.22))))
                    new_seats = sub.seats + delta
                    max_seats = PLAN_BY_ID[sub.plan_id]["max_seats"]
                    if max_seats:
                        new_seats = min(new_seats, max_seats)
                    if new_seats > sub.seats:
                        change_day = random_day_in_month(rng, current_month)
                        hist = apply_change(
                            sub, hist, change_day, new_seats=new_seats, event_type="seats_expanded"
                        )
                        changed = True
                # Seat contraction
                elif rng.random() < (0.014 + (0.03 if cust.usage_propensity < 0.35 else 0)):
                    delta = max(1, int(round(sub.seats * rng.uniform(0.08, 0.25))))
                    new_seats = max(2, sub.seats - delta)
                    if new_seats < sub.seats:
                        change_day = random_day_in_month(rng, current_month)
                        hist = apply_change(
                            sub, hist, change_day, new_seats=new_seats, event_type="seats_contracted"
                        )
                        changed = True

            current_month = add_months(current_month, 1)

        # Reactivation for a subset of churned customers.
        if churned_once and (
            cust.segment != "SMB" or rng.random() < 0.45
        ):
            if sub.ended_at and rng.random() < (0.11 if cust.segment == "SMB" else 0.18):
                gap = rng.randint(2, 8)
                restart_month = add_months(month_start(sub.ended_at), gap)
                if restart_month <= end_limit:
                    restart = random_day_in_month(rng, restart_month)
                    if restart <= AS_OF:
                        # Often come back on a lower or similar plan.
                        plan_id = sub.plan_id
                        if rng.random() < 0.4 and plan_id > 1:
                            plan_id = plan_id - 1
                        seats = max(2, int(sub.seats * rng.uniform(0.55, 0.95)))
                        max_seats = PLAN_BY_ID[plan_id]["max_seats"]
                        if max_seats:
                            seats = min(seats, max_seats)
                        interval = draw_billing_interval(rng, plan_id, cust.segment)
                        new_sub = Subscription(
                            subscription_id=next_sub_id,
                            customer_id=cust.customer_id,
                            plan_id=plan_id,
                            seats=seats,
                            billing_interval=interval,
                            started_at=restart,
                            ended_at=None,
                            status="active",
                            mrr=compute_mrr(plan_id, seats, interval),
                        )
                        next_sub_id += 1
                        cust.subscriptions.append(new_sub)
                        subscriptions.append(new_sub)
                        add_event(new_sub, restart, "reactivated")
                        hist = open_history(new_sub, restart, "active")
                        cust.status = "active"
                        reactivated = True
                        sub = new_sub
                        # Continue a shorter post-reactivation life; some churn again.
                        current_month = add_months(month_start(restart), 1)
                        while current_month <= end_limit and sub.status == "active":
                            if rng.random() < 0.012:
                                cancel_day = random_day_in_month(rng, current_month)
                                close_history(hist, cancel_day)
                                sub.ended_at = cancel_day
                                sub.status = "cancelled"
                                sub.cancellation_reason = "low_adoption"
                                add_event(sub, cancel_day, "cancelled", notes="low_adoption", mrr=0.0)
                                cust.status = "churned"
                                break
                            if rng.random() < 0.03:
                                new_seats = sub.seats + max(1, int(sub.seats * 0.1))
                                max_seats = PLAN_BY_ID[sub.plan_id]["max_seats"]
                                if max_seats:
                                    new_seats = min(new_seats, max_seats)
                                if new_seats > sub.seats:
                                    change_day = random_day_in_month(rng, current_month)
                                    hist = apply_change(
                                        sub, hist, change_day, new_seats=new_seats, event_type="seats_expanded"
                                    )
                            current_month = add_months(current_month, 1)

        if sub.status == "active":
            cust.status = "active"

        customers.append(cust)

    # ---- failed trials (never converted) ----
    for j in range(N_FAILED_TRIALS):
        i = N_PAYING_CUSTOMERS + j + 1
        signup_month = rng.choices(months, weights=weights, k=1)[0]
        signup = random_day_in_month(rng, signup_month)
        geo = choose_country(rng)
        employees = rng.randint(6, 80)
        segment = segment_from_employees(employees)
        name = company_name(rng, geo["legal_suffix"])
        while name in used_names:
            name = company_name(rng, geo["legal_suffix"])
        used_names.add(name)
        trial_start = signup
        customers.append(
            Customer(
                customer_id=i,
                customer_code=f"cus_{i:06d}",
                organisation_name=name,
                country_code=geo["country_code"],
                country_name=geo["country_name"],
                region=geo["region"],
                subregion=geo["subregion"],
                industry=choose_industry(rng),
                employee_count=employees,
                segment=segment,
                acquisition_channel="self_serve",
                signup_date=signup,
                trial_start_date=trial_start,
                trial_converted=False,
                status="trial_expired",
                usage_propensity=rng.uniform(0.08, 0.35),
                support_need=rng.uniform(0.2, 1.1),
                growth_appetite=rng.uniform(0.1, 0.4),
                is_failed_trial=True,
            )
        )

    # Close open history rows.
    for row in history:
        if row.valid_to is None:
            row.valid_to = date(9999, 12, 31)

    return {
        "customers": customers,
        "subscriptions": subscriptions,
        "history": history,
        "events": events,
    }


def build_invoices(rng: random.Random, sim: dict) -> tuple[list[dict], list[dict]]:
    invoices: list[dict] = []
    items: list[dict] = []
    invoice_id = 1
    item_id = 1

    # Index history by subscription for as-of lookups.
    hist_by_sub: dict[int, list[HistoryRow]] = {}
    for row in sim["history"]:
        hist_by_sub.setdefault(row.subscription_id, []).append(row)
    for rows in hist_by_sub.values():
        rows.sort(key=lambda r: r.valid_from)

    def state_on(sub_id: int, on_date: date) -> HistoryRow | None:
        current = None
        for row in hist_by_sub.get(sub_id, []):
            if row.valid_from <= on_date and on_date < row.valid_to:
                return row
            if row.valid_from <= on_date:
                current = row
        return current

    def add_invoice(
        customer_id: int,
        subscription_id: int,
        invoice_date: date,
        line_specs: list[dict],
        force_status: str | None = None,
    ) -> None:
        nonlocal invoice_id, item_id
        if invoice_date > AS_OF:
            return
        subtotal = round_money(sum(s["amount"] for s in line_specs))
        # ~8% of invoices include a small one-time implementation or training fee
        # already passed in via line_specs.
        tax_rate = 0.0
        # Simple regional tax approximation for realism, not a tax engine.
        # Applied only as a separate tax line when country would typically add VAT/sales tax
        # onto the invoice total. We keep billed currency USD.
        tax_amount = 0.0
        total = round_money(subtotal + tax_amount)

        age_days = (AS_OF - invoice_date).days
        if force_status:
            status = force_status
        elif age_days <= 20 and rng.random() < 0.22:
            status = "open"
        elif rng.random() < 0.015:
            status = "void"
        elif rng.random() < 0.012 and age_days > 45:
            status = "uncollectible"
        else:
            status = "paid"

        due = invoice_date + timedelta(days=rng.choice([15, 30, 30, 45]))
        paid_at = ""
        if status == "paid":
            delay = max(0, int(rng.expovariate(1 / 8.0)))
            paid_day = invoice_date + timedelta(days=min(delay, 40))
            if paid_day > AS_OF:
                paid_day = AS_OF
            paid_at = paid_day.isoformat()

        invoices.append(
            {
                "invoice_id": invoice_id,
                "invoice_number": f"INV-{invoice_id:06d}",
                "customer_id": customer_id,
                "subscription_id": subscription_id,
                "invoice_date": invoice_date,
                "due_date": due,
                "status": status,
                "currency": "USD",
                "subtotal_amount": subtotal,
                "tax_amount": tax_amount,
                "total_amount": total,
                "paid_at": paid_at,
            }
        )
        for spec in line_specs:
            items.append(
                {
                    "invoice_item_id": item_id,
                    "invoice_id": invoice_id,
                    "customer_id": customer_id,
                    "subscription_id": subscription_id,
                    "plan_id": spec.get("plan_id"),
                    "description": spec["description"],
                    "item_type": spec["item_type"],
                    "quantity": spec.get("quantity", 1),
                    "unit_price": spec.get("unit_price", spec["amount"]),
                    "amount": spec["amount"],
                }
            )
            item_id += 1
        invoice_id += 1

    for sub in sim["subscriptions"]:
        end = sub.ended_at or AS_OF
        if sub.billing_interval == "monthly":
            period = month_start(sub.started_at)
            last = month_start(end)
            while period <= last:
                on = date(period.year, period.month, min(sub.started_at.day, month_end(period).day))
                if on < sub.started_at:
                    on = sub.started_at
                if sub.ended_at and on >= sub.ended_at:
                    break
                st = state_on(sub.subscription_id, on)
                if st is None or st.status != "active" or st.mrr <= 0:
                    period = add_months(period, 1)
                    continue
                unit = round_money(st.mrr / st.seats) if st.seats else st.mrr
                lines = [
                    {
                        "description": f"{PLAN_BY_ID[st.plan_id]['plan_name']} plan · {st.seats} seats",
                        "item_type": "subscription",
                        "plan_id": st.plan_id,
                        "quantity": st.seats,
                        "unit_price": unit,
                        "amount": st.mrr,
                    }
                ]
                # Recurring add-ons for a minority of business/enterprise invoices.
                if st.plan_id >= 3 and rng.random() < 0.18:
                    addon = round_money(rng.choice([49.0, 79.0, 129.0]))
                    lines.append(
                        {
                            "description": "Additional storage",
                            "item_type": "addon",
                            "plan_id": st.plan_id,
                            "quantity": 1,
                            "unit_price": addon,
                            "amount": addon,
                        }
                    )
                add_invoice(sub.customer_id, sub.subscription_id, on, lines)
                period = add_months(period, 1)
        else:
            # Annual: invoice on each anniversary while the subscription is active.
            on = sub.started_at
            while on <= end:
                if sub.ended_at and on >= sub.ended_at:
                    break
                st = state_on(sub.subscription_id, on)
                if st is None or st.status != "active":
                    break
                annual_amount = round_money(st.mrr * 12)
                unit = round_money(annual_amount / st.seats) if st.seats else annual_amount
                lines = [
                    {
                        "description": f"{PLAN_BY_ID[st.plan_id]['plan_name']} annual · {st.seats} seats",
                        "item_type": "subscription",
                        "plan_id": st.plan_id,
                        "quantity": st.seats,
                        "unit_price": unit,
                        "amount": annual_amount,
                    }
                ]
                if on == sub.started_at and st.plan_id >= 3 and rng.random() < 0.55:
                    impl = round_money(rng.choice([1500.0, 2500.0, 4000.0, 7500.0]))
                    lines.append(
                        {
                            "description": "Implementation and onboarding",
                            "item_type": "one_time",
                            "plan_id": st.plan_id,
                            "quantity": 1,
                            "unit_price": impl,
                            "amount": impl,
                        }
                    )
                if st.plan_id == 4:
                    # Premium support is included in list price conceptually, but some
                    # enterprise deals still bill a success-package as a line.
                    if rng.random() < 0.25:
                        pkg = round_money(rng.choice([2400.0, 3600.0, 6000.0]))
                        lines.append(
                            {
                                "description": "Customer success package",
                                "item_type": "addon",
                                "plan_id": st.plan_id,
                                "quantity": 1,
                                "unit_price": pkg,
                                "amount": pkg,
                            }
                        )
                add_invoice(sub.customer_id, sub.subscription_id, on, lines)
                try:
                    on = date(on.year + 1, sub.started_at.month, sub.started_at.day)
                except ValueError:
                    on = date(on.year + 1, sub.started_at.month, 28)

    return invoices, items


def build_usage(rng: random.Random, sim: dict) -> list[dict]:
    """Daily product usage at customer grain for days with recorded activity."""
    rows: list[dict] = []
    cust_by_id = {c.customer_id: c for c in sim["customers"]}
    hist_by_sub: dict[int, list[HistoryRow]] = {}
    for row in sim["history"]:
        hist_by_sub.setdefault(row.subscription_id, []).append(row)

    usage_id = 1
    for sub in sim["subscriptions"]:
        cust = cust_by_id[sub.customer_id]
        end = sub.ended_at or AS_OF
        # Pre-churn usage drop.
        decline_start = end - timedelta(days=40) if sub.ended_at else None
        day = sub.started_at
        while day <= end:
            st = None
            for h in hist_by_sub.get(sub.subscription_id, []):
                if h.valid_from <= day < h.valid_to:
                    st = h
                    break
            if st is None or st.status != "active":
                day += timedelta(days=1)
                continue

            propensity = cust.usage_propensity
            if decline_start and day >= decline_start:
                propensity *= 0.45
            # Weekends are quieter.
            if day.weekday() >= 5:
                activity_p = 0.18 * propensity
            else:
                activity_p = 0.62 * propensity + 0.12
            activity_p = min(0.95, activity_p)
            if rng.random() <= activity_p:
                active_seats = clamp(int(round(st.seats * rng.uniform(0.35, 0.95) * (0.5 + propensity))), 1, st.seats)
                work_items = max(0, int(rng.gauss(active_seats * (1.8 + 3.5 * propensity), active_seats * 0.8)))
                api_calls = 0
                if PLAN_BY_ID[st.plan_id]["includes_api_access"]:
                    api_calls = max(0, int(rng.gauss(active_seats * 18 * propensity, 25)))
                session_minutes = max(5, int(rng.gauss(active_seats * 22, 18)))
                rows.append(
                    {
                        "usage_id": usage_id,
                        "customer_id": sub.customer_id,
                        "subscription_id": sub.subscription_id,
                        "usage_date": day,
                        "active_seats": active_seats,
                        "licensed_seats": st.seats,
                        "work_items_completed": work_items,
                        "api_calls": api_calls,
                        "session_minutes": session_minutes,
                    }
                )
                usage_id += 1
            day += timedelta(days=1)

    # Light trial usage for failed trials.
    for cust in sim["customers"]:
        if not cust.is_failed_trial or not cust.trial_start_date:
            continue
        trial_end = min(cust.signup_date + timedelta(days=14), AS_OF)
        day = cust.trial_start_date
        while day <= trial_end:
            if rng.random() < 0.35:
                seats = clamp(int(cust.employee_count * 0.2), 1, 8)
                rows.append(
                    {
                        "usage_id": usage_id,
                        "customer_id": cust.customer_id,
                        "subscription_id": "",
                        "usage_date": day,
                        "active_seats": max(1, int(seats * rng.uniform(0.2, 0.7))),
                        "licensed_seats": seats,
                        "work_items_completed": rng.randint(0, 12),
                        "api_calls": 0,
                        "session_minutes": rng.randint(8, 90),
                    }
                )
                usage_id += 1
            day += timedelta(days=1)

    return rows


def build_tickets(rng: random.Random, sim: dict) -> list[dict]:
    rows: list[dict] = []
    ticket_id = 1
    agents = ["ava.nguyen", "marcus.holm", "priya.shah", "jonas.becker", "emma.cole", "unassigned"]

    for cust in sim["customers"]:
        if cust.is_failed_trial:
            n = poisson(rng, 0.4)
            start = cust.trial_start_date or cust.signup_date
            end = min(start + timedelta(days=20), AS_OF)
            for _ in range(n):
                opened = start + timedelta(days=rng.randint(0, max(0, (end - start).days)))
                rows.append(make_ticket(rng, ticket_id, cust, opened, None, agents))
                ticket_id += 1
            continue

        # Active lifetime across all subscriptions.
        first = min(s.started_at for s in cust.subscriptions)
        last = max((s.ended_at or AS_OF) for s in cust.subscriptions)
        months = max(1, (last.year - first.year) * 12 + (last.month - first.month) + 1)
        mean_per_month = 0.15 + cust.support_need * 0.55
        # Seat volume also drives tickets.
        avg_seats = sum(s.seats for s in cust.subscriptions) / len(cust.subscriptions)
        mean_per_month *= 0.7 + min(avg_seats, 80) / 80
        n = poisson(rng, mean_per_month * months)
        # Chronic accounts already have high support_need.
        for _ in range(n):
            opened = first + timedelta(days=rng.randint(0, max(0, (last - first).days)))
            if opened > AS_OF:
                opened = AS_OF
            sub = None
            for s in cust.subscriptions:
                if s.started_at <= opened and (s.ended_at is None or opened <= s.ended_at):
                    sub = s
                    break
            rows.append(make_ticket(rng, ticket_id, cust, opened, sub, agents))
            ticket_id += 1
    return rows


def make_ticket(
    rng: random.Random,
    ticket_id: int,
    cust: Customer,
    opened: date,
    sub: Subscription | None,
    agents: list[str],
) -> dict:
    category = rng.choices(
        TICKET_CATEGORIES,
        weights=[0.34, 0.22, 0.14, 0.16, 0.04, 0.10],
        k=1,
    )[0]
    if category == "outage":
        priority = rng.choices(["high", "urgent"], weights=[0.55, 0.45], k=1)[0]
    elif category == "billing":
        priority = rng.choices(["low", "medium", "high"], weights=[0.4, 0.45, 0.15], k=1)[0]
    else:
        priority = rng.choices(TICKET_PRIORITIES, weights=[0.28, 0.48, 0.18, 0.06], k=1)[0]

    # Most tickets resolve; recent ones may still be open.
    age = (AS_OF - opened).days
    if age < 3 and rng.random() < 0.5:
        status = rng.choice(["open", "pending"])
        resolved = None
        first_response_hours = rng.choice([1, 2, 4, 8, None])
    else:
        status = rng.choices(["solved", "closed", "open"], weights=[0.72, 0.22, 0.06], k=1)[0]
        if status in {"solved", "closed"}:
            hours = max(1, int(rng.lognormvariate(2.4, 0.9)))  # ~11h median
            if priority in {"high", "urgent"}:
                hours = max(1, int(hours * 0.45))
            resolved_dt = datetime(opened.year, opened.month, opened.day) + timedelta(hours=hours)
            resolved = min(resolved_dt.date(), AS_OF)
            first_response_hours = max(1, int(hours * rng.uniform(0.05, 0.35)))
        else:
            resolved = None
            first_response_hours = rng.choice([2, 4, 8, 24, None])

    agent = rng.choice(agents)
    if agent == "unassigned" and status in {"solved", "closed"}:
        agent = rng.choice(agents[:-1])

    csat = ""
    if status in {"solved", "closed"} and rng.random() < 0.42:
        # Slightly worse CSAT for chronic accounts.
        stars = rng.choices([1, 2, 3, 4, 5], weights=[0.04, 0.06, 0.14, 0.32, 0.44], k=1)[0]
        if cust.support_need > 2.5 and rng.random() < 0.35:
            stars = rng.choice([1, 2, 3])
        csat = stars

    return {
        "ticket_id": ticket_id,
        "ticket_number": f"TCK-{ticket_id:06d}",
        "customer_id": cust.customer_id,
        "subscription_id": sub.subscription_id if sub else "",
        "opened_at": opened,
        "resolved_at": resolved,
        "status": status,
        "category": category,
        "priority": priority,
        "channel": rng.choices(["email", "in_app", "chat", "phone"], weights=[0.46, 0.32, 0.16, 0.06], k=1)[0],
        "assignee": agent,
        "first_response_hours": first_response_hours if first_response_hours is not None else "",
        "csat_score": csat,
    }


def build_trials(sim: dict) -> list[dict]:
    rows = []
    trial_id = 1
    for cust in sim["customers"]:
        if not cust.trial_start_date:
            continue
        converted_at = cust.signup_date if cust.trial_converted and not cust.is_failed_trial else None
        ended = converted_at or min(cust.trial_start_date + timedelta(days=14), AS_OF)
        rows.append(
            {
                "trial_id": trial_id,
                "customer_id": cust.customer_id,
                "trial_start_date": cust.trial_start_date,
                "trial_end_date": ended,
                "converted": cust.trial_converted and not cust.is_failed_trial,
                "converted_at": converted_at if (cust.trial_converted and not cust.is_failed_trial) else "",
                "acquisition_channel": cust.acquisition_channel,
            }
        )
        trial_id += 1
    return rows


def customer_rows(sim: dict) -> list[dict]:
    rows = []
    for c in sim["customers"]:
        rows.append(
            {
                "customer_id": c.customer_id,
                "customer_code": c.customer_code,
                "organisation_name": c.organisation_name,
                "country_code": c.country_code,
                "country_name": c.country_name,
                "region": c.region,
                "subregion": c.subregion,
                "industry": c.industry or "",
                "employee_count": c.employee_count,
                "segment": c.segment,
                "acquisition_channel": c.acquisition_channel,
                "signup_date": c.signup_date,
                "trial_start_date": c.trial_start_date or "",
                "status": c.status,
            }
        )
    return rows


def subscription_rows(sim: dict) -> list[dict]:
    rows = []
    for s in sim["subscriptions"]:
        rows.append(
            {
                "subscription_id": s.subscription_id,
                "customer_id": s.customer_id,
                "plan_id": s.plan_id,
                "seats": s.seats,
                "billing_interval": s.billing_interval,
                "mrr": s.mrr if s.status == "active" else 0.0,
                "started_at": s.started_at,
                "ended_at": s.ended_at or "",
                "status": s.status,
                "cancellation_reason": s.cancellation_reason or "",
            }
        )
    return rows


def history_rows(sim: dict) -> list[dict]:
    rows = []
    hid = 1
    for h in sim["history"]:
        rows.append(
            {
                "subscription_history_id": hid,
                "subscription_id": h.subscription_id,
                "customer_id": h.customer_id,
                "plan_id": h.plan_id,
                "seats": h.seats,
                "billing_interval": h.billing_interval,
                "mrr": h.mrr,
                "status": h.status,
                "valid_from": h.valid_from,
                "valid_to": h.valid_to,
                "is_current": h.valid_to == date(9999, 12, 31),
            }
        )
        hid += 1
    return rows


def main() -> None:
    rng = random.Random(SEED)
    print(f"Generating Oakwell source data with seed={SEED} as_of={AS_OF.isoformat()}")
    sim = simulate(rng)
    invoices, items = build_invoices(rng, sim)
    usage = build_usage(rng, sim)
    tickets = build_tickets(rng, sim)
    trials = build_trials(sim)

    plan_rows = []
    for p in PLANS:
        plan_rows.append(
            {
                **p,
                "includes_sso": p["includes_sso"],
                "includes_premium_support": p["includes_premium_support"],
                "includes_api_access": p["includes_api_access"],
                "max_seats": p["max_seats"] if p["max_seats"] is not None else "",
            }
        )

    write_csv(
        SEED_DIR / "raw_plans.csv",
        plan_rows,
        [
            "plan_id",
            "plan_code",
            "plan_name",
            "plan_tier",
            "list_price_monthly",
            "billing_intervals",
            "max_seats",
            "includes_sso",
            "includes_premium_support",
            "includes_api_access",
        ],
    )
    write_csv(
        SEED_DIR / "raw_customers.csv",
        customer_rows(sim),
        [
            "customer_id",
            "customer_code",
            "organisation_name",
            "country_code",
            "country_name",
            "region",
            "subregion",
            "industry",
            "employee_count",
            "segment",
            "acquisition_channel",
            "signup_date",
            "trial_start_date",
            "status",
        ],
    )
    write_csv(
        SEED_DIR / "raw_subscriptions.csv",
        subscription_rows(sim),
        [
            "subscription_id",
            "customer_id",
            "plan_id",
            "seats",
            "billing_interval",
            "mrr",
            "started_at",
            "ended_at",
            "status",
            "cancellation_reason",
        ],
    )
    write_csv(
        SEED_DIR / "raw_subscription_history.csv",
        history_rows(sim),
        [
            "subscription_history_id",
            "subscription_id",
            "customer_id",
            "plan_id",
            "seats",
            "billing_interval",
            "mrr",
            "status",
            "valid_from",
            "valid_to",
            "is_current",
        ],
    )
    write_csv(
        SEED_DIR / "raw_subscription_events.csv",
        sim["events"],
        [
            "event_id",
            "subscription_id",
            "customer_id",
            "event_at",
            "event_type",
            "plan_id",
            "seats",
            "mrr",
            "billing_interval",
            "notes",
        ],
    )
    write_csv(
        SEED_DIR / "raw_invoices.csv",
        invoices,
        [
            "invoice_id",
            "invoice_number",
            "customer_id",
            "subscription_id",
            "invoice_date",
            "due_date",
            "status",
            "currency",
            "subtotal_amount",
            "tax_amount",
            "total_amount",
            "paid_at",
        ],
    )
    write_csv(
        SEED_DIR / "raw_invoice_items.csv",
        items,
        [
            "invoice_item_id",
            "invoice_id",
            "customer_id",
            "subscription_id",
            "plan_id",
            "description",
            "item_type",
            "quantity",
            "unit_price",
            "amount",
        ],
    )
    write_csv(
        SEED_DIR / "raw_product_usage.csv",
        usage,
        [
            "usage_id",
            "customer_id",
            "subscription_id",
            "usage_date",
            "active_seats",
            "licensed_seats",
            "work_items_completed",
            "api_calls",
            "session_minutes",
        ],
    )
    write_csv(
        SEED_DIR / "raw_support_tickets.csv",
        tickets,
        [
            "ticket_id",
            "ticket_number",
            "customer_id",
            "subscription_id",
            "opened_at",
            "resolved_at",
            "status",
            "category",
            "priority",
            "channel",
            "assignee",
            "first_response_hours",
            "csat_score",
        ],
    )
    write_csv(
        SEED_DIR / "raw_trials.csv",
        trials,
        [
            "trial_id",
            "customer_id",
            "trial_start_date",
            "trial_end_date",
            "converted",
            "converted_at",
            "acquisition_channel",
        ],
    )

    paying = [c for c in sim["customers"] if not c.is_failed_trial]
    active = [c for c in paying if c.status == "active"]
    print("Wrote seeds to", SEED_DIR)
    print(f"  customers:            {len(sim['customers']):>7}")
    print(f"  paying customers:     {len(paying):>7}")
    print(f"  active customers:     {len(active):>7}")
    print(f"  failed trials:        {N_FAILED_TRIALS:>7}")
    print(f"  subscriptions:        {len(sim['subscriptions']):>7}")
    print(f"  subscription history: {len(sim['history']):>7}")
    print(f"  subscription events:  {len(sim['events']):>7}")
    print(f"  invoices:             {len(invoices):>7}")
    print(f"  invoice items:        {len(items):>7}")
    print(f"  product usage days:   {len(usage):>7}")
    print(f"  support tickets:      {len(tickets):>7}")
    print(f"  trials:               {len(trials):>7}")


if __name__ == "__main__":
    main()
