PROJECT_ID=$1
PROJECT_PLACEHOLDER="YOUR_PROJECT_ID_HERE"

find . -type f -name '*' -print0 | xargs -0 sed -i '' -e "s/$PROJECT_PLACEHOLDER/$PROJECT_ID/g"