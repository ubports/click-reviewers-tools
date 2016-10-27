'''test_sr_declaration.py: tests for the sr_declaration module'''
#
# Copyright (C) 2014-2016 Canonical Ltd.
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

from clickreviews.sr_declaration import SnapReviewDeclaration, SnapDeclarationException
import clickreviews.sr_tests as sr_tests
import yaml


class TestSnapReviewDeclaration(sr_tests.TestSnapReview):
    """Tests for the lint review tool."""
    def _set_base_declaration(self, c, decl):
        # TODO: don't hardcode series
        c.base_declaration["16"] = decl

    def _use_test_base_declaration(self, c):
        # setup minimized, intended base declaration
        decl = yaml.safe_load('''
plugs:
  # super-privileged implicit
  docker-support: # snap decl needs 'allow-connection: ...'
    deny-connection: true
    deny-auto-connection: true
slots:
  # manually connected implicit
  bluetooth-control:
    allow-installation:
      slot-snap-type:
      - core
    deny-auto-connection: true
  docker-support: # snap decl needs 'allow-connection: ...'
    allow-installation:
      slot-snap-type:
      - core
    deny-connection: true
    deny-auto-connection: true
  # auto-connected implicit
  home:
    allow-installation:
      slot-snap-type:
      - core
    allow-auto-connection:
      on-classic: true
  content:
    allow-installation:
      slot-snap-type:
      - app
      - gadget
    allow-auto-connection:
      plug-publisher-id:
      - $SLOT_PUBLISHER_ID
  browser-support: # snap decl needs 'allow-connection: ... allow-sandbox: ...'
    allow-installation:
      slot-snap-type:
      - core
    deny-connection:
      plug-attributes:
        allow-sandbox: true
  network:
    allow-installation:
      slot-snap-type:
      - core
  # manually connecect app-provided
  bluez: # snap decl needs 'allow-connection: ...'
    allow-installation:
      slot-snap-type:
      - app
    deny-connection: true
    deny-auto-connection: true
  docker: # snap decl needs 'allow-installation/connection: ...'
    allow-installation: false
    deny-connection: true
    deny-auto-connection: true
  mpris: # snap decl needs 'allow-connection: ... name: ...'
    allow-installation:
      slot-snap-type:
      - app
    deny-connection:
      slot-attributes:
        name: .+
  mir: # snap decl needs 'allow-connection: ...'
    allow-installation:
      slot-snap-type:
      - app
    deny-connection: true
  serial-port: # snap decl needs 'allow-connection: ...'
    allow-installation:
      slot-snap-type:
      - core
      - gadget
    deny-connection: true
    deny-auto-connection: true
''')
        c._verify_declaration(decl=decl, base=True)

        self._set_base_declaration(c, decl)

    def test_all_checks_as_v2(self):
        '''Test snap v2 has checks'''
        self.set_test_pkgfmt("snap", "16.04")
        c = SnapReviewDeclaration(self.test_name)
        c.do_checks()
        sum = 0
        for i in c.click_report:
            sum += len(c.click_report[i])
        self.assertTrue(sum == 0)

    def test_all_checks_as_v1(self):
        '''Test snap v1 has no checks'''
        self.set_test_pkgfmt("snap", "15.04")
        c = SnapReviewDeclaration(self.test_name)
        c.do_checks()
        sum = 0
        for i in c.click_report:
            sum += len(c.click_report[i])
        self.assertTrue(sum == 0)

    def test_all_checks_as_click(self):
        '''Test click format has no checks'''
        self.set_test_pkgfmt("click", "0.4")
        c = SnapReviewDeclaration(self.test_name)
        c.do_checks()
        sum = 0
        for i in c.click_report:
            sum += len(c.click_report[i])
        self.assertTrue(sum == 0)

    def test__verify_declaration_valid(self):
        '''Test _verify_declaration - valid'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'inst-on-classic-true': {
                    'allow-installation': {
                        'on-classic': True
                    },
                },
                'inst-on-classic-false': {
                    'deny-installation': {
                        'on-classic': False
                    },
                },
                'inst-slot-snap-type-all': {
                    'allow-installation': {
                        'slot-snap-type': ['core', 'gadget', 'kernel', 'app']
                    },
                },
                'inst-slot-snap-type-app': {
                    'deny-installation': {
                        'slot-snap-type': ['app']
                    },
                },
                'inst-slot-attributes-empty': {
                    'allow-installation': {
                        'slot-attributes': {},
                    },
                },
                'conn-on-classic-true': {
                    'allow-connection': {
                        'on-classic': True
                    },
                },
                'conn-on-classic-false': {
                    'deny-connection': {
                        'on-classic': False
                    },
                },
                'conn-plug-snap-type-all': {
                    'allow-connection': {
                        'plug-snap-type': ['core', 'gadget', 'kernel', 'app']
                    },
                },
                'conn-plug-snap-type-core': {
                    'deny-connection': {
                        'plug-snap-type': ['core']
                    },
                },
                'conn-plug-snap-id-allow': {
                    'allow-connection': {
                        'plug-snap-id': ['something32charslongGgGgGgGgGgGg']
                    },
                },
                'conn-plug-snap-id-deny': {
                    'deny-connection': {
                        'plug-snap-id': ['somethingelse32charslongGgGgGgGg']
                    },
                },
                'conn-plug-publisher-id-allow': {
                    'allow-connection': {
                        'plug-publisher-id': ['$SLOT_PUBLISHER_ID',
                                              'canonical']
                    },
                },
                'conn-plug-publisher-id-deny': {
                    'deny-connection': {
                        'plug-publisher-id': ['badpublisher']
                    },
                },
                'conn-slot-attributes-empty': {
                    'allow-connection': {
                        'slot-attributes': {},
                    },
                },
                'conn-plug-attributes-empty': {
                    'deny-connection': {
                        'plug-attributes': {},
                    },
                },
                'autoconn-on-classic-true': {
                    'allow-connection': {
                        'on-classic': True
                    },
                },
                'autoconn-on-classic-false': {
                    'deny-connection': {
                        'on-classic': False
                    },
                },
                'autoconn-plug-snap-type-all': {
                    'allow-connection': {
                        'plug-snap-type': ['core', 'gadget', 'kernel', 'app']
                    },
                },
                'autoconn-plug-snap-type-core': {
                    'deny-connection': {
                        'plug-snap-type': ['core']
                    },
                },
                'autoconn-plug-snap-id-allow': {
                    'allow-connection': {
                        'plug-snap-id': ['something32charslongGgGgGgGgGgGg']
                    },
                },
                'autoconn-plug-snap-id-deny': {
                    'deny-connection': {
                        'plug-snap-id': ['somethingelse32charslongGgGgGgGg']
                    },
                },
                'autoconn-plug-publisher-id-allow': {
                    'allow-connection': {
                        'plug-publisher-id': ['$SLOT_PUBLISHER_ID',
                                              'canonical']
                    },
                },
                'autoconn-plug-publisher-id-deny': {
                    'deny-connection': {
                        'plug-publisher-id': ['badpublisher']
                    },
                },
                'autoconn-slot-attributes-empty': {
                    'allow-connection': {
                        'slot-attributes': {},
                    },
                },
                'autoconn-plug-attributes-empty': {
                    'deny-connection': {
                        'plug-attributes': {},
                    },
                },
            },
            'plugs': {
                'inst-on-classic-true': {
                    'allow-installation': {
                        'on-classic': True
                    },
                },
                'inst-on-classic-false': {
                    'deny-installation': {
                        'on-classic': False
                    },
                },
                'inst-plug-snap-type-all': {
                    'allow-installation': {
                        'plug-snap-type': ['core', 'gadget', 'kernel', 'app']
                    },
                },
                'inst-plug-snap-type-app': {
                    'deny-installation': {
                        'plug-snap-type': ['app']
                    },
                },
                'inst-plug-attributes-empty': {
                    'allow-installation': {
                        'plug-attributes': {},
                    },
                },
                'conn-on-classic-true': {
                    'allow-connection': {
                        'on-classic': True
                    },
                },
                'conn-on-classic-false': {
                    'deny-connection': {
                        'on-classic': False
                    },
                },
                'conn-slot-snap-type-all': {
                    'allow-connection': {
                        'slot-snap-type': ['core', 'gadget', 'kernel', 'app']
                    },
                },
                'conn-slot-snap-type-core': {
                    'deny-connection': {
                        'slot-snap-type': ['core']
                    },
                },
                'conn-slot-snap-id-allow': {
                    'allow-connection': {
                        'slot-snap-id': ['something32charslongGgGgGgGgGgGg']
                    },
                },
                'conn-slot-snap-id-deny': {
                    'deny-connection': {
                        'slot-snap-id': ['somethingelse32charslongGgGgGgGg']
                    },
                },
                'conn-slot-publisher-id-allow': {
                    'allow-connection': {
                        'slot-publisher-id': ['$PLUG_PUBLISHER_ID',
                                              'canonical']
                    },
                },
                'conn-slot-publisher-id-deny': {
                    'deny-connection': {
                        'slot-publisher-id': ['badpublisher']
                    },
                },
                'conn-plug-attributes-empty': {
                    'allow-connection': {
                        'plug-attributes': {},
                    },
                },
                'conn-slot-attributes-empty': {
                    'deny-connection': {
                        'slot-attributes': {},
                    },
                },
                'autoconn-on-classic-true': {
                    'allow-connection': {
                        'on-classic': True
                    },
                },
                'autoconn-on-classic-false': {
                    'deny-connection': {
                        'on-classic': False
                    },
                },
                'autoconn-slot-snap-type-all': {
                    'allow-connection': {
                        'slot-snap-type': ['core', 'gadget', 'kernel', 'app']
                    },
                },
                'autoconn-slot-snap-type-core': {
                    'deny-connection': {
                        'slot-snap-type': ['core']
                    },
                },
                'autoconn-slot-snap-id-allow': {
                    'allow-connection': {
                        'slot-snap-id': ['something32charslongGgGgGgGgGgGg']
                    },
                },
                'autoconn-slot-snap-id-deny': {
                    'deny-connection': {
                        'slot-snap-id': ['somethingelse32charslongGgGgGgGg']
                    },
                },
                'autoconn-slot-publisher-id-allow': {
                    'allow-connection': {
                        'slot-publisher-id': ['$PLUG_PUBLISHER_ID',
                                              'canonical']
                    },
                },
                'autoconn-slot-publisher-id-deny': {
                    'deny-connection': {
                        'slot-publisher-id': ['badpublisher']
                    },
                },
                'autoconn-plug-attributes-empty': {
                    'allow-connection': {
                        'plug-attributes': {},
                    },
                },
                'autoconn-slot-attributes-empty': {
                    'deny-connection': {
                        'slot-attributes': {},
                    },
                },
            },
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 50, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test__verify_declaration_invalid_empty(self):
        '''Test _verify_declaration - empty'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_dict'
        expected['error'][name] = {"text": "declaration malformed (empty)"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_empty_base(self):
        '''Test _verify_declaration - empty'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {}

        try:
            c._verify_declaration(decl=decl, base=True)
        except SnapDeclarationException:
            return
        raise Exception("base declaration should be invalid")

    def test__verify_declaration_invalid_type(self):
        '''Test _verify_declaration - bad type (list)'''
        c = SnapReviewDeclaration(self.test_name)
        decl = []
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_dict'
        expected['error'][name] = {"text": "declaration malformed (not a dict)"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_true(self):
        '''Test _verify_declaration - invalid slots - true'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'slots': True}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_dict:slots'
        expected['error'][name] = {"text": "declaration malformed (not a dict)"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_plugs_false(self):
        '''Test _verify_declaration - invalid plugs - false'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'plugs': False}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_dict:plugs'
        expected['error'][name] = {"text": "declaration malformed (not a dict)"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_bad_key(self):
        '''Test _verify_declaration - bad key'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'non-existent': {'foo': True}}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_key'
        expected['error'][name] = {"text": "declaration malformed (unknown key 'non-existent')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_slots_iface_bool(self):
        '''Test _verify_declaration - interface: boolean (slots)'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'slots': {'foo': True}}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_plugs_iface_bool(self):
        '''Test _verify_declaration - interface: boolean (plugs)'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'plugs': {'foo': True}}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_plugs:foo'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_iface_type(self):
        '''Test _verify_declaration - invalid interface: list'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'slots': {'foo': []}}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots_dict:foo'
        expected['error'][name] = {
            "text": "declaration malformed (interface not True, False or dict)"
        }
        self.check_results(r, expected=expected)

    def test__verify_declaration_slots_iface_constraint_bool(self):
        '''Test _verify_declaration - interface constraint: boolean (slots)'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'slots': {'foo': {'allow-installation': True}}}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-installation'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_plugs_iface_constraint_bool(self):
        '''Test _verify_declaration - interface constraint: boolean (plugs)'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'plugs': {'foo': {'deny-installation': True}}}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_plugs:foo:deny-installation'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_iface_constraint_list(self):
        '''Test _verify_declaration - invalid interface constraint: list
           (slots)'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'slots': {'foo': {'allow-installation': []}}}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-installation'
        expected['error'][name] = {"text": "declaration malformed (allow-installation not True, False or dict)"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_iface_constraint_unknown(self):
        '''Test _verify_declaration - invalid interface constraint: unknown
           (slots with allow-installation)'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'slots': {'foo': {'nonexistent': True}}}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:nonexistent'
        expected['error'][name] = {"text": "declaration malformed (unknown constraint 'nonexistent')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_iface_constraint_key_unknown(self):
        '''Test _verify_declaration - invalid interface constraint key: unknown
           (slots with allow-installation)'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'foo': {
                    'allow-installation': {
                        'nonexistent': True,
                        'nonexistent2': False
                    },
                },
            },
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 2}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-installation_nonexistent'
        expected['error'][name] = {"text": "declaration malformed (unknown constraint key 'nonexistent')"}
        name2 = 'declaration-snap-v2:valid_slots:foo:allow-installation_nonexistent2'
        expected['error'][name2] = {"text": "declaration malformed (unknown constraint key 'nonexistent2')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_iface_constraint_list2(self):
        '''Test _verify_declaration - invalid interface constraint: list
           (slots with allow-connection)'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'slots': {'foo': {'allow-connection': []}}}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-connection'
        expected['error'][name] = {"text": "declaration malformed (allow-connection not True, False or dict)"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_iface_constraint_key_unknown2(self):
        '''Test _verify_declaration - invalid interface constraint key: unknown
           (slots with deny-auto-connection)'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'foo': {
                    'deny-auto-connection': {
                        'nonexistent': True,
                        'nonexistent2': False
                    },
                },
            },
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 2}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:deny-auto-connection_nonexistent'
        expected['error'][name] = {"text": "declaration malformed (unknown constraint key 'nonexistent')"}
        name2 = 'declaration-snap-v2:valid_slots:foo:deny-auto-connection_nonexistent2'
        expected['error'][name2] = {"text": "declaration malformed (unknown constraint key 'nonexistent2')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_iface_constraint_bool(self):
        '''Test _verify_declaration - invalid interface constraint bool'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'slots': {'foo': {'allow-installation': {'on-classic': []}}}}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-installation_on-classic'
        expected['error'][name] = {"text": "declaration malformed ('on-classic' not True or False)"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_iface_constraint_str(self):
        '''Test _verify_declaration - invalid interface constraint str'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {'slots': {'foo': {'allow-installation': {'plug-snap-id': ""}}}}
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-installation_plug-snap-id'
        expected['error'][name] = {"text": "declaration malformed ('plug-snap-id' not a list)"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_iface_constraint_list_value(self):
        '''Test _verify_declaration - invalid interface constraint list
           value'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'foo': {
                    'allow-installation': {
                        'plug-snap-id': [{}]
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-installation_plug-snap-id'
        expected['error'][name] = {"text": "declaration malformed ('{}' in 'plug-snap-id' not a string)"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_iface_constraint_dict(self):
        '''Test _verify_declaration - invalid interface constraint dict'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'foo': {
                    'allow-connection': {
                        'plug-attributes': []
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-connection_plug-attributes'
        expected['error'][name] = {"text": "declaration malformed ('plug-attributes' not a dict)"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_valid_slots_plug_attribs_browser_support(self):
        '''Test _verify_declaration - valid interface constraint attrib
           value for browser-support
        '''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'browser-support': {
                    'allow-connection': {
                        'plug-attributes': {
                            'allow-sandbox': True
                        }
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:browser-support:allow-connection'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_plug_attribs_browser_support_bad(self):
        '''Test _verify_declaration - invalid interface constraint attrib
           value'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'browser-support': {
                    'allow-connection': {
                        'plug-attributes': {
                            'allow-sandbox': []
                        }
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:browser-support:allow-connection_plug-attributes'
        expected['error'][name] = {"text": "declaration malformed (wrong type '[]' for attribute 'allow-sandbox')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_plug_attribs_browser_support_nonexistent(self):
        '''Test _verify_declaration - invalid interface constraint attrib
           nonexistent'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'something': {
                    'allow-connection': {
                        'plug-attributes': {
                            'nonexistent': []
                        }
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:something:allow-connection_plug-attributes'
        expected['error'][name] = {"text": "declaration malformed (unknown attribute 'nonexistent')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_valid_slots_plug_attribs_content(self):
        '''Test _verify_declaration - valid interface constraint attrib
           for content'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'content': {
                    'allow-connection': {
                        'slot-attributes': {
                            'read': ["/foo"],
                            'write': ["/bar"]
                        },
                        'plug-attributes': {
                            'target': "/target",
                            'content': "baz"
                        },
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()

        name = 'declaration-snap-v2:valid_slots:content:allow-connection'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_plug_attribs_content_value(self):
        '''Test _verify_declaration - invalid interface constraint attrib
           value for content'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'content': {
                    'allow-connection': {
                        'slot-attributes': {
                            'read': ""
                        }
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:content:allow-connection_slot-attributes'
        expected['error'][name] = {"text": "declaration malformed (wrong type '' for attribute 'read')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_plug_attribs_content_side(self):
        '''Test _verify_declaration - invalid interface constraint attrib
           side for content'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'content': {
                    'allow-connection': {
                        'slot-attributes': {
                            'target': ""
                        }
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:content:allow-connection_slot-attributes'
        expected['error'][name] = {"text": "declaration malformed (attribute 'target' wrong for 'slots')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_plug_snap_type(self):
        '''Test _verify_declaration - invalid plug-snap-type'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'foo': {
                    'allow-connection': {
                        'plug-snap-type': ['bad-snap-type']
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-connection'
        expected['error'][name] = {"text": "declaration malformed (invalid snap type 'bad-snap-type')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_plugs_slot_snap_type(self):
        '''Test _verify_declaration - invalid slot-snap-type'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'plugs': {
                'foo': {
                    'allow-connection': {
                        'slot-snap-type': ['bad-snap-type']
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_plugs:foo:allow-connection'
        expected['error'][name] = {"text": "declaration malformed (invalid snap type 'bad-snap-type')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_plugs_slot_publisher_id(self):
        '''Test _verify_declaration - invalid slot-publisher-id'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'plugs': {
                'foo': {
                    'allow-connection': {
                        'slot-publisher-id': ['$SLOT_PUBLISHER_ID']
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_plugs:foo:allow-connection'
        expected['error'][name] = {"text": "declaration malformed (invalid publisher id '$SLOT_PUBLISHER_ID')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_plug_publisher_id(self):
        '''Test _verify_declaration - invalid plug-publisher-id'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'foo': {
                    'allow-connection': {
                        'plug-publisher-id': ['$PLUG_PUBLISHER_ID']
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-connection'
        expected['error'][name] = {"text": "declaration malformed (invalid publisher id '$PLUG_PUBLISHER_ID')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_plug_publisher_id_value(self):
        '''Test _verify_declaration - invalid plug-publisher-id'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'foo': {
                    'allow-connection': {
                        'plug-publisher-id': ['b@d']
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-connection'
        expected['error'][name] = {"text": "declaration malformed (invalid format for publisher id 'b@d')"}
        self.check_results(r, expected=expected)

    def test__verify_declaration_invalid_slots_plug_snap_id(self):
        '''Test _verify_declaration - invalid plug-snap-id'''
        c = SnapReviewDeclaration(self.test_name)
        decl = {
            'slots': {
                'foo': {
                    'allow-connection': {
                        'plug-snap-id': ['b@d']
                    }
                }
            }
        }
        c._verify_declaration(decl=decl)
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:valid_slots:foo:allow-connection'
        expected['error'][name] = {"text": "declaration malformed (invalid format for snap id 'b@d')"}
        self.check_results(r, expected=expected)

    def test_check_declaration_unknown_interface(self):
        '''Test check_declaration - unknown interface'''
        slots = {'iface-foo': {'interface': 'bar'}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'deny-installation': False
                }
            },
            'plugs': {}
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slot_known:iface-foo:bar'
        expected['error'][name] = {"text": "interface 'bar' not found in base declaration"}
        self.check_results(r, expected=expected)

    def test_check_declaration_unknown_interface_app(self):
        '''Test check_declaration - unknown interface - app'''
        apps = {'app1': {'slots': ['bar']}}
        self.set_test_snap_yaml("apps", apps)

        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'deny-installation': False
                }
            },
            'plugs': {}
        }
        self._set_base_declaration(c, base)
        c.check_declaration_apps()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:app_slot_known:app1:bar'
        expected['error'][name] = {"text": "interface 'bar' not found in base declaration"}
        self.check_results(r, expected=expected)

    def test_check_declaration_interface_app_bad_ref(self):
        '''Test check_declaration - interface - app - bad ref'''
        apps = {'app1': {'slots': [{}]}}
        self.set_test_snap_yaml("apps", apps)

        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'deny-installation': False
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration_apps()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_slots_deny_installation_true(self):
        '''Test check_declaration - slots/deny-installation/true'''
        slots = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'deny-installation': True
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_deny-installation:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'deny-installation'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_deny_installation_true_abbreviated(self):
        '''Test check_declaration - slots/deny-installation/true'''
        slots = {'iface-foo': 'foo'}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'deny-installation': True
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_deny-installation:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'deny-installation'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_deny_installation_false(self):
        '''Test check_declaration - slots/deny-installation/false'''
        slots = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'deny-installation': False
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_slots_allow_installation_false(self):
        '''Test check_declaration - slots/allow-installation/false'''
        slots = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'allow-installation': False
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_allow-installation:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'allow-installation'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_allow_installation_true(self):
        '''Test check_declaration - slots/allow-installation/true'''
        slots = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'allow-installation': True
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_plugs_deny_connection_true(self):
        '''Test check_declaration - plugs/deny-connection/true'''
        plugs = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-connection': True
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_deny-connection:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'deny-connection'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_deny_connection_false(self):
        '''Test check_declaration - plugs/deny-connection/false'''
        plugs = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-connection': False
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_plugs_allow_connection_false(self):
        '''Test check_declaration - plugs/allow-connection/false'''
        plugs = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'allow-connection': False
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_allow-connection:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'allow-connection'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_allow_connection_true(self):
        '''Test check_declaration - plugs/allow-connection/true'''
        plugs = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'allow-connection': True
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_slots_allow_installation_snap_type_app(self):
        '''Test check_declaration - slots/allow-installation/snap-type'''
        slots = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'allow-installation': {
                        'slot-snap-type': ['app']
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_slots_allow_installation_snap_type_bad(self):
        '''Test check_declaration - bad slots/allow-installation/snap-type'''
        slots = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'allow-installation': {
                        'slot-snap-type': ['kernel']
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_allow-installation:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'allow-installation/slot-snap-type'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_deny_installation_snap_type_app(self):
        '''Test check_declaration - plugs/deny-installation/snap-type'''
        plugs = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-installation': {
                        'plug-snap-type': ['app']
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_deny-installation:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'deny-installation/plug-snap-type'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_deny_installation_snap_type_bad(self):
        '''Test check_declaration - bad plugs/deny-installation/snap-type'''
        plugs = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-installation': {
                        'plug-snap-type': ['kernel']
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_z_check_declaration_plugs_deny_connection_attrib_str_match(self):
        '''Test check_declaration - plugs/deny-connection/attrib - str match'''
        plugs = {'iface-foo': {'interface': 'foo', 'attrib1': 'val1'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-connection': {
                        'plug-attributes': {
                            'attrib1': 'val1'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_deny-connection:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'deny-connection/plug-attributes'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_deny_connection_attrib_str_nomatch(self):
        '''Test check_declaration - plugs/deny-connection/attrib - str nomatch'''
        plugs = {'iface-foo': {'interface': 'foo', 'attrib1': 'val1'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-connection': {
                        'plug-attributes': {
                            'attrib1': 'other'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_plugs_allow_connection_attrib_str_match(self):
        '''Test check_declaration - plugs/allow-connection/attrib - str match'''
        plugs = {'iface-foo': {'interface': 'foo', 'attrib1': 'val1'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'allow-connection': {
                        'plug-attributes': {
                            'attrib1': 'val1'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_plugs_allow_connection_attrib_str_nomatch(self):
        '''Test check_declaration - plugs/allow-connection/attrib - str nomatch'''
        plugs = {'iface-foo': {'interface': 'foo', 'attrib1': 'val2'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'allow-connection': {
                        'plug-attributes': {
                            'attrib1': 'val1'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_allow-connection:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'allow-connection/plug-attributes'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_deny_connection_attrib_str2_match(self):
        '''Test check_declaration - plugs/deny-connection/attrib - strs match'''
        plugs = {'iface-foo': {'interface': 'foo',
                               'attrib1': 'val1',
                               'attrib2': 'val2'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-connection': {
                        'plug-attributes': {
                            'attrib1': 'val1',
                            'attrib2': 'val2'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_deny-connection:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'deny-connection/plug-attributes'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_deny_connection_attrib_str2_match2(self):
        '''Test check_declaration - plugs/deny-connection/attrib - strs match2'''
        plugs = {'iface-foo': {'interface': 'foo', 'attrib2': 'val2'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-connection': {
                        'plug-attributes': {
                            'attrib1': 'other',
                            'attrib2': 'val2'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_deny-connection:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'deny-connection/plug-attributes'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_deny_connection_attrib_str2_nomatch(self):
        '''Test check_declaration - plugs/deny-connection/attrib - strs nomatch'''
        plugs = {'iface-foo': {'interface': 'foo',
                               'attrib1': 'val1',
                               'attrib2': 'val2',
                               'attrib3': 'val3'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-connection': {
                        'plug-attributes': {
                            'attrib1': 'other',
                            'attrib2': 'other'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_plugs_allow_connection_attrib_str2_match(self):
        '''Test check_declaration - plugs/allow-connection/attrib - strs match'''
        plugs = {'iface-foo': {'interface': 'foo',
                               'attrib1': 'val1',
                               'attrib2': 'val2'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'allow-connection': {
                        'plug-attributes': {
                            'attrib1': 'val1',
                            'attrib2': 'val2'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_plugs_allow_connection_attrib_str2_match2(self):
        '''Test check_declaration - plugs/allow-connection/attrib - strs match2'''
        plugs = {'iface-foo': {'interface': 'foo', 'attrib2': 'val2'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'allow-connection': {
                        'plug-attributes': {
                            'attrib1': 'other',
                            'attrib2': 'val2'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_plugs_allow_connection_attrib_str2_nomatch(self):
        '''Test check_declaration - plugs/allow-connection/attrib - strs nomatch'''
        plugs = {'iface-foo': {'interface': 'foo',
                               'attrib1': 'val1',
                               'attrib2': 'val2',
                               'attrib3': 'val3'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'allow-connection': {
                        'plug-attributes': {
                            'attrib1': 'val1',
                            'attrib2': 'other'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_allow-connection:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'allow-connection/plug-attributes'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_deny_connection_attrib_list_match(self):
        '''Test check_declaration - slots/deny-connection/attrib - list match'''
        slots = {'iface-foo': {'interface': 'foo', 'attrib1': ['b', 'a']}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'deny-connection': {
                        'slot-attributes': {
                            'attrib1': ['a', 'b']
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_deny-connection:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'deny-connection/slot-attributes'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_deny_connection_attrib_list_nomatch(self):
        '''Test check_declaration - slots/deny-connection/attrib - list nomatch'''
        slots = {'iface-foo': {'interface': 'foo', 'attrib1': ['z', 'b']}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'deny-connection': {
                        'slot-attributes': {
                            'attrib1': ['a', 'b']
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_slots_allow_connection_attrib_list_match(self):
        '''Test check_declaration - slots/allow-connection/attrib - list match'''
        slots = {'iface-foo': {'interface': 'foo', 'attrib1': ['b', 'a']}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'allow-connection': {
                        'slot-attributes': {
                            'attrib1': ['a', 'b']
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_slots_allow_connection_attrib_list_nomatch(self):
        '''Test check_declaration - slots/allow-connection/attrib - list nomatch'''
        slots = {'iface-foo': {'interface': 'foo', 'attrib1': ['z', 'a']}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'slots': {
                'foo': {
                    'allow-connection': {
                        'slot-attributes': {
                            'attrib1': ['a', 'b']
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_allow-connection:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'allow-connection/slot-attributes'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_deny_connection_attrib_dict_match(self):
        '''Test check_declaration - plugs/deny-connection/attrib - dict match'''
        plugs = {'iface-foo': {'interface': 'foo', 'attrib1': {'c': 'd',
                                                               'a': 'b'}}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-connection': {
                        'plug-attributes': {
                            'attrib1': {'a': 'b', 'c': 'd'}
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_deny-connection:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'deny-connection/plug-attributes'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_deny_connection_attrib_dict_nomatch(self):
        '''Test check_declaration - plugs/deny-connection/attrib - dict nomatch'''
        plugs = {'iface-foo': {'interface': 'foo', 'attrib1': {'z': 'b',
                                                               'c': 'd'}}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-connection': {
                        'plug-attributes': {
                            'attrib1': {'a': 'b', 'c': 'd'}
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_plugs_allow_connection_attrib_dict_match(self):
        '''Test check_declaration - plugs/allow-connection/attrib - dict match'''
        plugs = {'iface-foo': {'interface': 'foo', 'attrib1': {'c': 'd',
                                                               'a': 'b'}}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'allow-connection': {
                        'plug-attributes': {
                            'attrib1': {'a': 'b', 'c': 'd'}
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_plugs_allow_connection_attrib_dict_nomatch(self):
        '''Test check_declaration - plugs/allow-connection/attrib - dict nomatch'''
        plugs = {'iface-foo': {'interface': 'foo', 'attrib1': {'z': 'b',
                                                               'c': 'd'}}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'allow-connection': {
                        'plug-attributes': {
                            'attrib1': {'a': 'b', 'c': 'd'}
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_allow-connection:iface-foo:foo'
        expected['error'][name] = {"text": "not allowed by 'allow-connection/plug-attributes'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_deny_connection_attrib_str_missing(self):
        '''Test check_declaration - plugs/deny-connection/attrib - str missing'''
        plugs = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'deny-connection': {
                        'plug-attributes': {
                            'attrib1': 'val1'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_plugs_allow_connection_attrib_str_missing(self):
        '''Test check_declaration - plugs/allow-connection/attrib - str missing'''
        plugs = {'iface-foo': {'interface': 'foo'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'allow-connection': {
                        'plug-attributes': {
                            'attrib1': 'val1'
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)
        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

    def test_check_declaration_plugs_bad_subsubkey_type(self):
        '''Test _verify_declaration - empty'''
        plugs = {'iface-foo': {'interface': 'foo', 'attrib1': None}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        base = {
            'plugs': {
                'foo': {
                    'allow-connection': {
                        'plug-attributes': {
                            'attrib1': None
                        }
                    }
                }
            }
        }
        self._set_base_declaration(c, base)

        try:
            c.check_declaration()
        except SnapDeclarationException:
            return
        raise Exception("base declaration should be invalid")

    def test_check_declaration_plugs_bluetooth_control(self):
        '''Test check_declaration - plugs bluetooth-control'''
        plugs = {'iface': {'interface': 'bluetooth-control'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs:iface:bluetooth-control'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_bluetooth_control_app(self):
        '''Test check_declaration - slots bluetooth-control - type: app'''
        slots = {'iface': {'interface': 'bluetooth-control'}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_allow-installation:iface:bluetooth-control'
        expected['error'][name] = {"text": "not allowed by 'allow-installation/slot-snap-type'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_bluetooth_control_core(self):
        '''Test check_declaration - slots bluetooth-control - type: core'''
        slots = {'iface': {'interface': 'bluetooth-control'}}
        self.set_test_snap_yaml("slots", slots)
        self.set_test_snap_yaml("type", "core")
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots:iface:bluetooth-control'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_docker_support(self):
        '''Test check_declaration - plugs docker-support'''
        plugs = {'iface': {'interface': 'docker-support'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_deny-connection:iface:docker-support'
        expected['error'][name] = {"text": "not allowed by 'deny-connection'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_docker_support(self):
        '''Test check_declaration - slots docker-support'''
        slots = {'iface': {'interface': 'docker-support'}}
        self.set_test_snap_yaml("slots", slots)
        self.set_test_snap_yaml("type", "core")
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_deny-connection:iface:docker-support'
        expected['error'][name] = {"text": "not allowed by 'deny-connection'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_home(self):
        '''Test check_declaration - plugs home'''
        plugs = {'iface': {'interface': 'home'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs:iface:home'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_home(self):
        '''Test check_declaration - slots home'''
        slots = {'iface': {'interface': 'home'}}
        self.set_test_snap_yaml("slots", slots)
        self.set_test_snap_yaml("type", "core")
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots:iface:home'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_content(self):
        '''Test check_declaration - plugs content'''
        plugs = {'iface': {'interface': 'content',
                           'target': 'foo',
                           'content': 'bar',
                           'default-provider': 'baz'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs:iface:content'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_content(self):
        '''Test check_declaration - slots content'''
        slots = {'iface': {'interface': 'content',
                           'read': 'foo',
                           'write': 'bar'}}
        self.set_test_snap_yaml("slots", slots)
        self.set_test_snap_yaml("type", "gadget")
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots:iface:content'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_browser_support(self):
        '''Test check_declaration - plugs browser-support'''
        plugs = {'iface': {'interface': 'browser-support'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs:iface:browser-support'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_browser_support_allow_sandbox_false(self):
        '''Test check_declaration - plugs browser-support - allow-sandbox: false'''
        plugs = {'iface': {'interface': 'browser-support',
                           'allow-sandbox': False}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs:iface:browser-support'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_browser_support_allow_sandbox_true(self):
        '''Test check_declaration - plugs browser-support - allow-sandbox: true'''
        plugs = {'iface': {'interface': 'browser-support',
                           'allow-sandbox': True}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs_deny-connection:iface:browser-support'
        expected['error'][name] = {"text": "not allowed by 'deny-connection/plug-attributes' in base declaration"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_browser_support(self):
        '''Test check_declaration - slots browser-support'''
        slots = {'iface': {'interface': 'browser-support'}}
        self.set_test_snap_yaml("slots", slots)
        self.set_test_snap_yaml("type", "core")
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots:iface:browser-support'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_network(self):
        '''Test check_declaration - plugs network'''
        plugs = {'iface': {'interface': 'network'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs:iface:network'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_network(self):
        '''Test check_declaration - slots network'''
        slots = {'iface': {'interface': 'network'}}
        self.set_test_snap_yaml("slots", slots)
        self.set_test_snap_yaml("type", "core")
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots:iface:network'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_bluez(self):
        '''Test check_declaration - plugs bluez'''
        plugs = {'iface': {'interface': 'bluez'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs:iface:bluez'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_bluez(self):
        '''Test check_declaration - slots bluez'''
        slots = {'iface': {'interface': 'bluez'}}
        self.set_test_snap_yaml("slots", slots)
        self.set_test_snap_yaml("type", "app")
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_deny-connection:iface:bluez'
        expected['error'][name] = {"text": "not allowed by 'deny-connection'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_docker(self):
        '''Test check_declaration - plugs docker'''
        plugs = {'iface': {'interface': 'docker'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs:iface:docker'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_docker(self):
        '''Test check_declaration - slots docker'''
        slots = {'iface': {'interface': 'docker'}}
        self.set_test_snap_yaml("slots", slots)
        self.set_test_snap_yaml("type", "gadget")
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 2}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_deny-connection:iface:docker'
        expected['error'][name] = {"text": "not allowed by 'deny-connection'"}
        name = 'declaration-snap-v2:slots_allow-installation:iface:docker'
        expected['error'][name] = {"text": "not allowed by 'allow-installation'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_mpris(self):
        '''Test check_declaration - plugs mpris'''
        plugs = {'iface': {'interface': 'mpris'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs:iface:mpris'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_mpris(self):
        '''Test check_declaration - slots mpris'''
        slots = {'iface': {'interface': 'mpris',
                           'name': 'foo'}}
        self.set_test_snap_yaml("slots", slots)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_deny-connection:iface:mpris'
        expected['error'][name] = {"text": "not allowed by 'deny-connection/slot-attributes'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_mir(self):
        '''Test check_declaration - plugs mir'''
        plugs = {'iface': {'interface': 'mir'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs:iface:mir'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_mir(self):
        '''Test check_declaration - slots mir'''
        slots = {'iface': {'interface': 'mir'}}
        self.set_test_snap_yaml("slots", slots)
        self.set_test_snap_yaml("type", "app")
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_deny-connection:iface:mir'
        expected['error'][name] = {"text": "not allowed by 'deny-connection'"}
        self.check_results(r, expected=expected)

    def test_check_declaration_plugs_serial_port(self):
        '''Test check_declaration - plugs serial-port'''
        plugs = {'iface': {'interface': 'serial-port'}}
        self.set_test_snap_yaml("plugs", plugs)
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 1, 'warn': 0, 'error': 0}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:plugs:iface:serial-port'
        expected['info'][name] = {"text": "OK"}
        self.check_results(r, expected=expected)

    def test_check_declaration_slots_serial_port(self):
        '''Test check_declaration - slots serial-port'''
        slots = {'iface': {'interface': 'serial-port'}}
        self.set_test_snap_yaml("slots", slots)
        self.set_test_snap_yaml("type", "gadget")
        c = SnapReviewDeclaration(self.test_name)
        self._use_test_base_declaration(c)

        c.check_declaration()
        r = c.click_report
        expected_counts = {'info': 0, 'warn': 0, 'error': 1}
        self.check_results(r, expected_counts)

        expected = dict()
        expected['error'] = dict()
        expected['warn'] = dict()
        expected['info'] = dict()
        name = 'declaration-snap-v2:slots_deny-connection:iface:serial-port'
        expected['error'][name] = {"text": "not allowed by 'deny-connection'"}
        self.check_results(r, expected=expected)