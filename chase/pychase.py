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

        #set the initial values to false
        show_passed = False
        show_failed = False
        show_unbuilt = False

        # if nothing is set, show all results
        if not args.passed and not args.failed and not args.unbuilt:
            show_passed = True
            show_failed = True
            show_unbuilt = True

        # otherwise, show only the results *if* they are set 
        if args.passed: show_passed = True
        if args.failed: show_failed = True
        if args.unbuilt: show_unbuilt = True

        tag_id = self.session.search(tag, 'tag', 'glob')[0]['id']

        pkgs = list()
        if pkg_list:
            for pkg in pkg_list:
                pkg_id = self.session.search(pkg, 'package', 'glob')[0]['id']
                builds = self.session.listPackages(pkgID=pkg_id, tagID=tag_id)
#                print "pkgsX: %s" % pkgs
                for b in builds:
#                    print 'pkgsY: %s' % b
                    pkgs.append(b)

#            print "pkgs B4: %s" % pkgs

        else:
            pkgs = self.session.listPackages(tagID=tag_id)

#            print "pkgs B4: %s" % pkgs

        passed = []
        passed_count = 0
        failed = []
        failed_count = 0
        unbuilt = []
        unbuilt_count = 0

        for p in pkgs:
#            print "pkginfo: %s" % p
            p_info = self.session.listBuilds(packageID=p['package_id'])
#            print "p_info: %s" % p_info
            for i in p_info:
                if i['release'].endswith('gl6'):
                    if i['state'] == 1:
                        passed.append(i)
                        passed_count += 1
                    else:
                        failed.append(i)
                        failed_count += 1
                else:
                    unbuilt.append(i)
                    unbuilt_count += 1

        # report results
        print "=== Build Information Report ===\n"
        # print passed packages
        if show_passed:

            for p in passed:
                print "  %s\t\t\tPASSED" % p['nvr'] 
        if show_failed:
            pass
        if show_unbuilt:
            pass

        print "Total Passed: %d" % passed_count
        print " Total Failed: %d" % failed_count
        print " Total Unbuilt: %d" % unbuilt_count





