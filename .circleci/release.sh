#!/usr/bin/env bash
set -eo pipefail
[[ -f ../.env ]] && . ../.env

TAG=0.3
CIRCLE_BRANCH=tag/0.3

export API_URL=https://api.github.com/repos/bitcaster-io/bitcaster
export TAG=${TAG:=${CIRCLE_BRANCH#*/}}
export TODAY=`date '+%d %B %Y at %H:%M'`
function is_pre()
{
    [[ "$(echo "$TAG" | sed 's/[0-9.]//g')" == "" ]] && echo false || echo true
}
function data() {
cat <<EOF
{"tag_name": "$TAG",
  "name": "v$TAG",
  "body": "version $TAG - Built on $TODAY",
  "draft": false,
  "prerelease": $(is_pre)
}
EOF
}
data=$(data)
echo $data | jq  .

curl \
  --fail \
  -H "Accept: application/json" \
  -H "Content-Type:application/json" \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  ${API_URL}/releases \
  -d "$data"
