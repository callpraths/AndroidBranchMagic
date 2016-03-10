#!/usr/bin/python

import argparse
import logging
import os
import os.path
import subprocess

import Manifest

def PrintName(name):
  logging.info('Walked ' + name)

scriptPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'cp_candidates.sh')
def CpCandidate(remote, fromBranch, toBranch, projects, restArgs, name):
  if (not projects) or name in projects:
    subprocess.call([scriptPath, remote, fromBranch, toBranch] + restArgs)


def main(argv):
  logging.basicConfig(level=logging.INFO)
  parser = argparse.ArgumentParser(description='Find out what is missing.')
  parser.add_argument('repo_root', metavar='repo-root',
                      help='Path to the of your repo checkout.')
  parser.add_argument('from_branch', metavar='from-branch',
                      help='Name of the branch you want to cp from.')
  parser.add_argument('to_branch', metavar='to-branch',
                      help='Name of the branch you want to cp to.')
  parser.add_argument('--project', default=[], action='append',
                      help='Restrict to project. By default, all projects are '
                           'scanned. Use multiple times to list more than one '
                           'project.')

  parser.add_argument('--remote', default='goog',
                      help='Name of the git remote. default: goog')
  parser.add_argument('--log-filter', default='',
                      help='Extra arguments to filter git-log')

  opts = parser.parse_args(argv[1:])

  manifestFile = os.path.join(opts.repo_root, '.repo', 'manifest.xml')
  manifest = Manifest.Manifest(manifestFile)
  manifest.load()

  Manifest.ForEachProject(manifest, opts.repo_root,
                          lambda x: CpCandidate(opts.remote,
                                                opts.from_branch,
                                                opts.to_branch,
                                                set(opts.project),
                                                opts.log_filter.split(),
                                                x),
                          stopOnError=False)
  return 0


if __name__ == '__main__':
  import sys
  main(sys.argv)
