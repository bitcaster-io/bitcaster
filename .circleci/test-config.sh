#!/usr/bin/env bash
#ARG=$1
#TAG=${ARG:=1.0a}
#    --form build_parameters[CIRCLE_JOB]=tag \
#    --form build_parameters[RELEASE_MATCH]="release/*" \
#    --form build_parameters[TAG]=$TAG \
BRANCH=release%2F1.0a
JOB=tag
TAG=1.0a

curl --user ${CIRCLE_TOKEN} \
    --request POST \
    --form config=@config.yml \
    --form build_parameters[CIRCLE_JOB]=$JOB \
    --form build_parameters[TAG]=$TAG \
    --form notify=false \
        https://circleci.com/api/v1.1/project/github/unicef/sir-poc/tree/$BRANCH
