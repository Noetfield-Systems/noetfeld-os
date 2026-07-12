#!/bin/bash
# fix_motor_secret.sh — stores the noetfield-motor App key + ID as GitHub Actions
# credentials, straight from the .pem file. Never prints or copies the key anywhere.
set -e

echo "== noetfield-motor credential fix =="

PEM=$(ls -t ~/Downloads/noetfield-motor.*.private-key.pem 2>/dev/null | head -1)
if [ -z "$PEM" ]; then
  echo "❌ No noetfield-motor .pem file found in ~/Downloads."
  echo "   Generate one: github.com -> Noetfield-Systems -> Settings -> Developer settings"
  echo "   -> GitHub Apps -> noetfield-motor -> Generate a private key"
  exit 1
fi
echo "Key file: $PEM (newest one in Downloads)"

if ! command -v gh >/dev/null 2>&1; then
  echo "❌ GitHub CLI (gh) is not installed. Install: brew install gh"; exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "❌ gh is not logged in. Run: gh auth login   (then run this script again)"; exit 1
fi

echo "-- storing secret MOTOR_APP_PRIVATE_KEY --"
if gh secret set MOTOR_APP_PRIVATE_KEY --org Noetfield-Systems --visibility all < "$PEM" 2>/dev/null; then
  echo "✅ Org-level secret saved (visible to all repositories)."
else
  echo "   Org-level not permitted with this token — using repo-level instead."
  gh secret set MOTOR_APP_PRIVATE_KEY -R Noetfield-Systems/noetfield-sandbox-private < "$PEM"
  echo "✅ Repo-level secret saved on noetfield-sandbox-private."
fi

echo "-- storing variable MOTOR_APP_ID = 4275961 --"
gh variable set MOTOR_APP_ID --org Noetfield-Systems --visibility all --body 4275961 2>/dev/null \
  || gh variable set MOTOR_APP_ID -R Noetfield-Systems/noetfield-sandbox-private --body 4275961
echo "✅ Variable saved."

echo "== VERIFY =="
gh secret list --org Noetfield-Systems 2>/dev/null && echo "(org secrets above)"
gh secret list -R Noetfield-Systems/noetfield-sandbox-private 2>/dev/null && echo "(repo secrets above)"

echo ""
echo "DONE. If MOTOR_APP_PRIVATE_KEY appears in a list above, the motor credentials are live."
echo "It does not matter what was pasted in the browser earlier — this overwrote it."
