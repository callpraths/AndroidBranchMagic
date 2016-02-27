#!/usr/bin/python

import logging
import os
import os.path
import xml.etree.ElementTree as ET
from collections import namedtuple

Project = namedtuple('Project', ['name', 'path', 'revision'])

class Manifest(object):
  def __init__(self, manifestPath):
    self._manifestPath = os.path.abspath(manifestPath)
    self._projects = {}

  def load(self):
    self._root = ET.parse(self._manifestPath)

    default = self._root.findall('default')
    assert len(default) == 1
    dRevision = default[0].attrib.get('revision')

    for project in self._root.iter('project'):
      attribs = project.attrib
      if 'name' not in attribs:
        logging.warning('Project without a name?: ' + str(attribs))
        continue

      self._projects[attribs['name']] = Project(attribs['name'],
                                                attribs.get('path'),
                                                attribs.get('revision',
                                                            dRevision))

  @property
  def projects(self):
    return self._projects

  def __str__(self):
    ret = 'Manifest:\n'
    ret += 'Filepath: ' + self._manifestPath + '\n'
    ret += 'Projects:\n'
    for name, project in self._projects.iteritems():
      ret += name + ': ' + str(project) + '\n'
    return ret


def ForEachProject(manifest, repoRoot, func,
                   stopOnError=True):
  """
  Calls |func| with cwd set to each path where manifest specifies the
  projects to walk under the repoRoot.

  Args:
    manifest: A |Manifest| object.
    repoRoot: Path to the root of the repo.
    func: The function to call. func should take a single argument -- the name
        of the project.
  """
  repoRoot = os.path.abspath(repoRoot)
  baseDir = os.path.abspath(os.getcwd())
  failed = False
  for _, (name, path, _) in manifest.projects.iteritems():
    fullpath = os.path.normpath(os.path.join(repoRoot, path))
    logging.info('Entering project ' + name + ' at path ' + fullpath)
    try:
      os.chdir(fullpath)
      func(name)
    except Exception as e:
      logging.error('Error in project ' + name)
      logging.error(str(e))
      if stopOnError:
        failed = True
        break
      else:
        continue

    logging.info('Successfully procesed project ' + name)

  if failed:
    logging.warning('Finished with errors')
  else:
    logging.info('All done')
  os.chdir(baseDir)


def main(argv):
  logging.basicConfig(level=logging.INFO)
  if len(argv) != 2:
    logging.error('Usage: ' + argv[0] + ' <path to manifest file>')
    return 1

  m = Manifest(argv[1])
  m.load()
  logging.info(m)
  return 0


if __name__ == '__main__':
  import sys
  main(sys.argv)
