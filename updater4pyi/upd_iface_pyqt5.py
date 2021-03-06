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

import datetime

from PyQt5 import Qt, QtCore, QtWidgets

from . import upd_core
from . import upd_iface
from .upd_log import logger


class UpdatePyQt5Interface(QtCore.QObject, upd_iface.UpdateGenericGuiInterface):

    def __init__(self, updater, parent=None, **kwargs):
        super(UpdatePyQt5Interface, self).__init__(parent=parent, updater=updater, **kwargs)
        # super doesn't propagate out of the Qt multiple inheritance...
        self.timer = None

    def get_settings_object(self):
        """
        Subclasses may reimplement this function to cusomize where the settings are stored.
        """
        settings = QtCore.QSettings()
        settings.beginGroup('updater4pyi')
        return settings

    def load_settings(self, keylist):
        settings = self.get_settings_object()
        d = {}
        for key in keylist:
            if settings.contains(key):
                d[key] = settings.value(key)

        logger.debug("load_settings: read settings: %r", d)
        return d

    def save_settings(self, d=None):
        if d is None:
            d = self.all_settings()

        logger.debug("save_settings: saving settings: %r", d)

        settings = self.get_settings_object()
        for k,v in d.iteritems():
            settings.setValue(k, QtCore.QVariant(v))

        # and save the settings to disk.
        settings.sync()

    def ask_first_time(self):
        msgBox = QtWidgets.QMessageBox(parent=None)
        msgBox.setWindowModality(QtCore.Qt.NonModal)
        msgBox.setText(unicode(self.tr("Would you like to regularly check for software updates%s?"))
                       %( ((unicode(self.tr(" for %s"))%self.progname)
                           if self.progname
                           else '') )
        )
        msgBox.addButton(msgBox.Yes)
        msgBox.addButton(msgBox.No)
        msgBox.setIcon(msgBox.Question)

        # show window as modeless window, so don't use exec_(). Instead, process application events
        # until the user has chosen some option.
        msgBox.show()
        msgBox.raise_()
        while (msgBox.isVisible()):
            Qt.QApplication.processEvents()

        # Yes, look for updates
        if (msgBox.clickedButton() == msgBox.button(msgBox.Yes)):
            return True

        # Anything else: no, go away
        return False

    def ask_to_update(self, rel_info):
        msgBox = QtWidgets.QMessageBox(parent=None)
        msgBox.setWindowModality(QtCore.Qt.NonModal)
        msgBox.setText(unicode(self.tr("A new software update is available (%sversion %s). "
                                       "Do you want to install it?"))
                       %(self.progname+' ' if self.progname else '', rel_info.get_version()))
        msgBox.setInformativeText(self.tr("Please make sure you save all your changes to your files "
                                          "before installing the update."))
        btnInstall = msgBox.addButton("Install", msgBox.AcceptRole)
        btnNotNow = msgBox.addButton("Not now", msgBox.RejectRole)
        btnDisableUpdates = msgBox.addButton("Disable Update Checks", msgBox.RejectRole)
        msgBox.setDefaultButton(btnInstall)
        msgBox.setEscapeButton(btnNotNow)
        msgBox.setIcon(msgBox.Question)

        # show window as modeless window, so don't use exec_(). Instead, process application events
        # until the user has chosen some option.
        msgBox.show()
        msgBox.raise_()
        while (msgBox.isVisible()):
            Qt.QApplication.processEvents()

        clickedbutton = msgBox.clickedButton()

        # btnInstall: install update
        if (clickedbutton == btnInstall):
            return True

        # btnNotNow, btnDisableUpdates: don't check for updates
        if (clickedbutton == btnDisableUpdates):
            self.setCheckForUpdatesEnabled(False)

        return False

    def ask_to_restart(self):
        msgBox = QtWidgets.QMessageBox(parent=None)
        #msgBox.setWindowModality(Qt.NonModal)
        msgBox.setText(self.tr("The software update is now complete."))

        thisprog = str(self.tr("This program"))
        if (self.progname):
            thisprog = str('<b>'+self.progname+'</b>');
        msgBox.setInformativeText(str(self.tr("%s needs to be restarted for the changes "
                                              "to take effect. Restart now?")) % (thisprog))
        btnRestart = msgBox.addButton("Restart", msgBox.AcceptRole)
        btnIgnore = msgBox.addButton("Ignore", msgBox.RejectRole)

        msgBox.setDefaultButton(btnRestart)
        msgBox.setEscapeButton(btnIgnore)
        msgBox.setIcon(msgBox.Information)
        msgBox.show()
        msgBox.raise_()
        msgBox.exec_();

        clickedbutton = msgBox.clickedButton()

        if (clickedbutton == btnRestart):
            return True

        return False

    def set_timeout_check(self, interval_timedelta):

        # interval in milliseconds
        interval_ms = int(interval_timedelta.total_seconds()*1000)

        if self.timer is None:
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.check_for_updates)
            self.timer.setSingleShot(True)
        elif self.timer.isActive():
            self.timer.stop()

        self.timer.setInterval(interval_ms)
        self.timer.start()
        logger.debug("single-shot timer started with interval=%d ms", interval_ms)

    # ------------------------------------------------------------------------------

    # add proper signal and slot interface / decorations to these settings
    # also, don't use timedelta, unknown to Qt5, but rather milliseconds (and the rename slot accordingly)

    initCheckDelayMsChanged = Qt.pyqtSignal([int])

    def initCheckDelayMs(self):
        return int(self.initCheckDelay().total_seconds()*1000)

    @Qt.pyqtSlot(int)
    def setInitCheckDelayMs(self, init_check_delay_ms, save=True):
        self.setInitCheckDelay(
            datetime.timedelta(days=0, microseconds=init_check_delay_ms*1000),
            save=save
            )

    def setInitCheckDelay(self, init_check_delay_td, save=True):
        if (self._timedelta_equal(init_check_delay_td, self.initCheckDelay())):
            # no change (up to small error)
            return

        super(UpdatePyQt5Interface, self).setInitCheckDelay(init_check_delay_td, save=save)
        self.initCheckDelayMsChanged.emit(int(init_check_delay_td.total_seconds()*1000))

    checkForUpdatesEnabledChanged = Qt.pyqtSignal([bool])

    @Qt.pyqtSlot(bool)
    def setCheckForUpdatesEnabled(self, enabled, save=True):
        if (enabled == self.checkForUpdatesEnabled()):
            # no change
            return

        super(UpdatePyQt5Interface, self).setCheckForUpdatesEnabled(enabled, save=save)
        self.checkForUpdatesEnabledChanged.emit(enabled)

    checkIntervalMsChanged = Qt.pyqtSignal([int])

    def checkIntervalMs(self):
        return int(self.checkInterval().total_seconds()*1000)

    @Qt.pyqtSlot(int)
    def setCheckIntervalMs(self, check_interval_ms, save=True):
        self.setCheckInterval(
            datetime.timedelta(days=0, microseconds=check_interval_ms*1000),
            save=save
            )

    def setCheckInterval(self, check_interval_td, save=True):
        if (self._timedelta_equal(check_interval_td, self.checkInterval())):
            # no change (up to small error)
            return

        super(UpdatePyQt5Interface, self).setCheckInterval(check_interval_td, save)
        self.checkIntervalMsChanged.emit(int(check_interval_td.total_seconds()*1000))

    def _timedelta_equal(self, a, b):
        return abs( (a-b).total_seconds() ) < 1.0;
