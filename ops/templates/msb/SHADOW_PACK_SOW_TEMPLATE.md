# Statement of Work — MSB Shadow Pack (template)

**Between:** Noetfield Systems Inc. (“Noetfield”)  
**And:** __________________________ (“MSB Partner”)  
**Effective date:** __________

## 1. Scope

Noetfield provides a **30-calendar-day shadow governance pilot**:

- Pilot API credentials bound to MSB Partner `tenant_id`: ____________________
- `POST /api/v1/governance/evaluate` in **`mode: shadow`** only
- `GET /api/v1/governance/audit-export` and ledger access for agreed RIDs
- Optional read-only `POST /api/v1/governance/partner-signals`
- **Two (2)** engineering workshops (90 min each): integration design + audit export review

## 2. Out of scope

- Payment execution, custody, or settlement by Noetfield  
- Production `enforce` mode (requires separate addendum)  
- Named co-marketing without separate approval  

## 3. MSB Partner responsibilities

- Call evaluate from **staging** before MSB payment APIs  
- Never expose pilot API keys in mobile client binaries  
- MSB retains all FINTRAC/RPAA licensing and execution  

## 4. Fees

**Fixed fee:** __________ CAD (suggested band $12,000–$18,000)  
**Payment terms:** 50% on signature, 50% on workshop 2 completion.

## 5. Term

30 days from key issuance. Extension by written change order.

## 6. Data

Canada-first processing per DPA schedule (attach). Noetfield subprocessors listed in DPA.

## 7. Boundary

Noetfield is a **software vendor** outside RPAA/MSB perimeter for MSB Partner’s regulatory filings.

---

**Signatures**

Noetfield: ____________________  
MSB Partner: ____________________
