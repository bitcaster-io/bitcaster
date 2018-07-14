#!/usr/bin/env bash

BRANCH=develop
JOB=build
TAG=1.0a
VERBOSE=0

help (){
    echo "./test-config.sh [-b/--branch BRANCH] [-j/--job JOB] [-t/--tag TAG] [-v/--verbose 1/2/3]"
    exit 1
}

#for key in "$@"
while [ "$1" != "" ]; do
case $1 in
    -b=*|--branch=*)
        BRANCH="${1#*=}"
        shift # past argument
        ;;
    -j=*|--job=*)
        JOB="${1#*=}"
        shift # past argument
        ;;
    -t=*|--tag=*)
        TAG="${key#*=}"
        shift # past argument
        ;;
    -v=*|--verbose=*)
        VERBOSE="${1#*=}"
        shift # past argument
        ;;
    -b|--branch)
        BRANCH="$2"
        shift # past argument
        shift # past value
        ;;
    -j|--job)
        JOB="$2"
        shift # past argument
        shift # past value
        ;;
    -t|--tag)
        TAG="$2"
        shift # past argument
        shift # past value
        ;;
    -v|--verbose)
        VERBOSE="$2"
        shift # past argument
        shift # past value
        ;;
    -h|--help)
            help
            ;;
    *) echo "unknown option '$1'"
       help
       ;;
esac
done

BRANCH="${BRANCH/\//%2F}"

if [ "$VERBOSE" -gt "0" ]; then
    echo "branch:  $BRANCH"
    echo "tag:     $TAG"
    echo "job:     $JOB"
    echo "verbose: $VERBOSE"
fi

curl --user ${CIRCLE_TOKEN} \
    --request POST \
    --form build_parameters[TAG]=$TAG \
    --form build_parameters[CIRCLE_JOB]=$JOB \
    --form config=@config.yml \
    --form notify=false \
        https://circleci.com/api/v1.1/project/github/unicef/sir-releases/tree/$BRANCH
