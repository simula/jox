################################################################################
#
# Copyright (c) 2016, EURECOM (www.eurecom.fr)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.
#
################################################################################
# file settings.py
# brief requited setting
# author  navid.nikaein@eurecom.fr

import os 

"""Juju simple orchstrator settings."""

# The base charm store API URL containing information about charms and bundles.
CHARMSTORE_API = 'https://api.jujucharms.com/charmstore/v4/'

# The URL of jujucharms.com, the home of Juju.
JUJUCHARMS_URL = 'https://jujucharms.com/'

# Retrieve the current juju-core home.
JUJU_HOME = os.getenv('JUJU_HOME', '~/.juju')

# The name of the Juju GUI charm.
JUJU_GUI_CHARM_NAME = 'juju-gui'


log_color = [{'level':' error',  'color': '\033[91m'}, # debug level 0
             {'level': 'warn' ,  'color': '\033[93m'},  # debug level 1
             {'level': 'notice', 'color': '\033[92m'},  # debug level 2
             {'level': 'info',   'color': '\033[0m'},   # debug level 3
             {'level': 'debug',  'color': '\033[0m'}]   # debug level 4




