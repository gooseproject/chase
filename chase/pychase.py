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
GL6_EXT=('gl6', 'gl6.1')

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
#        print "pkg_list: %s" % pkg_list

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
                pkg_ids = self.session.search(pkg, 'package', 'glob')
#                print "pkg_id: %s" % pkg_ids
                for pi in pkg_ids:
                    builds = self.session.listPackages(pkgID=pi['id'], tagID=tag_id)
#                print "pkgsX: %s" % pkgs
                    for b in builds:
#                    print 'pkgsY: %s' % b
                        pkgs.append(b)

#            print "pkgs B4: %s" % pkgs

        else:
            pkgs = self.session.listPackages(tagID=tag_id)

#            print "pkgs B4: %s" % pkgs

        passed = {}
        passed_count = 0
        failed = {}
        failed_count = 0
        unbuilt = {}
        unbuilt_count = 0

        for p in pkgs:
#            print "pkginfo: %s" % p
            p_info = self.session.listBuilds(packageID=p['package_id'])
#            print "p_info: %s" % p_info
            for i in p_info:
                if i['name'] not in passed and i['name'] not in failed and i['name'] not in unbuilt:
                    if i['release'].endswith(GL6_EXT):
                        if i['state'] == 1:
                            passed[i['name']] = i
                            passed_count += 1
                        else:
                            failed[i['name']] = i
                            failed_count += 1
                    else:
                        unbuilt[i['name']] = i
                        unbuilt_count += 1

        # report results
        print "=== Build Information Report ==="
        # print passed packages
        if show_passed:
            if passed_count:
                print
            for p in passed:
                print "   %s " % passed[p]['nvr'], "PASSED".rjust(80-len(passed[p]['nvr']))
        if show_failed:
            if failed_count:
                print
                for f in failed:
                    print "   %s " % failed[f]['nvr'], "FAILED".rjust(80-len(failed[f]['nvr']))
        if show_unbuilt:
            if unbuilt_count:
                print 
                for u in unbuilt:
                    print "   %s " % unbuilt[u]['nvr'], "NOT YET BUILT".rjust(80-len(unbuilt[u]['nvr']))

        print

        if show_passed:
            print " Total Passed: %d" % passed_count
        if show_failed:
            print " Total Failed: %d" % failed_count
        if show_unbuilt:
            print " Total Unbuilt: %d" % unbuilt_count

        print 




