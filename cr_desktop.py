'''cr_desktop.py: click desktop checks'''
#
# Copyright (C) 2013 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

from cr_common import ClickReview, error, open_file_read
import os
from xdg.DesktopEntry import DesktopEntry
from xdg.Exceptions import ParsingError as xdgParsingError

class ClickReviewDesktop(ClickReview):
    '''This class represents click lint reviews'''
    def __init__(self, fn):
        ClickReview.__init__(self, fn, "desktop")

        self.desktop_files = dict()
        self.desktop_entries = dict()
        self.desktop_hook_entries = 0
        for app in self.manifest['hooks']:
            if 'desktop' not in self.manifest['hooks'][app]:
                error("could not find desktop hook for '%s'" % app)
            if not isinstance(self.manifest['hooks'][app]['desktop'], str):
                error("manifest malformed: hooks/%s/desktop is not str" % app)
            self.desktop_hook_entries += 1
            d = self.manifest['hooks'][app]['desktop']
            full_fn = os.path.join(self.unpack_dir, d)
            if os.path.exists(full_fn):
                self.desktop_entries[app] = self._get_desktop_entry(full_fn)
                self.desktop_files[app] = full_fn

        self.required_keys = ['Name',
                              'Type',
                              'Icon',
                              'Exec',
                              'X-Ubuntu-Touch']
        self.expected_execs = ['qmlscene',
                               'webbrowser-app',
                               'cordova-ubuntu-2.8'
                              ]
        self.expected_webbrowser_args = ['--enable-back-forward',
                                         '--webapp',
                                         '--webappUrlPatterns=*'
                                        ]
        self.blacklisted_keys = ['Path']

        self.valid_gettext_domains = [self.click_pkgname]
        if self.click_pkgname.split('.')[-1] not in self.valid_gettext_domains:
            self.valid_gettext_domains.append(self.click_pkgname.split('.')[-1])

    def _get_desktop_entry(self, fn):
        '''Get DesktopEntry for desktop file and verify it'''
        bn = os.path.basename(fn)
        if not os.path.exists(fn):
            error("Could not find '%s'" % bn)

        fh = open_file_read(fn)
        contents = ""
        for line in fh.readlines():
            contents += line
        fh.close()

        try:
            de = DesktopEntry(fn)
        except xdgParsingError as e:
            error("desktop file unparseable: %s (%s):\n%s" % (bn, str(e),
                                                              contents))
        try:
            de.parse(fn)
        except Exception as e:
            error("desktop file unparseable: %s (%s):\n%s" % (bn, str(e),
                                                              contents))
        return de

    def check_desktop_file(self):
        '''Check desktop file'''
        t = 'info'
        n = 'files_available'
        s = 'OK'
        if len(self.desktop_files.keys()) < 1:
            t = 'error'
            s = 'No .desktop files available.'
        self._add_result(t, n, s)

        t = 'info'
        n = 'files_usable'
        s = 'OK'
        if len(self.desktop_files.keys()) != self.desktop_hook_entries:
            t = 'error'
            s = 'Could not use all specified .desktop files'
        self._add_result(t, n, s)

    def check_desktop_file_valid(self):
        '''Check desktop file validates'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'validates (%s)' % app
            s = 'OK'
            try:
                de.validate()
            except Exception as e:
                t = 'error'
                s = 'did not validate: (%s)' % str(e)
            self._add_result(t, n, s)

    def check_desktop_required_keys(self):
        '''Check for required keys'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'required_keys (%s)' % app
            s = "OK"
            missing = []
            for f in self.required_keys:
                if not de.hasKey(f):
                    missing.append(f)
            if len(missing) > 0:
                t = 'error'
                s = 'missing required keys: %s' % ",".join(missing)
            self._add_result(t, n, s)

            t = 'info'
            n = 'required_fields_not_empty (%s)' % app
            s = "OK"
            empty = []
            for f in self.required_keys:
                if de.hasKey(f) and de.get(f) == "":
                    empty.append(f)
            if len(empty) > 0:
                t = 'error'
                s = 'Empty required keys: %s' % ",".join(empty)
            self._add_result(t, n, s)

    def check_desktop_blacklisted_keys(self):
        '''Check for blacklisted keys'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'blacklisted_keys (%s)' % app
            s = "OK"
            found = []
            for f in self.blacklisted_keys:
                if de.hasKey(f):
                    found.append(f)
            if len(found) > 0:
                t = 'error'
                s = 'found blacklisted keys: %s' % ",".join(found)
            self._add_result(t, n, s)

    def check_desktop_exec(self):
        '''Check Exec entry'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'Exec (%s)' % app
            s = 'OK'
            if not de.hasKey('Exec'):
                t = 'error'
                s = "missing key 'Exec'"
            elif de.getExec().startswith('/'):
                t = 'error'
                s = "absolute path '%s' for Exec given in .desktop file." \
                        % de.getExec()
            elif de.getExec().split()[0] not in self.expected_execs:
                if self.click_arch == "all": # interpreted file
                    s = "found unexpected Exec with architecture '%s': %s" % (self.click_arch, de.getExec().split()[0])
                    t = 'warn'
                else:                        # compiled
                    # TODO: this can be a lot smarter
                    s = "Non-standard Exec with architecture '%s': %s (ok for compiled code)" % (self.click_arch, de.getExec().split()[0])
                    t = 'info'
            self._add_result(t, n, s)

    def check_desktop_exec_webbrowser(self):
        '''Check Exec=webbrowser-app entry'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'Exec_webbrowser (%s)' % app
            s = 'OK'
            if not de.hasKey('Exec'):
                t = 'error'
                s = "missing key 'Exec'"
                self._add_result(t, n, s)
                continue
            elif de.getExec().split()[0] != "webbrowser-app":
                s = "SKIPPED (not webbrowser-app)"
                self._add_result(t, n, s)
                continue

            for arg in self.expected_webbrowser_args:
                t = 'info'
                n = 'Exec_webbrowser %s (%s)' % (arg, app)
                s = 'OK'
                if arg.endswith('*'):
                    found = False
                    for i in de.getExec().split():
                        if i.startswith(arg.rstrip('*')):
                            found = True
                    if not found:
                        t = 'error'
                        s = "could not find '%s' in  '%s'" % (arg, de.getExec())
                elif arg not in de.getExec().split():
                    t = 'error'
                    s = "could not find '%s' in  '%s'" % (arg, de.getExec())
                self._add_result(t, n, s)

    def check_desktop_groups(self):
        '''Check Desktop Entry entry'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'groups (%s)' % app
            s = "OK"
            if len(de.groups()) != 1:
                t = 'error'
                s = 'too many desktop groups'
            elif "Desktop Entry" not in de.groups():
                t = 'error'
                s = "'[Desktop Entry]' group not found"
            self._add_result(t, n, s)

    def check_desktop_type(self):
        '''Check Type entry'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'Type (%s)' % app
            s = "OK"
            if not de.hasKey('Type'):
                t = 'error'
                s = "missing key 'Type'"
            elif de.getType() != "Application":
                t = 'error'
                s = 'does not use Type=Application'
            self._add_result(t, n, s)

    def check_desktop_x_ubuntu_touch(self):
        '''Check X-Ubuntu-Touch entry'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'X-Ubuntu-Touch (%s)' % app
            s = "OK"
            if not de.hasKey('X-Ubuntu-Touch'):
                t = 'error'
                s = "missing key 'X-Ubuntu-Touch'"
            elif de.get("X-Ubuntu-Touch") != "true" and \
                 de.get("X-Ubuntu-Touch") != "True":
                t = 'error'
                s = 'does not use X-Ubuntu-Touch=true'
            self._add_result(t, n, s)

    def check_desktop_x_ubuntu_stagehint(self):
        '''Check X-Ubuntu-StageHint entry'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'X-Ubuntu-StageHint (%s)' % app
            s = "OK"
            if not de.hasKey('X-Ubuntu-StageHint'):
                t = 'info'
                s = "OK (not specified)"
            elif de.get("X-Ubuntu-StageHint") != "SideStage":
                t = 'error'
                s = "unsupported X-Ubuntu-StageHint=%s (should be for example, 'SideStage')" % \
                    de.get("X-Ubuntu-StageHint")
            self._add_result(t, n, s)

    def check_desktop_x_ubuntu_gettext_domain(self):
        '''Check X-Ubuntu-Gettext-Domain entry'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'X-Ubuntu-Gettext-Domain (%s)' % app
            s = "OK"
            if not de.hasKey('X-Ubuntu-Gettext-Domain'):
                t = 'info'
                s = "OK (not specified)"
            elif de.get("X-Ubuntu-Gettext-Domain") not in \
                 self.valid_gettext_domains:
                t = 'warn'
                s = "unexpected X-Ubuntu-Gettext-Domain=%s (expected: %s)" % \
                    (de.get("X-Ubuntu-Gettext-Domain"),
                    ",".join(self.valid_gettext_domains))
            self._add_result(t, n, s)

    def check_desktop_terminal(self):
        '''Check Terminal entry'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'Terminal (%s)' % app
            s = "OK"
            if not de.hasKey('Terminal'):
                s = "OK (not specified)"
            elif de.getTerminal() != False:
                t = 'error'
                s = 'does not use Terminal=false (%s)' % de.getTerminal()
            self._add_result(t, n, s)

    def check_desktop_version(self):
        '''Check Version entry'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'Version (%s)' % app
            s = "OK"
            if not de.hasKey('Version'):
                s = "OK (not specified)"
            elif de.getVersionString() != "1.0":
                # http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html#entries
                t = 'error'
                s = "'%s' does not match freedesktop.org version '1.0'" % \
                    de.getVersionString()
            self._add_result(t, n, s)

    def check_desktop_comment(self):
        '''Check Comment entry'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'Comment_boilerplate (%s)' % app
            s = "OK"
            if de.hasKey('Comment') and de.getComment() == "My project description":
                t = 'warn'
                s = "Comment uses SDK boilerplate '%s'" % de.getComment()
            self._add_result(t, n, s)

    def check_desktop_icon(self):
        '''Check Icon entry'''
        for app in sorted(self.desktop_entries):
            de = self.desktop_entries[app]
            t = 'info'
            n = 'Icon (%s)' % app
            s = 'OK'
            if not de.hasKey('Icon'):
                t = 'error'
                s = "missing key 'Icon'"
            elif de.getIcon().startswith('/'):
                t = 'error'
                s = "absolute path '%s' for icon given in .desktop file." \
                        % de.getIcon()
            self._add_result(t, n, s)

    def check_desktop_duplicate_entries(self):
        '''Check desktop for duplicate entries'''
        for app in sorted(self.desktop_entries):
            found = []
            dupes = []
            t = 'info'
            n = 'duplicate_keys (%s)' % app
            s = 'OK'
            fn = self.desktop_files[app]
            content = open_file_read(fn).readlines()
            for line in content:
                tmp = line.split('=')
                if len(tmp) < 2:
                    continue
                if tmp[0] in found:
                    dupes.append(tmp[0])
                else:
                    found.append(tmp[0])
            if len(dupes) > 0:
                t = 'error'
                s = 'found duplicate keys: %s' % ",".join(dupes)
            self._add_result(t, n, s)
