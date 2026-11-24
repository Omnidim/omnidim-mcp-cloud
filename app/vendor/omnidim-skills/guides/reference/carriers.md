---
name: "Which carrier to buy a number from"
description: "The carriers each region holds and what each one stocks, why `carrier` is required on search and purchase, and the rules that decide which to use: ask rather than pick, buy from the carrier you searched, verification is per carrier."
---

# Which carrier to buy from

A region holds one or more carriers. They do not stock the same numbers and
they are not interchangeable. `purchasePhoneNumber` requires `carrier`. Pass
the same `carrier` to `searchPhoneNumbers`, so you search the stock you buy
from.

## What each one stocks

| Region | `carrier` | Stocks |
|---|---|---|
| `IN` | `carrier-1` | Landline numbers, city codes 11, 12 and 80 |
| `IN` | `carrier-2-new` | Mobile numbers, 94 and 79 series |
| `US` | `carrier-us` | US local numbers, by area code |

A snapshot, not the authority. The API is: omit `carrier` on a call that needs
one and the `409 carrier_required` body lists that region's carriers with what
each stocks and whether each is taking orders. Many MCP clients will not let
you omit a required field, which is why the table is here at all. If a user
names a carrier that is not in it, pass it through rather than refusing: this
file can be older than the account.

## Rules

- **Ask, do not pick.** Landline and mobile are not substitutes, and buying
  spends the account's balance on a rental that renews. If the user has not
  said which they want, ask, and say what each one stocks.
- **Buy from the carrier you searched.** `searchPhoneNumbers` echoes the
  `carrier` its results came from. Pass that exact value to
  `purchasePhoneNumber`, or you are buying out of inventory you never looked
  at.
- **Verification is per carrier.** An account verified on one carrier of a
  region is not verified on the other, and a purchase it has not cleared fails
  with `409 kyc_incomplete`. Verification is not on this surface: send the user
  to the dashboard number shop.
- **A carrier can be down.** The `409 carrier_required` body says whether each
  one is taking orders. If the user's carrier is down, tell them and ask
  whether to wait or use another. A purchase charges the account first and
  refunds it if the carrier then fails.
- **The name is stable across a rename**, so it is safe for a user to store.
