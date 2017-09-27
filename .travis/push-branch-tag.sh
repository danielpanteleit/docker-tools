#!/usr/bin/env bash

set -e

if [[ -n "$TRAVIS_TAG" || -z "$TRAVIS_BRANCH" ]]; then
    echo "not pushing branch tag"
    exit
fi

echo tagging latest-$TRAVIS_BRANCH $TRAVIS_COMMIT
TAG=latest-$TRAVIS_BRANCH
git tag -f $TAG $TRAVIS_COMMIT

export GIT_SSH=".travis/ssh_wrapper.sh"
git push -f ssh://git@github.com/danielpanteleit/docker-tools $TAG

rm -f .travis/github_deploy_key

echo "done"
