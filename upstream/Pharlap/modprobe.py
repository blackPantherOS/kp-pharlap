import os
import pprint
import re



class modprobe():


  def __init__(self):
    self._config = {}

  def blacklist(self, module, state=True):
    m = module(module)
    m['blacklisted'] = state

  def module(self, module):
    return self._config.setdefault(module, {
      'alias': None,
      'blacklisted': False,
      'options': set()
    })

  def options(self, module, option=None):
    if option is not None:
      m = self.module(module)

      m['options'].append(option)

  def parse(self, base='/etc/modprobe.d'):
    for root, dirs, files in os.walk(base):
      for f in files:
        self.parseFile(os.path.join(root,f))

  def parseFile(self, path):
    with open(path, 'r') as f:
      for l in f:
        e = l.strip().split()

        if len(e) < 2:
          continue

        # check for alias
        if e[0] == 'alias':
          m = self.module(e[2])
          m['alias'] = e[1]

        # check for blacklist
        elif e[0] == 'blacklist':
          m = self.module(e[1])
          m['blacklisted'] = True

        # check for options (quirks)
        elif e[0] == 'options':
          m = self.module(e[1])
          m['options'].update(e[2:])

  def writeToFile(self, path='/etc/modprobe.d/pharlap.conf'):
    try:
      with open(path, 'w') as f:
        header = "# this file is automatically generated by Pharlap\n" \
                 "# any manual changes will likely be lost"
        f.write(header.encode('utf-8'))

        for k in sorted(self._config):
          m = self.module(k)

          options = m.get('options', [])

          if len(options):
            l = 'options %s %s\n' % (k, ' '.join(options))
            f.write(l.encode('utf-8'))

          blacklist = m.get('blacklisted', False)
          if blacklist:
            l = 'blacklist %s\n' % (k)
            f.write(l.encode('utf-8'))

    except:
      raise Exception('Unable to write to file: %s' % (path))


  def getConfig(self):
    c = self._config.copy()

    for k in c:
      m = c[k]
      if 'options' in m:
        m['options'] = ' '.join(m['options'])

    return c



if __name__ == '__main__':
  c = modprobe()
  c.parse()

  pp = pprint.PrettyPrinter(indent=2)
  pp.pprint(c.getConfig())

  c.writeToFile()

