# @noetfield/gate

TypeScript client for **Noetfield GEL** `POST /v1/decision`.

```bash
npm install @noetfield/gate   # publish pending
```

```typescript
import { postDecision, SAMPLE_APPROVE_INTENT } from "@noetfield/gate";

const receipt = await postDecision(SAMPLE_APPROVE_INTENT, {
  apiKey: process.env.NOETFIELD_API_KEY!,
});
console.log(receipt.decision, receipt.audit_id);
```

Python chain tools: `pip install noetfield-gate` · https://www.noetfield.com/gel/
