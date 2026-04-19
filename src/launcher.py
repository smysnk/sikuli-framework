"""
Application launcher helpers for the SikuliGO runtime.
"""

from __future__ import annotations

import os as osLib
import platform
import subprocess

from entity import Application
from wrapper import Env


class Launcher(object):
    logger = None

    @classmethod
    def setLogger(cls, logger):
        cls.logger = logger(cls)

    @classmethod
    def run(cls, className):
        """Launch an application through reflection."""

        cls.logger.info("is attempting to run [%s] wd=%s" % (className, osLib.getcwd()))

        for appCls in Application.__subclasses__():
            if className != appCls.__name__:
                continue

            os_name = Env.getOS()
            os_version = Env.getOSVersion(fullName=True)
            arch = platform.machine().lower()

            app = appCls()
            binary = app.getBinary(os_name, os_version, arch)
            working_dir = app.getWorkingDir(os_name, os_version, arch)
            cls.logger.info(
                'created [%s] from [%s] [%s %s %s]'
                % (className, binary, os_name, os_version, arch)
            )

            subprocess.Popen(
                binary,
                shell=isinstance(binary, str),
                cwd=working_dir,
            )
            return app

        raise Exception(
            "Unable to find Application sub-class [%s], ensure that it is included"
            % className
        )

    @classmethod
    def formatPrefix(cls, *args, **kwargs):
        return "[Launcher] "
