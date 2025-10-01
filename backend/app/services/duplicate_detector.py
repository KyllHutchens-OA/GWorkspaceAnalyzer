"""
Duplicate Detection Service
Analyzes invoices to find duplicates, price increases, and subscription issues
"""
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, date
from decimal import Decimal
from collections import defaultdict

from ..models import (
    ParsedInvoice,
    DuplicateFinding,
    DuplicateType,
    PriceIncreaseFinding,
    UnusedSubscriptionFinding,
)

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """
    Detects duplicate charges, price increases, and subscription issues
    """

    def __init__(self, duplicate_window_days: int = 7, price_threshold: float = 20.0):
        """
        Initialize detector

        Args:
            duplicate_window_days: Days within which to consider duplicates
            price_threshold: Percentage increase to flag (default 20%)
        """
        self.duplicate_window_days = duplicate_window_days
        self.price_threshold = price_threshold

    def detect_duplicates(
        self, invoices: List[Dict]
    ) -> List[DuplicateFinding]:
        """
        Detect duplicate charges in a list of invoices

        Args:
            invoices: List of invoice dictionaries from database

        Returns:
            List of duplicate findings
        """
        findings = []

        # Group invoices by vendor
        by_vendor = self._group_by_vendor(invoices)

        for vendor_name, vendor_invoices in by_vendor.items():
            # Check for exact duplicates
            exact_dupes = self._find_exact_duplicates(vendor_invoices)
            findings.extend(exact_dupes)

            # Check for probable duplicates
            probable_dupes = self._find_probable_duplicates(vendor_invoices)
            findings.extend(probable_dupes)

        logger.info(f"Found {len(findings)} duplicate findings")
        return findings

    def _group_by_vendor(self, invoices: List[Dict]) -> Dict[str, List[Dict]]:
        """Group invoices by normalized vendor name"""
        grouped = defaultdict(list)

        for invoice in invoices:
            vendor = invoice.get("vendor_name_normalized", "unknown")
            grouped[vendor].append(invoice)

        return dict(grouped)

    def _find_exact_duplicates(
        self, invoices: List[Dict]
    ) -> List[DuplicateFinding]:
        """
        Find exact duplicates: same invoice number, vendor, and amount

        Args:
            invoices: List of invoices from same vendor

        Returns:
            List of exact duplicate findings
        """
        findings = []

        # Group by invoice number
        by_invoice_number = defaultdict(list)

        for inv in invoices:
            invoice_num = inv.get("invoice_number")
            if invoice_num:
                by_invoice_number[invoice_num].append(inv)

        # Find duplicates
        for invoice_num, duplicates in by_invoice_number.items():
            if len(duplicates) > 1:
                # Check if amounts match
                amounts = [Decimal(str(inv.get("amount", 0))) for inv in duplicates]
                if len(set(amounts)) == 1:  # All same amount
                    # This is an exact duplicate
                    total_waste = amounts[0] * (len(duplicates) - 1)

                    finding = DuplicateFinding(
                        duplicate_type=DuplicateType.EXACT,
                        vendor_name=duplicates[0].get("vendor_name", "Unknown"),
                        invoice_count=len(duplicates),
                        amount=total_waste,
                        confidence_score=0.98,
                        invoice_ids=[inv["id"] for inv in duplicates],
                        details={
                            "invoice_number": invoice_num,
                            "charge_amount": float(amounts[0]),
                            "charged_times": len(duplicates),
                            "dates": [inv.get("invoice_date") for inv in duplicates],
                        },
                    )

                    findings.append(finding)

        return findings

    def _find_probable_duplicates(
        self, invoices: List[Dict]
    ) -> List[DuplicateFinding]:
        """
        Find probable duplicates: same vendor, amount, within time window

        CONSERVATIVE APPROACH: Only flag if charges appear within 2-3 days
        to avoid flagging regular recurring subscriptions (weekly/monthly).
        These are FLAGS for user review, NOT guaranteed savings.

        Args:
            invoices: List of invoices from same vendor

        Returns:
            List of probable duplicate findings (for user review only)
        """
        findings = []

        # Sort by date
        sorted_invoices = sorted(
            invoices,
            key=lambda x: x.get("invoice_date") or date.min
        )

        # Group by amount
        by_amount = defaultdict(list)
        for inv in sorted_invoices:
            amount = Decimal(str(inv.get("amount", 0)))
            if amount > 0:
                by_amount[amount].append(inv)

        # Check each amount group for temporal proximity
        for amount, amount_invoices in by_amount.items():
            if len(amount_invoices) < 2:
                continue

            # Use SHORTER window (2 days) to avoid flagging weekly subscriptions
            short_window = 2

            # Find clusters within short time window
            clusters = self._find_temporal_clusters(
                amount_invoices, short_window
            )

            for cluster in clusters:
                if len(cluster) > 1:
                    # Calculate date range
                    dates = [inv.get("invoice_date") for inv in cluster if inv.get("invoice_date")]
                    if dates:
                        date_range = (max(dates) - min(dates)).days
                    else:
                        date_range = 0

                    # Skip if already found as exact duplicate
                    invoice_numbers = [inv.get("invoice_number") for inv in cluster]
                    if len(set(invoice_numbers)) == 1 and invoice_numbers[0]:
                        continue  # Already caught by exact duplicate

                    # Check if this is likely a regular subscription
                    if self._is_likely_subscription(amount_invoices):
                        continue  # Don't flag regular subscriptions

                    # DON'T count as waste - this is just a flag for user review
                    finding = DuplicateFinding(
                        duplicate_type=DuplicateType.PROBABLE,
                        vendor_name=cluster[0].get("vendor_name", "Unknown"),
                        invoice_count=len(cluster),
                        amount=Decimal("0.00"),  # Zero - not counted as guaranteed waste
                        date_range_days=date_range,
                        confidence_score=0.50,  # Lower confidence - needs verification
                        invoice_ids=[inv["id"] for inv in cluster],
                        details={
                            "charge_amount": float(amount),
                            "charged_times": len(cluster),
                            "date_range_days": date_range,
                            "dates": [str(inv.get("invoice_date")) for inv in cluster],
                            "requires_review": True,
                            "potential_waste": float(amount * (len(cluster) - 1)),
                            "note": "Please verify if this is a legitimate recurring charge or a duplicate",
                        },
                    )

                    findings.append(finding)

        return findings

    def _is_likely_subscription(self, invoices: List[Dict]) -> bool:
        """
        Check if invoices appear to be a regular subscription

        Args:
            invoices: List of invoices with same amount

        Returns:
            True if likely a subscription (regular intervals)
        """
        if len(invoices) < 3:
            return False

        # Sort by date
        sorted_invoices = sorted(
            [inv for inv in invoices if inv.get("invoice_date")],
            key=lambda x: x.get("invoice_date")
        )

        if len(sorted_invoices) < 3:
            return False

        # Calculate intervals
        intervals = []
        for i in range(len(sorted_invoices) - 1):
            date1 = sorted_invoices[i].get("invoice_date")
            date2 = sorted_invoices[i + 1].get("invoice_date")
            if date1 and date2:
                intervals.append((date2 - date1).days)

        if not intervals:
            return False

        avg_interval = sum(intervals) / len(intervals)

        # Common subscription patterns
        subscription_patterns = [
            (7, 2),    # Weekly
            (14, 3),   # Bi-weekly
            (30, 5),   # Monthly
            (90, 7),   # Quarterly
            (365, 14), # Annual
        ]

        for expected_days, tolerance in subscription_patterns:
            if abs(avg_interval - expected_days) <= tolerance:
                return True

        return False

    def _find_temporal_clusters(
        self, invoices: List[Dict], window_days: int
    ) -> List[List[Dict]]:
        """
        Group invoices into temporal clusters

        Args:
            invoices: Sorted list of invoices
            window_days: Days within which to group

        Returns:
            List of invoice clusters
        """
        if not invoices:
            return []

        clusters = []
        current_cluster = [invoices[0]]

        for inv in invoices[1:]:
            current_date = inv.get("invoice_date")
            prev_date = current_cluster[-1].get("invoice_date")

            if current_date and prev_date:
                days_diff = (current_date - prev_date).days

                if days_diff <= window_days:
                    current_cluster.append(inv)
                else:
                    if len(current_cluster) > 1:
                        clusters.append(current_cluster)
                    current_cluster = [inv]
            else:
                # Missing dates, start new cluster
                if len(current_cluster) > 1:
                    clusters.append(current_cluster)
                current_cluster = [inv]

        # Add final cluster
        if len(current_cluster) > 1:
            clusters.append(current_cluster)

        return clusters

    def detect_price_increases(
        self, invoices: List[Dict]
    ) -> List[PriceIncreaseFinding]:
        """
        Detect significant price increases for recurring charges

        Args:
            invoices: List of invoice dictionaries

        Returns:
            List of price increase findings
        """
        findings = []

        # Group by vendor
        by_vendor = self._group_by_vendor(invoices)

        for vendor_name, vendor_invoices in by_vendor.items():
            # Sort by date
            sorted_invoices = sorted(
                vendor_invoices,
                key=lambda x: x.get("invoice_date") or date.min
            )

            # Compare consecutive invoices
            for i in range(len(sorted_invoices) - 1):
                old_inv = sorted_invoices[i]
                new_inv = sorted_invoices[i + 1]

                old_amount = Decimal(str(old_inv.get("amount", 0)))
                new_amount = Decimal(str(new_inv.get("amount", 0)))

                if old_amount > 0 and new_amount > old_amount:
                    increase_pct = float((new_amount - old_amount) / old_amount * 100)

                    if increase_pct >= self.price_threshold:
                        finding = PriceIncreaseFinding(
                            vendor_name=old_inv.get("vendor_name", "Unknown"),
                            old_amount=old_amount,
                            new_amount=new_amount,
                            increase_percentage=increase_pct,
                            old_date=old_inv.get("invoice_date"),
                            new_date=new_inv.get("invoice_date"),
                            amount=new_amount - old_amount,
                            confidence_score=0.90,
                            invoice_ids=[old_inv["id"], new_inv["id"]],
                            details={
                                "old_amount": float(old_amount),
                                "new_amount": float(new_amount),
                                "increase_amount": float(new_amount - old_amount),
                                "increase_percentage": increase_pct,
                            },
                        )

                        findings.append(finding)

        logger.info(f"Found {len(findings)} price increase findings")
        return findings

    def detect_subscription_sprawl(
        self, invoices: List[Dict]
    ) -> List[UnusedSubscriptionFinding]:
        """
        Detect multiple subscriptions to same vendor or overlapping services

        Args:
            invoices: List of invoice dictionaries

        Returns:
            List of subscription sprawl findings
        """
        findings = []

        # Group by vendor
        by_vendor = self._group_by_vendor(invoices)

        for vendor_name, vendor_invoices in by_vendor.items():
            # Check for recurring pattern (multiple charges)
            if len(vendor_invoices) < 2:
                continue

            # Sort by date
            sorted_invoices = sorted(
                vendor_invoices,
                key=lambda x: x.get("invoice_date") or date.min
            )

            # Check if amounts are consistent (subscription)
            amounts = [Decimal(str(inv.get("amount", 0))) for inv in sorted_invoices]
            amount_counts = defaultdict(int)
            for amt in amounts:
                amount_counts[amt] += 1

            # Find most common amount (likely subscription price)
            if amount_counts:
                recurring_amount = max(amount_counts, key=amount_counts.get)
                recurring_count = amount_counts[recurring_amount]

                # If we see the same amount 3+ times, likely a subscription
                if recurring_count >= 3:
                    # Check for frequency
                    dates = [inv.get("invoice_date") for inv in sorted_invoices if inv.get("amount") == recurring_amount]
                    if len(dates) >= 2:
                        avg_days = self._calculate_avg_frequency(dates)
                        frequency = self._determine_frequency(avg_days)

                        # For now, just flag duplicate subscriptions
                        # More sophisticated detection would check for:
                        # - Multiple account emails
                        # - Unused seat detection (requires usage data)
                        # - Overlapping services (requires categorization)

                        # Placeholder for duplicate account detection
                        # This would need additional data (e.g., account IDs from invoices)

        logger.info(f"Found {len(findings)} subscription sprawl findings")
        return findings

    def _calculate_avg_frequency(self, dates: List[date]) -> float:
        """Calculate average days between charges"""
        if len(dates) < 2:
            return 0

        sorted_dates = sorted(dates)
        intervals = []

        for i in range(len(sorted_dates) - 1):
            days = (sorted_dates[i + 1] - sorted_dates[i]).days
            intervals.append(days)

        return sum(intervals) / len(intervals) if intervals else 0

    def _determine_frequency(self, avg_days: float) -> str:
        """Determine billing frequency from average days"""
        if avg_days < 10:
            return "weekly"
        elif avg_days < 35:
            return "monthly"
        elif avg_days < 100:
            return "quarterly"
        elif avg_days < 400:
            return "annual"
        else:
            return "irregular"

    def analyze_all(self, invoices: List[Dict]) -> Dict[str, List]:
        """
        Run all detection algorithms

        Args:
            invoices: List of invoice dictionaries

        Returns:
            Dictionary with all findings categorized
        """
        return {
            "duplicates": self.detect_duplicates(invoices),
            "price_increases": self.detect_price_increases(invoices),
            "subscription_sprawl": self.detect_subscription_sprawl(invoices),
        }

    def calculate_total_waste(self, findings: List) -> Decimal:
        """
        Calculate total money wasted across all findings

        Args:
            findings: List of Finding objects

        Returns:
            Total waste amount
        """
        total = Decimal("0.00")
        for finding in findings:
            total += finding.amount
        return total
