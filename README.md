# MRP Smart Reservation

**Intelligent, priority-based stock reservation for Manufacturing Orders in Odoo 17 & 18.**

## The Problem

Odoo 17/18 natively supports reservation methods (At Confirmation, Manually, Before Scheduled Date).  
But when stock is **insufficient for all confirmed MOs**, Odoo has no built-in mechanism to decide *which MO gets the stock first*.

Result: a distant MO scheduled for September can block components needed by an urgent MO due tomorrow.

## The Solution

This module adds a **global rebalancing engine** that distributes stock according to priority:

| Priority | Category | Condition | Behavior |
|---|---|---|---|
| 1 (max) | Forced | `Force Reservation` button clicked | Reserved first, sorted by date |
| 2 | Urgent | Scheduled date ≤ today + horizon | Reserved after forced, sorted by date |
| 3 (min) | Distant | Scheduled date > today + horizon | Never reserved — stock stays free |

## Features

- **Configurable horizon** (Manufacturing → Configuration → Settings)
- **Force Reservation** button on any MO form (orange button)
- **Cancel Forced Reservation** button to restore normal priority
- **Rebalance** action available from the MO list (Action menu)
- **Daily cron** for automatic overnight rebalancing
- **Automatic rebalancing** after each scheduler run
- **Visual status badge** on MO form and list views

## Configuration

Go to **Manufacturing → Configuration → Settings → Smart Reservation**  
Set the **Reservation Horizon** (default: 30 days).

## Compatibility

- Odoo 17.0 Community & Enterprise
- Odoo 18.0 Community & Enterprise
