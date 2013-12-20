# -*- coding: utf-8 -*-
#######################################################################################
#                                                                                     #
#   This file is part of the updater4pyi Project.                                     #
#                                                                                     #
#   Copyright (C) 2013, Philippe Faist                                                #
#   philippe.faist@bluewin.ch                                                         #
#   All rights reserved.                                                              #
#                                                                                     #
#   Redistribution and use in source and binary forms, with or without                #
#   modification, are permitted provided that the following conditions are met:       #
#                                                                                     #
#   1. Redistributions of source code must retain the above copyright notice, this    #
#      list of conditions and the following disclaimer.                               #
#   2. Redistributions in binary form must reproduce the above copyright notice,      #
#      this list of conditions and the following disclaimer in the documentation      #
#      and/or other materials provided with the distribution.                         #
#                                                                                     #
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND   #
#   ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED     #
#   WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE            #
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR   #
#   ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES    #
#   (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;      #
#   LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND       #
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT        #
#   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS     #
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                      #
#                                                                                     #
#######################################################################################

import re

import upd_core
from upd_source import UpdateInfo, UpdateSource



class UpdateInterface(object):
    def __init__(self, *args, **pwargs):
        pass

    def start(self, update_source):
        """
        Start being aware of wanting to check for updates. It is up to the interface
        to decide when to check for updates, how often, etc. For example, a console
        interface would check right away, while a GUI might first load the application,
        and set a timer to check later, so that startup is not slowed down by the update
        check.
        """
        raise NotImplementedError
    







class UpdateConsoleInterface(UpdateInterface):
    def __init__(self, *args, **pwargs):
        super(UpdateConsoleInteface, self).__init__(self, *args, **kwargs)

    def start(self, update_source):

        #
        # Check for updates.
        # 
        upd_info = update_source.check_for_updates()

        if (upd_info is None):
            # no updates.
            print "No updates available."
            return

        #
        # There's an update, prompt the user.
        #
        print ""
        print "-----------------------------------------------------------"
        print ""
        print "A new software update is available (version %s)" %(upd_info.version)
        print ""

        yn = raw_input("Do you want to install it? (y/n)")

        if (re.match(r'\s*y(es)?\s*', yn, re.IGNORECASE)):
            #
            # yes, install update
            #
            upd_core.install_update(upd_info)
            #
            # update installed.
            #
            print ""
            print "Update installed. Please restart the program."
            print ""
            print "-----------------------------------------------------------"
            print ""
        else:
            print ""
            print "Not installing update."
            print ""
            print "-----------------------------------------------------------"
            print ""

        # return to the main program.
        return
        



