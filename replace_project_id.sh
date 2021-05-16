PROJECT_PLACEHOLDER="YOUR_PROJECT_ID_HERE"
PROJECT_ID=$1


find . -type f -name '*' -print0 | xargs -0 sed -i '' -e "s/$PROJECT_PLACEHOLDER/$PROJECT_ID/g"