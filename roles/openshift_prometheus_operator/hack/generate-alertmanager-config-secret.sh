#!/bin/bash

function b64() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    base64 -b 0
  else
    base64 --wrap=0
  fi
}

cat <<-EOF
apiVersion: v1
kind: Secret
metadata:
  name: alertmanager-main
data:
  alertmanager.yaml: $(cat files/assets/alertmanager/alertmanager.yaml | b64)
EOF
