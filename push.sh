#!/bin/bash

if [ "$1" != "-m" ] || [ -z "$2" ]; then
  echo "사용법: ./push.sh -m \"커밋 메시지\""
  exit 1
fi

COMMIT_MSG="$2"

echo 'CSS 빌드 START..'
if python3 scripts/build_css.py --update-html; then
    echo "✅ CSS 빌드 성공"
    
    # admin.css가 git에 추적되는지 확인
    git add static/css/admin.css
    git add .
    git commit -m "$COMMIT_MSG"
    git push -f
else
    echo "❌ CSS 빌드 실패! Push를 중단합니다."
    exit 1
fi