#!/bin/bash

MAX_NUM_PROCS=16

remote="$1"
shift
from_branch="${remote}/$1"
shift
to_branch="${remote}/$1"
shift
git_args="$@"

function errecho () {
  >&2 echo "$@"
}
export -f errecho

function check_candidate() {
  local -r from_branch="$1"
  local -r to_branch="$2"
  local -r candidate="$3"
  errecho Processing "${candidate}..."
  if ! [[ $(git log --grep "${candidate}" "${to_branch}") ]]; then
    echo "$(git log -1 --grep "${candidate}" "${from_branch}")"
  fi
}
export -f check_candidate

errecho First looking for candidates
candidates="$(git log ${git_args[@]} --cherry "${to_branch}".."${from_branch}" \
  | grep 'Change-Id:' | awk '{ print $2 }')"

if [[ "${candidates}" == "" ]]; then
  errecho "No candidates found"
  exit 0
fi

errecho Found candidates: "${candidates}"
for candidate in ${candidates[@]}; do
  printf "%s\0%s\0%s\0" "${from_branch}" "${to_branch}" "${candidate}"
done | xargs -0 -x -n 3 -P "${MAX_NUM_PROCS}" \
  bash -c 'check_candidate "$@"' --
