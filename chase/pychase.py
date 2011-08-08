# Main class for goose 'chase'
    
import os
import re
import cmd
import sys
import stat
import time
import shutil
import hashlib
import logging

# github api and token should be kept secret
#import github_settings as ghs
#from github2.client import Github

import koji

# some variables that are generally global

CLIENT_CERT="~/.koji/goose.cert"
CLIENT_CA_CERT="~/.koji/goose-client-ca.cert"
SERVER_CA_CERT="~/.koji/goose-server-ca.cert"
GOOSE_KOJI_SERVER="http://koji.gooselinux.org/kojihub"

class PyChase(cmd.Cmd):
    """
    Support class for chase. GoOSe Project reporting tool.
    """

    def __init__(self):
        self.session = koji.ClientSession(GOOSE_KOJI_SERVER, opts={'user': 'clints'})
        self.session.ssl_login(os.path.expanduser(CLIENT_CERT), os.path.expanduser(CLIENT_CA_CERT), os.path.expanduser(SERVER_CA_CERT))

    def do_buildinfo(self, args):

        tag = args.tag
        pkg_list = args.pkgs
        tag_id = None
        if tag:
            tag_id = self.session.search(tag, 'tag', 'glob')[0]['id']
#        print "tag: %s, tag_id: %s" % (tag, tag_id)

        pkgs = list()
        if pkg_list:
            for pkg in pkg_list:
                pkg_id = self.session.search(pkg, 'package', 'glob')[0]['id']
                pkgs.append(self.session.listPackages(pkgID=pkg_id, tagID=tag_id))

            pkgs = pkgs[0]

        else:
            pkgs = self.session.listPackages(tagID=tag_id)

        for p in pkgs:
#            print "name: %s" % p['package_name']
#            print "id: %d" % p['package_id']
            p_info = self.session.listBuilds(packageID=p['package_id'])
            for i in p_info:
                if i['release'].endswith('gl6'):
                    print i['nvr']
                    if i['state'] == 1:
                        print "succeeded"
                    else:
                        print "failed"
